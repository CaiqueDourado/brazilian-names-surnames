# Changelog

All notable changes to this dataset are documented here. Versions follow [Semantic Versioning](https://semver.org/): a new major version renames or removes columns.

## [1.1.0] - 2026-10-22

### Added
- 13 columns in `nomes`: women, men, share of women, decade with most births and people born per decade (before 1930 to the 2000s), from the v2 endpoint of IBGE's names API, fetched with [ibge-nomes](https://github.com/CaiqueDourado/ibge-nomes) (`scripts/fetch_ibge.py`, answers summarised in `raw/ibge_v2.csv`). 17,200 of the 24,751 names with an IBGE rank have them.
- README: process flowchart, the story and technique of nomessobrenomes.com, the IBGE names API explained with sample calls.

## [1.0.0] - 2026-10-21

### Added
- 46,840 given names (18 columns) and 27,047 surnames (11 columns), in CSV and Parquet.
- Model named on every text (`text-davinci-002` or `gpt-3.5`); source of every name (`cnpj`, `search`, `ibge_variant`).
- Data dictionary in English and Portuguese, methodology, data quality report, cover images.
- `scripts/build.py`, `scripts/validate.py`, `scripts/docs.py`, `scripts/make_figures.py`; validation in GitHub Actions.
- Kaggle metadata (`data/dataset-metadata.json`) and exploratory notebook.

### Removed (relative to the 2023 database)
- Rows without a text, model refusals, texts in English, company words and codes; surnames with fewer than 3 partners. Counts in `stats.json`.
