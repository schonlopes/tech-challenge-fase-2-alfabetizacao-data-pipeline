# Dicionário de dados

Contratos conferidos na página oficial do conjunto
`basedosdados.br_inep_avaliacao_alfabetizacao` em 26/08/2026.

## Entidades de origem

### `uf`

Grão: `ano + sigla_uf + serie + rede`.

| Campo | Tipo | Significado |
|---|---|---|
| `ano` | INT64 | Ano de aplicação da avaliação estadual |
| `sigla_uf` | STRING | Sigla da unidade da federação |
| `serie` | STRING | Ano escolar |
| `rede` | STRING | Rede de ensino avaliada |
| `taxa_alfabetizacao` | FLOAT64 | Percentual de estudantes alfabetizados |
| `media_portugues` | FLOAT64 | Média equalizada com o SAEB |
| `proporcao_aluno_nivel_0` … `_8` | FLOAT64 | Distribuição percentual nos nove níveis |

### `meta_alfabetizacao_brasil`

Grão: `ano + rede`.

| Campo | Tipo | Significado |
|---|---|---|
| `ano` | INT64 | Ano da avaliação |
| `rede` | STRING | Rede de ensino |
| `taxa_alfabetizacao` | FLOAT64 | Resultado nacional observado |
| `meta_alfabetizacao_2024` … `_2030` | FLOAT64 | Metas anuais do compromisso |
| `percentual_participacao` | FLOAT64 | Participação na avaliação |

### `meta_alfabetizacao_uf`

Grão: `ano + sigla_uf + rede`. Possui os mesmos campos de meta nacional e
acrescenta `sigla_uf`.

### `meta_alfabetizacao_municipio`

Grão: `ano + id_municipio + rede`.

| Campo | Tipo | Significado |
|---|---|---|
| `ano` | INT64 | Ano da avaliação |
| `id_municipio` | STRING | Código IBGE de sete dígitos |
| `rede` | STRING | Rede de ensino |
| `taxa_alfabetizacao` | FLOAT64 | Resultado municipal observado |
| `meta_alfabetizacao_2024` … `_2030` | FLOAT64 | Metas anuais municipais |
| `nivel_alfabetizacao` | INT64 | Nível de alfabetização informado pela fonte |
| `percentual_participacao` | FLOAT64 | Participação municipal |

### `municipio`

Grão: `ano + id_municipio + serie + rede`.

| Campo | Tipo | Significado |
|---|---|---|
| `ano` | INT64 | Ano de aplicação |
| `id_municipio` | STRING | Código IBGE de sete dígitos |
| `serie` | STRING | Ano escolar |
| `rede` | STRING | Rede de ensino |
| `taxa_alfabetizacao` | FLOAT64 | Percentual alfabetizado no município |
| `media_portugues` | FLOAT64 | Média municipal equalizada com o SAEB |
| `proporcao_aluno_nivel_0` … `_8` | FLOAT64 | Distribuição percentual nos nove níveis |

### `alunos`

Grão Silver: `ano + id_aluno`.

| Campo | Tipo | Significado |
|---|---|---|
| `ano` | INT64 | Ano de aplicação |
| `id_municipio` | STRING | Município da escola |
| `id_escola` | STRING | Máscara/código fictício de escola |
| `id_aluno` | STRING | Código pseudonimizado do aluno |
| `caderno` | STRING | Código do caderno de Língua Portuguesa |
| `serie` | STRING | Ano escolar |
| `rede` | STRING | Dependência administrativa |
| `presenca` | STRING | Indicador de presença |
| `preenchimento_caderno` | STRING | Indicador de preenchimento |
| `alfabetizado` | STRING | Classificação de alfabetização |
| `proficiencia` | FLOAT64 | Proficiência equalizada com o SAEB |
| `peso_aluno` | FLOAT64 | Peso amostral |

No streaming são acrescentados `event_id`, `event_ts` e `event_date`.

## Enriquecimento

`dim_municipio` deriva do diretório oficial da Base dos Dados e acrescenta
nome do município, UF e região. O arquivo local contém somente os municípios da
amostra; o SQL cloud utiliza o diretório nacional.

## Produtos Gold

### `indicador_municipio`

Campos de negócio: `taxa_alfabetizacao`, `media_portugues`, `meta_ano`,
`gap_meta_pp`, `status_meta`, `nivel_alfabetizacao` e
`percentual_participacao`. Status possíveis: `ATINGIDA`, `ATENCAO`, `CRITICO` e
`SEM_META`.

### `meta_resultado_municipio`

Uma linha por município/rede/ano-meta entre 2024 e 2030. `resultado` permanece
nulo enquanto a avaliação daquele ano não estiver disponível; nesse caso o
status é `AGUARDANDO_RESULTADO`.

### `evolucao_municipio`

Inclui `taxa_ano_anterior` e `variacao_anual_pp`, calculadas por janela.

### `monitoramento_stream`

Agrega `alunos_recebidos`, `alunos_presentes`, `taxa_alfabetizacao_amostra`,
`media_proficiencia` e `ultimo_evento`.

