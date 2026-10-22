# Data quality report

What is right, what is fixed, and what is still wrong. The removal counts are in `stats.json`; the rules are in `scripts/build.py`.

## The texts are model output, not facts

`meaning` and `history` were written by OpenAI models in 2023 and **no person checked them**. They read well and are often wrong. Examples that are still in the data, on purpose:

| Row | Text says | In fact |
|---|---|---|
| Araken | "nome masculino de origem japonesa" | Tupi origin |
| Shirley | "variação do nome inglês Cheryl" | Shirley is an English place name; Cheryl is a later name |
| Cerqueira | "originária da cidade de Cerqueira César, no norte de Portugal" | Cerqueira César is a city in São Paulo state |
| Braga | 557 histories say the family "é originária da cidade de Braga, no norte de Portugal" | A template, not a fact |
| Barboza | the whole history is about *Barbosa*, with an invented couple "Francisco Barbosa e Maria Nunes" | — |
| Carrero | "Pedro Carrero, que nasceu em Sevilha, Espanha, em 1573", five generations of "comerciante bem-sucedido" | An invented genealogy. In 2023 it reached the site and was shortened by hand |
| Silva | "o primeiro a usar o sobrenome Silva foi um guerreiro chamado Dinis de Silva" | The surname comes from Latin *silva*, "forest" |

Use the texts to study what language models write about names (style, made-up etymologies, repeated templates, how davinci and gpt-3.5 differ), not as a source of meanings. The davinci texts are short (median 68 characters for names); gpt-3.5 texts are longer (median 224) and hedge more.

## Fixed in this release

| # | Problem in the export | Rows | Fix |
|---|---|---:|---|
| 1 | Refusals stored as meanings: "Não há um significado específico para o nome…", "não é um nome", "Infelizmente…", "Como um modelo de língua, eu não posso…", and texts that open by saying no meaning is known before guessing one | 42,078 names, 1,513 surnames | Row removed (only rows with a text are published) |
| 2 | Histories that switch to English mid-text ("A história da família Saito data back to the 12th century") | 44 names, 1,263 surnames | Row removed |
| 3 | The model looping: the same sentence many times in one text | 433 surnames, 4 names | Repeated sentences removed |
| 4 | Two text columns with the same text in 59,214 names and 14,947 surnames | all | One text column plus `model` |
| 5 | Company names and codes taken as names (`Mercadolivre.com`, `Indica.com`, `M2K`, `B&B`) | 147 names, 173 surnames | Row removed |
| 6 | Company words taken as surnames (`Limitada`, `Participações`, `Servicos`, `Transportes`) | 17 + 17 | Row removed |
| 7 | Wrong accents in frequent names from the CNPJ export (`António`, `Joâo`, `Claúdia`, `Diêgo`) | 4 | Corrected, merged with the search row of the same name |
| 8 | The same name twice with different accents (`Júlio César` / `Julio Cesar`) | 78 names, 1 surname | One row, the spelling with more accents, the larger count |
| 9 | Names in capitals (`ANA`) | 2,903 in the export | Capitalised (`Ana`) |
| 10 | IBGE numbers as text, some with comma decimals (`"0,0003"`) | all | Typed |
| 11 | `ibge_regiao` always 0, `ibge_sexo` always empty, `buscouIBGE` always true | all | Columns left out |
| 12 | Leading blank lines in davinci texts | most of the 33,086 | Trimmed |

## Known limitations (kept as they are)

- **`key_fingerprint` has the 2023 bug.** The C# port of OpenRefine's fingerprint keyer skipped every other word while joining, so `Larissa no Amor` has the key `amor no`. It only matters for names with several words (2,390 rows, all affected). The bug and a fixed keyer are in [DedupKit](https://github.com/CaiqueDourado/DedupKit) (`legacy_fingerprint` reproduces it, `fingerprint` is correct). `key_ngram` keeps spaces inside the letter pairs, unlike OpenRefine.
- **Surnames without accents.** The CNPJ register is mostly written without accents, so `Goncalves`, `Guimaraes`, `Conceicao` appear as such.
- **Surnames are words, not always surnames.** Second given names (`Aparecida`, `Aparecido`, `Lourdes`) and suffixes (`Filho`, `Neto`, `Junior`) are among the most frequent "surnames", as they are in the register.
- **The CNPJ count is not population.** `cnpj_partners` counts company partners, who are adults and skew towards some regions and ages. For population use `ibge_frequency` (2010 Census).
- **IBGE fields are missing for 47% of names.** The API had no data for them. Another 6,639 names have a rank but no top state.
- **Search names.** Names from searches (`source = search`) may be rare spellings, nicknames or compound names nobody registered.
- **Coverage.** Only names and surnames the 2023 site had a text for; 82,975 names and 188,821 surnames were never sent to the model.
