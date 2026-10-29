# Nomes e sobrenomes do Brasil

[![validate](https://github.com/CaiqueDourado/brazilian-names-surnames/actions/workflows/validate.yml/badge.svg)](https://github.com/CaiqueDourado/brazilian-names-surnames/actions/workflows/validate.yml)
[![Dados: CC BY 4.0](https://img.shields.io/badge/dados-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA.md)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-blue.svg)](LICENSE)
[![Kaggle](https://img.shields.io/badge/Kaggle-dataset-20BEFF.svg)](https://www.kaggle.com/datasets/caiquedourado/nomes-e-sobrenomes-brasil)

[Read in English](README.md)

![Nomes e sobrenomes mais comuns do Brasil](docs/img/cover.png)

São 46.840 nomes e 27.047 sobrenomes brasileiros. Cada um traz quantos sócios do cadastro CNPJ o têm, e os nomes também trazem dados do Censo 2010 do IBGE: posição, frequência, estado onde o nome é mais comum, grafias relacionadas, quantos são mulheres e homens e a década de nascimento. Há ainda seis chaves fonéticas e de fingerprint e um significado ou história da família **escrito por modelos da OpenAI em 2023**, com o modelo indicado em cada linha.

É o banco por trás do **nomessobrenomes.com**, um site de 90 mil páginas que o autor fez em 2023. Dois usos:

- **Lista de nomes brasileiros com frequência real**, para separar nome e sobrenome, criar atributos de gênero ou região, gerar dados de teste e montar autocompletar.
- **Corpus de textos de modelos de linguagem sobre nomes**, para estudar alucinação: etimologias plausíveis e erradas, genealogias inventadas, fórmulas que o modelo repete e a diferença entre o text-davinci-002 e o gpt-3.5 na mesma tarefa.

| Arquivo | Linhas | Colunas | Formatos |
|---|---|---|---|
| `nomes` | 46.840 | 31 | CSV · Parquet |
| `sobrenomes` | 27.047 | 11 | CSV · Parquet |

## Prévia

| name | cnpj_partners | ibge_rank | ibge_top_state | model | meaning |
|---|---:|---:|---|---|---|
| José | 1.015.442 | 2 | Alagoas | text-davinci-002 | O nome Jose significa "Deus salva". *(José quer dizer "Deus acrescentará")* |
| Tadeu | 4.716 | 905 | Paraná | gpt-3.5 | O nome Tadeu tem origem hebraica e significa "o corajoso"… |
| Araken | 287 | 23.359 | Rio Grande do Norte | text-davinci-002 | Araken é um nome masculino de origem japonesa. *(errado: é tupi)* |

## Como usar

```python
import pandas as pd

base = "https://raw.githubusercontent.com/CaiqueDourado/brazilian-names-surnames/main/data/"
nomes = pd.read_parquet(base + "nomes.parquet")
sobrenomes = pd.read_parquet(base + "sobrenomes.parquet")

nomes.nlargest(10, "ibge_frequency")[["name", "ibge_frequency", "ibge_top_state"]]
```

```sql
-- DuckDB: nomes que soam parecido (mesma chave Metaphone português)
SELECT key_metaphone, list(name ORDER BY ibge_frequency DESC NULLS LAST)[1:6] AS grafias
FROM 'data/nomes.parquet'
GROUP BY key_metaphone HAVING count(*) > 3
ORDER BY sum(coalesce(ibge_frequency, 0)) DESC LIMIT 10;
```

## O que tem dentro

| Grupo | `nomes` | `sobrenomes` |
|---|---|---|
| Nome | `name_id`, `name`, `source` | `surname_id`, `surname` |
| Frequência | `cnpj_partners`, `ibge_rank`, `ibge_frequency`, `ibge_percent`, `ibge_top_state`, `ibge_top_state_per_100k`, `ibge_spellings` | `cnpj_partners` |
| Sexo e década de nascimento | `ibge_female`, `ibge_male`, `ibge_share_female`, `ibge_peak_decade`, `ibge_born_before_1930` … `ibge_born_2000s` | — |
| Texto escrito por modelo | `meaning`, `model` | `history`, `model` |
| Chaves para casamento | `key_metaphone`, `key_fingerprint`, `key_tokens`, `key_tokens_fingerprint`, `key_ngram`, `key_soft` | as mesmas seis |

Cada coluna está descrita no **[dicionário de dados](docs/data-dictionary.pt-BR.md)** ([EN](docs/data-dictionary.md)).

## Como foi feito

```mermaid
flowchart LR
    K["Buscas<br/>significado do nome X"] --> N
    A["Cadastro CNPJ<br/>nome dos sócios"] -->|"primeira palavra"| N["Nomes"]
    A -->|"demais palavras"| S["Sobrenomes"]
    N --> C["API do IBGE<br/>frequência, estado,<br/>sexo, década"]
    N --> D["GPT<br/>significado e história"]
    S --> D
    C --> E["Limpeza<br/>tira recusas e erros"]
    D --> E
    E --> F["Base publicada<br/>GitHub · Kaggle"]
```

Os nomes vieram de três fontes: a primeira palavra do nome dos sócios no cadastro CNPJ (dados abertos da Receita Federal, com 3 ou mais pessoas por nome), buscas por "significado do nome X" e as grafias listadas pela API de nomes do IBGE. Os sobrenomes são as outras palavras do nome dos sócios. Cada nome foi consultado na API de nomes do IBGE (próxima seção). Uma rotina em C# calculou seis chaves de casamento por linha, e modelos da OpenAI escreveram um significado para cada nome e uma história para cada sobrenome.

Nesta versão ficaram só as linhas com texto aproveitável. Saíram as recusas ("Não há um significado específico…" e todo texto que começa dizendo que não se conhece o significado), os textos que viram inglês no meio, as palavras de razão social e os códigos de empresa. As frases repetidas pelos laços do modelo foram cortadas, e as variantes de acento, unidas. O passo a passo, com as contagens, está na [metodologia](docs/methodology.md) (em inglês).

## O site: nomessobrenomes.com (2023)

[![nomessobrenomes.com](https://raw.githubusercontent.com/CaiqueDourado/CaiqueDourado/main/assets/nomessobrenomes.com_screenshot.png)](https://web.archive.org/web/20250610174857/https://nomessobrenomes.com/qual-o-significado-do-nome-alan-gustavo)

*nomessobrenomes.com, [arquivado no Wayback Machine](https://web.archive.org/web/20250610174857/https://nomessobrenomes.com/qual-o-significado-do-nome-alan-gustavo).*

Um site de SEO programático com cerca de **90 mil páginas estáticas**, feito pelo autor a partir desta tabela:

| Parte | Como funcionava |
|---|---|
| Páginas | Uma por nome ("Qual o significado do nome X?"), uma por sobrenome ("Qual a história e origem do sobrenome X?") e um post de blog por estado com os 100 nomes mais comuns (dados do IBGE, com a bandeira do estado) |
| Geração | Tabelas e procedures no SQL Server montavam os dados de cada página, e um gerador em C# escrevia arquivos HTML. Nenhum banco nem servidor na hora do acesso |
| Hospedagem | **Google Cloud Storage** como site estático: serverless, sem servidor para manter, escala com o tráfego |
| Desempenho | 100% mobile-friendly, notas máximas nos **Core Web Vitals** (HTML estático, sem framework no navegador) |
| Dados estruturados | **JSON-LD** em todas as páginas: `FAQPage`, `ItemList`, `WebSite`, `BreadcrumbList` e `Article` |
| Imagens | Banners e imagens para redes sociais (formatos stories e post) gerados em C# para cada nome |
| Nomes parecidos | Ligados pelas seis chaves (mesmo Metaphone, fingerprint, radicais…) |
| Qualidade do texto | Checagens em SQL em toda resposta do modelo antes de publicar: recusas, respostas em inglês, n-gramas de 2 a 5 palavras para achar as frases feitas do modelo, palavras e frases repetidas, respostas cortadas pelo limite de tokens (aparadas até a última frase completa) |
| URLs | Slugs a partir do título, numerados quando repetiam, com os nomes reservados do Windows (`con`, `prn`) tratados, já que as páginas eram arquivos em disco |

As fontes foram o cadastro CNPJ (Receita Federal), a API de nomes do IBGE e listas de palavras-chave; os textos vieram do text-davinci-002 e depois do gpt-3.5. Detalhes na [metodologia](docs/methodology.md#the-site).

## A API de nomes do IBGE

Cada nome foi consultado na **API de nomes do IBGE**, o serviço público que responde a partir do **Censo 2010** (pessoas contadas pelo primeiro nome). Sem chave e sem login. Em 2023 o site só chamou o endpoint básico. Para esta versão, os outros endpoints foram chamados com o [ibge-nomes](https://github.com/CaiqueDourado/ibge-nomes), um cliente escrito para isso, para preencher sexo e década de nascimento.

```text
GET https://servicodados.ibge.gov.br/api/v1/censos/nomes/basica?nome=caique
```

```json
[{"rank":529,"nome":"CAIQUE","freq":50902,"percentual":0.0278,"ufMax":"Bahia","ufMaxProp":"68.3960","regiao":0,"sexo":"","nomes":"CAYQUE,KAIQUE,KAYQUE"}]
```

| Campo da API | Coluna aqui | O que significa |
|---|---|---|
| `rank` | `ibge_rank` | Posição entre todos os primeiros nomes do Censo (1 = Maria) |
| `freq` | `ibge_frequency` | Pessoas com exatamente essa grafia em 2010 |
| `percentual` | `ibge_percent` | Percentual da população |
| `ufMax` | `ibge_top_state` | Estado onde o nome é proporcionalmente mais comum |
| `ufMaxProp` | `ibge_top_state_per_100k` | Pessoas com o nome a cada 100 mil habitantes desse estado |
| `nomes` | `ibge_spellings` | Grafias relacionadas que o IBGE lista para esse nome (a `,` virou `\|`) |
| `regiao`, `sexo` | — | Repetem os filtros da consulta; as chamadas de 2023 não usaram filtro, por isso `0` e vazio |

```text
GET https://servicodados.ibge.gov.br/api/v2/censos/nomes/caique|maria?sexo=F
```

O endpoint v2 responde quantas pessoas com cada nome nasceram em cada década (de antes de 1930 até os anos 2000), para vários nomes numa chamada, e pode filtrar só mulheres (`sexo=F`) ou só homens (`sexo=M`). Três chamadas por lote de 20 nomes deram:

| Colunas | O que trazem |
|---|---|
| `ibge_female`, `ibge_male`, `ibge_share_female` | Pessoas de cada sexo com essa grafia e a proporção de mulheres |
| `ibge_born_before_1930` … `ibge_born_2000s` | Pessoas com essa grafia nascidas em cada década (vivas em 2010) |
| `ibge_peak_decade` | A década com mais nascimentos do nome |

Cada grafia tem a própria contagem; `nomes` só aponta as grafias relacionadas (Caique 50.902, Kaique 43.883, Cayque 475). As grafias de `nomes` que ainda não estavam na tabela entraram como nomes próprios (`source = ibge_variant`). Nomes que a API não conhece (grafias raras e todo nome composto, porque o Censo conta só o primeiro nome) ficam com as colunas do IBGE vazias. Detalhes na [metodologia](docs/methodology.md#the-ibge-names-api).

```python
from ibge_nomes import IbgeNomes   # pip install "ibge-nomes @ git+https://github.com/CaiqueDourado/ibge-nomes"

ibge = IbgeNomes()
ibge.basic("Caique")["freq"]                  # 50902
ibge.by_decade(["Caique"], sex="F")           # mulheres chamadas Caique, por década de nascimento
```

## Qualidade dos dados

**Os textos não são fatos.** Ninguém os revisou. Alguns exemplos de erros do modelo:

- diz que Araken é japonês, quando é tupi;
- põe a cidade de Cerqueira César "no norte de Portugal", quando ela fica em São Paulo;
- escreve a história dos Barboza falando dos Barbosa;
- dá aos Carrero um fundador nascido em Sevilha em 1573, seguido de cinco gerações de "comerciantes bem-sucedidos", tudo inventado.

Esses exemplos ficaram na base de propósito. O relatório completo está em [data-quality.md](docs/data-quality.md). Ele mostra o que foi corrigido e o bug conhecido de `key_fingerprint`.

**Privacidade.** Só são publicadas contagens por nome ou por sobrenome: nenhum nome completo, nenhuma empresa. Sobrenomes com menos de 3 sócios ficaram de fora.

## Estrutura do repositório

```text
data/          nomes.csv/.parquet, sobrenomes.csv/.parquet, dataset-metadata.json (Kaggle)
schema/        definição das colunas e metadados: fonte única da documentação e do Kaggle
scripts/       build.py (exportação → data), validate.py (checagens), docs.py (dicionários + Kaggle), make_figures.py
notebooks/     eda.ipynb, análise exploratória
docs/          dicionário de dados, metodologia, qualidade, descrição do Kaggle, imagens
stats.json     o que cada etapa removeu, linhas por modelo e por origem
```

A exportação do SQL Server não é redistribuída. Com ela, `python scripts/build.py --raw <pasta>` refaz `data/`. As checagens que o CI roda a cada push estão em `python scripts/validate.py`.

## Relacionados

- [ibge-nomes](https://github.com/CaiqueDourado/ibge-nomes): o cliente usado na API de nomes do IBGE.
- [DedupKit](https://github.com/CaiqueDourado/DedupKit): a biblioteca de casamento, com o fingerprint corrigido e a chave fonética em português.
- [Municípios e estados do Brasil](https://github.com/CaiqueDourado/municipios-e-estados-do-brasil): códigos do IBGE, Censo e mapas, para os estados de `ibge_top_state`.
- [Catálogo de produtos do e-commerce brasileiro](https://github.com/CaiqueDourado/brazilian-ecommerce-products), do mesmo data lake.
- [dicionario-portugues](https://github.com/CaiqueDourado/dicionario-portugues): 272 mil palavras do português com chaves fonéticas, rimas e textos gerados por IA ([Kaggle](https://www.kaggle.com/datasets/caiquedourado/dicionario-portugues)), com as mesmas chaves fonéticas.

## Licença

Dados: [CC BY 4.0](LICENSE-DATA.md). Código: [MIT](LICENSE). Para citar, veja [CITATION.cff](CITATION.cff).

## Autor

**Caique Dourado**: 20 anos construindo crawlers, pipelines de dados e SEO programático em .NET e SQL Server. Mais em [github.com/CaiqueDourado](https://github.com/CaiqueDourado).
