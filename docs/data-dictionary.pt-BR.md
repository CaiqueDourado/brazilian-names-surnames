# Dicionário de dados: Nomes e sobrenomes do Brasil: frequência, dados do IBGE e significados escritos por IA

Gerado por `scripts/docs.py` a partir de `schema/columns.json`. Tipos, nulos e exemplos vêm dos arquivos em `data/`.

## `nomes.csv`

Uma linha por nome (46.840): significado escrito pelo GPT, contagem de sócios no CNPJ, frequência no Censo 2010 do IBGE e chaves fonéticas.

| Coluna | Tipo | Nulos | Exemplo | Descrição | Padrão | Origem |
|---|---|---|---|---|---|---|
| `name_id` | integer | 0,0% | `83309` | Id do nome no banco de 2023. Chave primária. | — | fonte |
| `name` | string | 0,0% | `Gertraude` | Nome como publicado no site, com iniciais maiúsculas ("José", "Maria Júlia"). | — | fonte |
| `meaning` | string | 0,0% | `Gertraude é um nome feminino alemão q…` | Significado do nome em português, escrito por um modelo da OpenAI em 2023. Não foi conferido por pessoa: pode estar errado ou ser inventado. Parágrafos separados por quebra de linha. | — | gerado |
| `model` | string | 0,0% | `gpt-3.5` | Modelo que escreveu o texto: `text-davinci-002` ou `gpt-3.5`. | — | fonte |
| `source` | string | 0,0% | `cnpj` | De onde veio o nome: `cnpj` (primeiro nome de sócios no cadastro CNPJ), `search` (buscas "significado do nome X"), `ibge_variant` (grafia listada pela API do IBGE para outro nome). | — | derivado |
| `cnpj_partners` | integer | 10,7% | `4` | Quantidade de sócios no cadastro CNPJ com esse primeiro nome (3 ou mais). Vazio quando o nome não veio do cadastro. | — | fonte |
| `ibge_rank` | integer | 47,2% | `18616` | Posição do nome na lista de nomes do Censo 2010 do IBGE (1 = mais comum). Vazio quando a API não tinha dado. | IBGE Nomes | enriquecimento |
| `ibge_frequency` | integer | 47,2% | `322` | Pessoas com exatamente essa grafia no Censo 2010, segundo a API do IBGE. | IBGE Nomes | enriquecimento |
| `ibge_percent` | float | 47,2% | `0.0002` | Percentual da população com o nome. | IBGE Nomes | enriquecimento |
| `ibge_top_state` | string | 61,3% | `Rio Grande do Sul` | Estado (UF) onde o nome é proporcionalmente mais comum. | IBGE Nomes | enriquecimento |
| `ibge_top_state_per_100k` | float | 61,3% | `1.0754` | Pessoas com o nome por 100 mil habitantes nesse estado. | IBGE Nomes | enriquecimento |
| `ibge_spellings` | string (list) | 62,2% | `LEUNICE` | Grafias relacionadas que a API do IBGE lista para esse nome, separadas por `\|` ("CAYQUE\|KAIQUE\|KAYQUE"). Cada uma tem a própria frequência. | IBGE Nomes | enriquecimento |
| `ibge_female` | integer | 77,9% | `1496` | Mulheres com essa grafia no Censo 2010 (soma das décadas do endpoint v2 com `sexo=F`). | IBGE Nomes | enriquecimento |
| `ibge_male` | integer | 79,5% | `15280` | Homens com essa grafia no Censo 2010 (endpoint v2 com `sexo=M`). | IBGE Nomes | enriquecimento |
| `ibge_share_female` | float | 63,3% | `1.0` | `ibge_female / (ibge_female + ibge_male)`, de 0 a 1. | IBGE Nomes | enriquecimento |
| `ibge_peak_decade` | string | 62,6% | `2000s` | Década de nascimento com mais pessoas com essa grafia (`before_1930`, `1930s` … `2000s`). | IBGE Nomes | enriquecimento |
| `ibge_born_before_1930` | integer | 91,5% | `2111` | Pessoas com essa grafia nascidas antes de 1930, vivas em 2010 (endpoint v2). | IBGE Nomes | enriquecimento |
| `ibge_born_1930s` | integer | 86,8% | `67` | Pessoas com essa grafia nascidas na década de 1930, vivas em 2010 (endpoint v2). | IBGE Nomes | enriquecimento |
| `ibge_born_1940s` | integer | 83,3% | `85` | Pessoas com essa grafia nascidas na década de 1940, vivas em 2010 (endpoint v2). | IBGE Nomes | enriquecimento |
| `ibge_born_1950s` | integer | 80,2% | `150` | Pessoas com essa grafia nascidas na década de 1950, vivas em 2010 (endpoint v2). | IBGE Nomes | enriquecimento |
| `ibge_born_1960s` | integer | 77,1% | `32` | Pessoas com essa grafia nascidas na década de 1960, vivas em 2010 (endpoint v2). | IBGE Nomes | enriquecimento |
| `ibge_born_1970s` | integer | 74,6% | `42` | Pessoas com essa grafia nascidas na década de 1970, vivas em 2010 (endpoint v2). | IBGE Nomes | enriquecimento |
| `ibge_born_1980s` | integer | 72,0% | `73` | Pessoas com essa grafia nascidas na década de 1980, vivas em 2010 (endpoint v2). | IBGE Nomes | enriquecimento |
| `ibge_born_1990s` | integer | 73,1% | `6438` | Pessoas com essa grafia nascidas na década de 1990, vivas em 2010 (endpoint v2). | IBGE Nomes | enriquecimento |
| `ibge_born_2000s` | integer | 77,4% | `33` | Pessoas com essa grafia nascidas na década de 2000, vivas em 2010 (endpoint v2). | IBGE Nomes | enriquecimento |
| `key_metaphone` | string | 0,0% | `JRTRLD` | Chave fonética: Metaphone português (porta do pt_metaphone de Várzea Paulista, 2008). Nomes com a mesma chave soam parecido. | — | derivado |
| `key_fingerprint` | string | 0,0% | `gertraude` | Chave fingerprint do OpenRefine como calculada em 2023. A porta tinha um bug que guarda só uma palavra sim, outra não; em nomes com várias palavras, metade delas some (ver data-quality). | — | derivado |
| `key_tokens` | string | 0,6% | `tem` | Palavras reduzidas ao radical pelo stemmer brasileiro (Lucene), na ordem original ("Lucas" → "luc"). | — | derivado |
| `key_tokens_fingerprint` | string | 0,6% | `tem` | Os radicais de `key_tokens`, em ordem alfabética. | — | derivado |
| `key_ngram` | string | 0,0% | `audeergerarttrud` | Fingerprint de 2-gramas de caracteres (variante do OpenRefine): os pares de letras do nome, ordenados, sem repetição e juntados. | — | derivado |
| `key_soft` | string | 0,0% | `gertraude` | Minúsculas, sem acento, só letras, dígitos e espaços. | — | derivado |

