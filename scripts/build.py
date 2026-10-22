"""Build data/nomes.* and data/sobrenomes.* from the SQL Server export.

    python scripts/build.py --raw D:\\nomes_raw          # folder written by exportar_nomes.py

The export (nomes.parquet, sobrenomes.parquet) is a faithful copy of the 2023 database behind
nomessobrenomes.com and is not redistributed. Every step below is documented in
docs/methodology.md and docs/data-quality.md; stats.json counts what each step removed.

Scope (decided with the author):
  * only names and surnames that have a generated text, as on the site;
  * texts the model refused to write, or wrote in English, are not published, and the row goes too;
  * surnames need 3 or more partners in the CNPJ register, the same cut the names already had.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"
MIN_PARTNERS = 3
# Names inserted from the IBGE spelling lists start at this id; their "ocorrencias" counts how many
# names list them as a spelling, not CNPJ partners (see docs/methodology.md).
FIRST_IBGE_VARIANT_ID = 379_876

# Refusals and model talk. Taken from the cleaning queries the site used in 2023
# (significado_dos_nomes_pega_dados_api_open_ai_chat.sql and the runbook), lower-cased.
# Two over-broad site rules were left out: bare "linguagem" (hits "na linguagem tupi") and " consigo ".
REFUSAL = [
    "ia de linguagem", "como uma ia", "sou um assistente", "assistente virtual", "como assistente", "linguagem natural", "modelo de linguagem",
    "como inteligência artificial", "language model", "inteligência artificial", "modelo linguistico",
    "não foi possível", "pode ser um nome raro ou inventado", "seja um nome inventado",
    "ou uma variação de outro nome", "não há informações", "não consegui encontrar",
    "sinto muito", "não há um significado oficial", "pode ser um nome raro ou incomum",
    "pode ser um nome inventado", "um nome raro ou inventado", "não há registro de um significado",
    "não é possível encontrar", "não encontrei", "não há significado registrado", "não consegui ",
    "sem mais informações", "não é possível fornecer", "não tenho informaç", "não posso",
    "não é apropriado", "lamento", "infelizmente", "desculp", "não sei",
    "não há um significado específico", "não é um nome", "não há registros", "não fui programad",
    "there is no one definitive answer", "não tem um significado específico", "não tem significado conhecido",
]
# A text that opens by saying there is no known meaning or history is a refusal too, even when the
# model goes on to guess ("Não há um significado claro para o nome X. É possível que seja...").
OPENS_WITH_NO_ANSWER = re.compile(
    r"^(não (há|existe|existem|foi encontrad|se sabe|se conhece|tem um significado|possui)"
    r"|o significado do nome \S+ (é desconhecido|não é conhecido))", re.I)
AI_WORD = re.compile(r"\b(IA|AI)\b")  # upper case only, as in the site's rule
ENGLISH = {"the", "and", "of", "was", "is", "in", "to", "family", "name", "meaning", "back", "which", "were"}
ENGLISH_SHARE = 0.15
NAME_OK = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ' -]*[A-Za-zÀ-ÖØ-öø-ÿ]$")
LOWER_WORDS = {"de", "da", "do", "das", "dos", "e"}
SENTENCE = re.compile(r"(?<=[.!?])\s+")
# Spellings the CNPJ export got wrong, among the most frequent names (docs/data-quality.md).
NAME_FIXES = {"António": "Antônio", "Joâo": "João", "Claúdia": "Cláudia", "Diêgo": "Diego"}
# Words of company names that the surname split took for surnames ("Brasil" is a real surname and stays).
BUSINESS_WORDS = {
    "limitada", "ltda", "eireli", "holding", "participacoes", "comercio", "servicos", "combustiveis",
    "industria", "construtora", "transportes", "imoveis", "sociedade", "representacoes", "agropecuaria",
    "empreendimentos", "administracao", "consultoria", "engenharia", "investimentos", "distribuidora",
    "anonima", "espana", "importacao", "exportacao", "incorporadora", "comercial", "industrial",
}


def fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


def accents(text: str) -> int:
    return sum(1 for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) == "Mn")


def clean_text(text: str | None) -> tuple[str | None, int]:
    """Trim, normalise spaces, drop a sentence that repeats an earlier one. Returns (text, sentences dropped)."""
    if not isinstance(text, str):
        return None, 0
    paragraphs = [re.sub(r"[ \t\r\f\v]+", " ", p).strip() for p in text.replace("\r", "").split("\n")]
    seen, out, dropped = set(), [], 0
    for paragraph in paragraphs:
        if not paragraph:
            continue
        kept = []
        for sentence in SENTENCE.split(paragraph):
            key = sentence.strip().lower()
            if len(key) > 15 and key in seen:
                dropped += 1
                continue
            seen.add(key)
            kept.append(sentence)
        if kept:
            out.append(" ".join(kept))
    return ("\n".join(out) or None), dropped


def text_problem(text: str | None) -> str | None:
    if not isinstance(text, str):
        return "no_text"
    low = text.lower()
    if len(text) < 20 or any(p in low for p in REFUSAL) or AI_WORD.search(text) or OPENS_WITH_NO_ANSWER.match(text):
        return "refusal"
    words = re.findall(r"[a-zà-ÿ]+", low)
    if words and sum(w in ENGLISH for w in words) / len(words) > ENGLISH_SHARE:
        return "english"
    return None


def title_case(name: str) -> str:
    if name != name.upper():
        return name
    parts = name.lower().split(" ")
    return " ".join(p if (i and p in LOWER_WORDS) else "-".join(s[:1].upper() + s[1:] for s in p.split("-"))
                    for i, p in enumerate(parts))


def ibge_number(value):
    if not isinstance(value, str) or value == "":
        return None
    return float(str(value).replace(",", "."))


def prepare(raw: pd.DataFrame, name_col: str, text_col: str, chat_col: str, stats: dict) -> pd.DataFrame:
    """Steps shared by names and surnames. Returns the rows kept, with the text and model columns."""
    df = raw.copy()
    chat = df[chat_col].notna()
    df["model"] = None
    df.loc[df[text_col].notna(), "model"] = "text-davinci-002"
    df.loc[chat, "model"] = "gpt-3.5"
    df["raw_text"] = df[chat_col].where(chat, df[text_col])
    cleaned = df["raw_text"].map(clean_text)
    df["text"] = cleaned.map(lambda t: t[0])
    stats["sentences_repeated_removed"] = int(cleaned.map(lambda t: t[1]).sum())
    stats["texts_with_repetition_fixed"] = int((cleaned.map(lambda t: t[1]) > 0).sum())
    df["problem"] = df["text"].map(text_problem)
    df.loc[df["problem"].isna() & ~df[name_col].fillna("").str.match(NAME_OK), "problem"] = "not_a_name"
    business = df[name_col].fillna("").map(lambda v: fold(v.strip()) in BUSINESS_WORDS)
    df.loc[df["problem"].isna() & business, "problem"] = "company_word"
    stats["rows_exported"] = len(df)
    stats["removed"] = {k: int(v) for k, v in df["problem"].value_counts().sort_index().items()}
    df = df[df["problem"].isna()].copy()
    df[name_col] = df[name_col].str.strip().map(title_case)
    fixed = df[name_col].isin(NAME_FIXES)
    stats["spellings_fixed"] = int(fixed.sum())
    df.loc[fixed, name_col] = df.loc[fixed, name_col].map(NAME_FIXES)
    return df


def merge_accent_variants(df: pd.DataFrame, name_col: str, count_col: str, stats: dict) -> pd.DataFrame:
    """Rows that differ only in accents ("Antônio", "António") become one: the spelling with more
    accents wins (ties: lowest id); the partner count is the largest of the group."""
    df["_key"] = df[name_col].map(fold)
    df["_acc"] = df[name_col].map(accents)
    df = df.sort_values(["_key", "_acc", "id"], ascending=[True, False, True])
    counts = df.groupby("_key")[count_col].max()
    groups = df.groupby("_key").size()
    stats["accent_variants_merged"] = int((groups[groups > 1] - 1).sum())
    df = df.drop_duplicates("_key", keep="first").copy()
    df[count_col] = df["_key"].map(counts)
    return df.drop(columns=["_key", "_acc"])


KEYS = ["metaphone", "fingerprint", "tokenizada", "tokenizada_fingerprint", "ngram", "soft"]
KEY_NAMES = {"metaphone": "key_metaphone", "fingerprint": "key_fingerprint", "tokenizada": "key_tokens",
             "tokenizada_fingerprint": "key_tokens_fingerprint", "ngram": "key_ngram", "soft": "key_soft"}


def build_names(raw: pd.DataFrame, stats: dict) -> pd.DataFrame:
    df = prepare(raw, "nome", "significado", "significado_chatGPT", stats)
    df["source"] = "cnpj"
    df.loc[df["ocorrencias"] == -1, "source"] = "search"
    df.loc[(df["id"] >= FIRST_IBGE_VARIANT_ID) & (df["ocorrencias"] > 0), "source"] = "ibge_variant"
    df["cnpj_partners"] = df["ocorrencias"].where(df["source"] == "cnpj")
    df = merge_accent_variants(df, "nome", "cnpj_partners", stats)
    df.loc[df["cnpj_partners"].notna(), "source"] = "cnpj"
    out = pd.DataFrame({
        "name_id": df["id"],
        "name": df["nome"],
        "meaning": df["text"],
        "model": df["model"],
        "source": df["source"],
        "cnpj_partners": df["cnpj_partners"],
        "ibge_rank": df["ibge_rank"].map(ibge_number),
        "ibge_frequency": df["ibge_freq"].map(ibge_number),
        "ibge_percent": df["ibge_percentual"].map(ibge_number),
        "ibge_top_state": df["ibge_ufMax"].replace("", None),
        "ibge_top_state_per_100k": df["ibge_ufMaxProp"].map(ibge_number),
        "ibge_spellings": df["ibge_nomes"].replace("", None).map(lambda v: v.replace(",", "|") if isinstance(v, str) else None),
        **{KEY_NAMES[k]: df[k].replace("", None) for k in KEYS},
    })
    for col in ("name_id", "cnpj_partners", "ibge_rank", "ibge_frequency"):
        out[col] = out[col].astype("Int64")
    out = add_sex_and_decades(out, stats)
    return out.sort_values("name_id").reset_index(drop=True)


DECADES = ["before_1930", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s"]
IBGE_V2 = ROOT / "raw" / "ibge_v2.csv"


def add_sex_and_decades(out: pd.DataFrame, stats: dict) -> pd.DataFrame:
    """Columns from IBGE's v2 endpoint (raw/ibge_v2.csv, written by scripts/fetch_ibge.py), placed
    after the other ibge_* columns. Missing file = the 2023 columns only."""
    if not IBGE_V2.exists():
        return out
    v2 = pd.read_csv(IBGE_V2, dtype={"name": str}).drop_duplicates("name").set_index("name")
    new = pd.DataFrame(index=out.index)
    new["ibge_female"] = out["name"].map(v2["female"]).astype("Int64")
    new["ibge_male"] = out["name"].map(v2["male"]).astype("Int64")
    new["ibge_share_female"] = out["name"].map(v2["share_female"]).astype("float64")
    new["ibge_peak_decade"] = out["name"].map(v2["peak_decade"]).astype("string").replace({pd.NA: None})
    for decade in DECADES:
        new[f"ibge_born_{decade}"] = out["name"].map(v2[f"born_{decade}"]).astype("Int64")
    stats["ibge_v2_names"] = int(new[["ibge_female", "ibge_male"]].notna().any(axis=1).sum())
    at = list(out.columns).index("ibge_spellings") + 1
    return pd.concat([out.iloc[:, :at], new, out.iloc[:, at:]], axis=1)


def build_surnames(raw: pd.DataFrame, stats: dict) -> pd.DataFrame:
    below = raw["ocorrencias"] < MIN_PARTNERS
    has_text = raw["historia"].notna() | raw["historia_chatGPT"].notna()
    stats["below_partner_cut_with_text"] = int((below & has_text).sum())
    df = prepare(raw[~below], "sobrenome", "historia", "historia_chatGPT", stats)
    df = merge_accent_variants(df, "sobrenome", "ocorrencias", stats)
    out = pd.DataFrame({
        "surname_id": df["id"],
        "surname": df["sobrenome"],
        "history": df["text"],
        "model": df["model"],
        "cnpj_partners": df["ocorrencias"],
        **{KEY_NAMES[k]: df[k].replace("", None) for k in KEYS},
    })
    for col in ("surname_id", "cnpj_partners"):
        out[col] = out[col].astype("Int64")
    return out.sort_values("surname_id").reset_index(drop=True)


def write(df: pd.DataFrame, stem: str) -> None:
    df.to_parquet(OUT / f"{stem}.parquet", index=False, compression="zstd")
    df.to_csv(OUT / f"{stem}.csv", index=False, encoding="utf-8", lineterminator="\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, type=Path)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    stats = {"names": {}, "surnames": {}}
    names = build_names(pd.read_parquet(args.raw / "nomes.parquet"), stats["names"])
    surnames = build_surnames(pd.read_parquet(args.raw / "sobrenomes.parquet"), stats["surnames"])
    write(names, "nomes")
    write(surnames, "sobrenomes")
    for key, df in (("names", names), ("surnames", surnames)):
        stats[key]["rows_published"] = len(df)
        stats[key]["by_model"] = {k: int(v) for k, v in df["model"].value_counts().sort_index().items()}
    stats["names"]["by_source"] = {k: int(v) for k, v in names["source"].value_counts().sort_index().items()}
    (ROOT / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
