"""One given name as nested JSON (docs/example-name.json): its row in nomes, grouped, plus what joins to it.

    python scripts/make_json.py

Groups the columns of data/nomes.parquet (IBGE 2010 Census counts by sex and decade of birth, the six matching
keys), lists the other names with the same Portuguese Metaphone key and adds the surname with the same
fingerprint from data/sobrenomes.parquet. Keys inside a group are the column names without the group
prefix (ibge_born_1950s -> ibge_2010.born["1950s"]). Only pandas and pyarrow are needed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAME = "Iracema"
DECADES = ("before_1930", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s")
KEYS = ("metaphone", "fingerprint", "tokens", "tokens_fingerprint", "ngram", "soft")


def plain(v):
    """pandas scalar -> JSON value (NA -> None, numpy numbers -> int/float)."""
    if pd.isna(v):
        return None
    if hasattr(v, "item"):
        return v.item()
    return v


def build() -> dict:
    names = pd.read_parquet(ROOT / "data" / "nomes.parquet")
    surnames = pd.read_parquet(ROOT / "data" / "sobrenomes.parquet")
    r = {k: plain(v) for k, v in names[names.name == NAME].iloc[0].items()}

    same = names[(names.key_metaphone == r["key_metaphone"]) & (names.name != NAME)]
    same = same.sort_values(["ibge_frequency", "name"], ascending=[False, True], na_position="last")
    sur = surnames[surnames.key_fingerprint == r["key_fingerprint"]].sort_values("surname_id")

    return {
        "name_id": r["name_id"],
        "name": r["name"],
        "source": r["source"],
        "cnpj_partners": r["cnpj_partners"],
        "ibge_2010": {
            "rank": r["ibge_rank"],
            "frequency": r["ibge_frequency"],
            "percent": r["ibge_percent"],
            "top_state": {"state": r["ibge_top_state"], "per_100k": r["ibge_top_state_per_100k"]},
            "spellings": r["ibge_spellings"].split("|") if r["ibge_spellings"] else [],
            "sex": {"female": r["ibge_female"], "male": r["ibge_male"], "share_female": r["ibge_share_female"]},
            "peak_decade": r["ibge_peak_decade"],
            "born": {d: r[f"ibge_born_{d}"] for d in DECADES},
        },
        "meaning": r["meaning"],
        "model": r["model"],
        "keys": {k: r[f"key_{k}"] for k in KEYS},
        "same_metaphone": [{"name": n, "ibge_frequency": plain(f), "cnpj_partners": plain(c)}
                           for n, f, c in same[["name", "ibge_frequency", "cnpj_partners"]].itertuples(index=False)],
        "as_surname": [{k: plain(v) for k, v in row.items() if not k.startswith("key_")}
                       for row in sur.to_dict("records")],
    }


def main() -> None:
    out = ROOT / "docs" / "example-name.json"
    out.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
