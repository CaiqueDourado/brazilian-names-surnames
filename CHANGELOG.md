# Changelog

All notable changes to this dataset are documented here. Versions follow [Semantic Versioning](https://semver.org/): a new major version renames or removes columns.

## [1.0.0] - 2026-10-21

### Added
- 46,840 given names (18 columns) and 27,047 surnames (11 columns), in CSV and Parquet.
- Model named on every text (`text-davinci-002` or `gpt-3.5`); source of every name (`cnpj`, `search`, `ibge_variant`).
- Data dictionary in English and Portuguese, methodology, data quality report, cover images.
- `scripts/build.py`, `scripts/validate.py`, `scripts/docs.py`, `scripts/make_figures.py`; validation in GitHub Actions.
- Kaggle metadata (`data/dataset-metadata.json`) and exploratory notebook.

### Removed (relative to the 2023 database)
- Rows without a text, model refusals, texts in English, company words and codes; surnames with fewer than 3 partners. Counts in `stats.json`.
