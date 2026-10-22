"""Fetch sex and decade of birth for every name from IBGE's names API (2010 Census).

    pip install "ibge-nomes @ git+https://github.com/CaiqueDourado/ibge-nomes"   (+ truststore on Windows)
    python scripts/fetch_ibge.py                 # about 3,700 calls, ~15 min; resumable

Asks the v2 endpoint three times per batch of 20 names (all, women, men) for the names that have
IBGE data (`ibge_rank` filled; compound names never have it) and writes raw/ibge_v2.csv, which is
committed so scripts/build.py stays reproducible without network. Raw answers are kept in
work/ibge_cache/ (not committed): stopping and running again costs no calls.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "raw" / "ibge_v2.csv"
CACHE = ROOT / "work" / "ibge_cache"

try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

try:
    from ibge_nomes import IbgeNomes
    from ibge_nomes.cli import enrich
except ImportError:
    sys.exit('Install the client first: pip install "ibge-nomes @ git+https://github.com/CaiqueDourado/ibge-nomes"')


def main() -> None:
    client = IbgeNomes(cache=CACHE)
    sample = client.by_decade(["maria"])
    women = client.by_decade(["maria"], sex="F")
    if len(sample.get("MARIA", {})) < 8 or not women.get("MARIA"):
        print("The API answered in an unexpected format. Send this output:")
        print(client.get_text("/v2/censos/nomes/maria"))
        print(client.get_text("/v2/censos/nomes/maria", {"sexo": "F"}))
        sys.exit(1)
    print("API ok:", sample["MARIA"])

    names = pd.read_parquet(ROOT / "data" / "nomes.parquet")
    todo = names.loc[names["ibge_rank"].notna(), ["name"]]
    OUT.parent.mkdir(exist_ok=True)
    source = ROOT / "work" / "ibge_names.csv"
    source.parent.mkdir(exist_ok=True)
    todo.to_csv(source, index=False)
    enrich(client, source, "name", OUT)
    print(f"done: {OUT} ({client.calls:,} calls). Run scripts/build.py next.")


if __name__ == "__main__":
    main()