## `sobrenomes.csv`

Uma linha por sobrenome (27.047): história escrita pelo GPT, contagem de sócios no CNPJ e chaves fonéticas.

| Coluna | Tipo | Nulos | Exemplo | Descrição | Padrão | Origem |
|---|---|---|---|---|---|---|
| `surname_id` | integer | 0,0% | `59110` | Id do sobrenome no banco de 2023. Chave primária. | — | fonte |
| `surname` | string | 0,0% | `Missfeld` | Sobrenome como aparece no cadastro CNPJ, com inicial maiúscula. Acentos seguem o cadastro, que muitas vezes não tem ("Goncalves"). | — | fonte |
| `history` | string | 0,0% | `A origem da família Missfeld é alemã.…` | História e origem do sobrenome em português, escrita por um modelo da OpenAI em 2023. Não foi conferida por pessoa: pode trazer pessoas, datas e lugares inventados. | — | gerado |
| `model` | string | 0,0% | `gpt-3.5` | Modelo que escreveu o texto: `text-davinci-002` ou `gpt-3.5`. | — | fonte |
| `cnpj_partners` | integer | 0,0% | `14` | Quantidade de sócios no cadastro CNPJ cujo nome contém esse sobrenome (3 ou mais). | — | fonte |
| `key_metaphone` | string | 0,0% | `MSFLD` | Chave fonética: Metaphone português (porta do pt_metaphone de Várzea Paulista, 2008). Nomes com a mesma chave soam parecido. | — | derivado |
| `key_fingerprint` | string | 0,0% | `missfeld` | Chave fingerprint do OpenRefine como calculada em 2023. A porta tinha um bug que guarda só uma palavra sim, outra não; em nomes com várias palavras, metade delas some (ver data-quality). | — | derivado |
| `key_tokens` | string | 0,2% | `colett` | Palavras reduzidas ao radical pelo stemmer brasileiro (Lucene), na ordem original ("Lucas" → "luc"). | — | derivado |
| `key_tokens_fingerprint` | string | 0,2% | `colett` | Os radicais de `key_tokens`, em ordem alfabética. | — | derivado |
| `key_ngram` | string | 0,0% | `elfeisldmisfss` | Fingerprint de 2-gramas de caracteres (variante do OpenRefine): os pares de letras do nome, ordenados, sem repetição e juntados. | — | derivado |
| `key_soft` | string | 0,0% | `missfeld` | Minúsculas, sem acento, só letras, dígitos e espaços. | — | derivado |

## Convenções

- Codificação UTF-8 sem BOM, separador vírgula, cabeçalho na primeira linha. Textos podem ter quebra de linha dentro de células entre aspas.
- Listas dentro de uma célula usam `|` como separador.
- Célula vazia = desconhecido ou não se aplica. Separador decimal é o ponto `.`.
- `meaning` e `history` foram escritos por modelos de linguagem e nunca revisados por pessoa. Use como exemplo de saída de modelo, não como fato.
