**Nomes e sobrenomes do Brasil**: 47 mil nomes e 27 mil sobrenomes com frequência no cadastro CNPJ, dados do Censo 2010 do IBGE e significados escritos por GPT. **Brazilian given names and surnames** with CNPJ counts, IBGE 2010 Census data and meanings written by OpenAI models in 2023.

This is the database behind nomessobrenomes.com, a 90,000-page static site built by the author in 2023. It works two ways:

- **A list of Brazilian names with real frequencies**: how many company partners in the CNPJ register share each name or surname, plus IBGE Census rank, frequency, the state where the name is most common, the related spellings IBGE lists for it, how many women and men carry it and in which decade they were born. The README explains the IBGE names API, with sample calls; the data was fetched with the open-source client [ibge-nomes](https://github.com/CaiqueDourado/ibge-nomes).
- **A corpus of language-model output about names**: every row carries a meaning (names) or family history (surnames) written by text-davinci-002 or gpt-3.5, with the model named. Nobody reviewed them. Many are wrong in instructive ways: Araken "of Japanese origin" (it is Tupi), the city of Cerqueira César "in the north of Portugal" (it is in São Paulo), an invented 1573 genealogy for the Carrero family.

## Files

- `nomes.csv` / `nomes.parquet`: 46,840 given names, 31 columns.
- `sobrenomes.csv` / `sobrenomes.parquet`: 27,047 surnames, 11 columns.

Both tables have six keys for matching similar names: Portuguese Metaphone, OpenRefine fingerprint (with the 2023 bug documented), stems, character n-grams and a soft normalisation.

## Cleaning

Only rows with a usable text are published. Model refusals ("Não há um significado específico…", or any text that opens by saying no meaning is known), texts that switch to English, company words and codes were removed; sentence loops were cut; accent variants were merged. Surnames need 3 or more partners in the register; only counts are published, never a full name or a company.

Methodology, data quality report, data dictionary (EN and PT) and the build and validation scripts: **https://github.com/CaiqueDourado/nomes-e-sobrenomes-brasil**

## Related datasets

- [DedupKit](https://github.com/CaiqueDourado/DedupKit): matching library with the fixed fingerprint keyer and the Portuguese phonetic key
- [Municípios e Estados do Brasil](https://www.kaggle.com/datasets/caiquedourado/municipios-e-estados-do-brasil)
- [Catálogo de produtos do e-commerce brasileiro](https://www.kaggle.com/datasets/caiquedourado/catalogo-produtos-ecommerce-brasil)

License: CC BY 4.0. Author: Caique Dourado.
