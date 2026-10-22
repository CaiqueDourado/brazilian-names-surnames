"""Validate data/nomes.* and data/sobrenomes.*. Exits with code 1 and lists every failure.

    python scripts/validate.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
failures: list[str] = []
NAME = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ' -]*[A-Za-zÀ-ÖØ-öø-ÿ]$")
REFUSAL = ["não há um significado específico", "infelizmente", "modelo de linguagem", "como uma ia", "não é um nome"]


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def table(stem: str, key: str, name: str, text: str, expected: int) -> pd.DataFrame:
    csv = pd.read_csv(ROOT / "data" / f"{stem}.csv", dtype=str, keep_default_na=False)
    df = pd.read_parquet(ROOT / "data" / f"{stem}.parquet")
    check(len(df) == expected, f"{stem}: expected {expected} rows (stats.json), got {len(df)}")
    check(len(csv) == len(df), f"{stem}: CSV and Parquet have different row counts")
    check(list(csv.columns) == list(df.columns), f"{stem}: CSV and Parquet have different columns")
    check(df[key].is_unique, f"{stem}: {key} is not unique")
    folded = df[name].str.normalize("NFD").str.replace(r"[̀-ͯ]", "", regex=True).str.lower()
    check(folded.is_unique, f"{stem}: names that differ only in accents: {folded[folded.duplicated()].head().tolist()}")
    bad = df.loc[~df[name].str.match(NAME), name].head().tolist()
    check(not bad, f"{stem}: names with other characters: {bad}")
    check(df[text].notna().all() and (df[text].str.len() >= 20).all(), f"{stem}: every row needs a text of 20+ characters")
    check(not df[text].str.match(r"^\s").any(), f"{stem}: texts with leading spaces")
    low = df[text].str.lower()
    for pattern in REFUSAL:
        check(not low.str.contains(pattern, regex=False).any(), f"{stem}: refusal left in the text: {pattern!r}")
    check(set(df["model"]) <= {"text-davinci-002", "gpt-3.5"}, f"{stem}: unexpected models {set(df['model'])}")
    return df


def main() -> int:
    stats = json.loads((ROOT / "stats.json").read_text(encoding="utf-8"))
    names = table("nomes", "name_id", "name", "meaning", stats["names"]["rows_published"])
    surnames = table("sobrenomes", "surname_id", "surname", "history", stats["surnames"]["rows_published"])

    check(set(names["source"]) <= {"cnpj", "search", "ibge_variant"}, f"nomes: unexpected source {set(names['source'])}")
    cnpj = names["source"] == "cnpj"
    check(names.loc[cnpj, "cnpj_partners"].ge(3).all(), "nomes: cnpj rows need 3+ partners")
    check(names.loc[~cnpj, "cnpj_partners"].isna().all(), "nomes: only cnpj rows have a partner count")
    check(surnames["cnpj_partners"].ge(3).all(), "sobrenomes: every surname needs 3+ partners")
    check(names["ibge_rank"].dropna().ge(1).all(), "nomes: ibge_rank below 1")
    check(names["ibge_percent"].dropna().between(0, 100).all(), "nomes: ibge_percent outside 0-100")
    states = set(json.loads((ROOT / "schema" / "states.json").read_text(encoding="utf-8")))
    bad = sorted(set(names["ibge_top_state"].dropna()) - states)
    check(not bad, f"nomes: unknown states {bad}")
    check(not names["ibge_spellings"].dropna().str.contains(",").any(), "nomes: ibge_spellings must use | as separator")
    if "ibge_female" in names.columns:  # sex and decade columns from raw/ibge_v2.csv
        check(names["ibge_share_female"].dropna().between(0, 1).all(), "nomes: ibge_share_female outside 0-1")
        decades = ["before_1930", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s"]
        check(set(names["ibge_peak_decade"].dropna()) <= set(decades), "nomes: unexpected ibge_peak_decade")
        born = names[[f"ibge_born_{d}" for d in decades]]
        has = names["ibge_female"].notna() & names["ibge_male"].notna() & born.notna().all(axis=1)
        sexes = names.loc[has, "ibge_female"] + names.loc[has, "ibge_male"]
        total = born[has].sum(axis=1)
        off = ((sexes - total).abs() > total * 0.05 + 20).sum()
        check(off <= len(total) * 0.05, f"nomes: women + men far from the decade total in {off} names")
        check(names.loc[~names["ibge_rank"].notna(), "ibge_female"].isna().all(), "nomes: sex data for a name without IBGE rank")
    for df, stem in ((names, "nomes"), (surnames, "sobrenomes")):
        check(df["key_metaphone"].notna().mean() > 0.99, f"{stem}: key_metaphone mostly empty")

    if failures:
        print(f"{len(failures)} check(s) failed:")
        for message in failures:
            print(" -", message)
        return 1
    print(f"OK: {len(names)} names, {len(surnames)} surnames")
    return 0


if __name__ == "__main__":
    sys.exit(main())
