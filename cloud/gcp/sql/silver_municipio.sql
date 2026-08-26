CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_silver.dim_municipio`
CLUSTER BY id_municipio AS
SELECT DISTINCT
  LPAD(TRIM(id_municipio), 7, '0') AS id_municipio,
  TRIM(nome) AS nome_municipio,
  UPPER(TRIM(sigla_uf)) AS sigla_uf,
  CASE
    WHEN sigla_uf IN ('AC','AM','AP','PA','RO','RR','TO') THEN 'Norte'
    WHEN sigla_uf IN ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
    WHEN sigla_uf IN ('DF','GO','MS','MT') THEN 'Centro-Oeste'
    WHEN sigla_uf IN ('ES','MG','RJ','SP') THEN 'Sudeste'
    WHEN sigla_uf IN ('PR','RS','SC') THEN 'Sul'
  END AS regiao,
  CURRENT_TIMESTAMP() AS _processed_at
FROM `basedosdados.br_bd_diretorios_brasil.municipio`;

CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_silver.municipio`
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY id_municipio, rede AS
SELECT
  CAST(ano AS INT64) AS ano,
  LPAD(TRIM(id_municipio), 7, '0') AS id_municipio,
  TRIM(serie) AS serie,
  TRIM(rede) AS rede,
  SAFE_CAST(taxa_alfabetizacao AS FLOAT64) AS taxa_alfabetizacao,
  SAFE_CAST(media_portugues AS FLOAT64) AS media_portugues,
  SAFE_CAST(proporcao_aluno_nivel_0 AS FLOAT64) AS proporcao_aluno_nivel_0,
  SAFE_CAST(proporcao_aluno_nivel_1 AS FLOAT64) AS proporcao_aluno_nivel_1,
  SAFE_CAST(proporcao_aluno_nivel_2 AS FLOAT64) AS proporcao_aluno_nivel_2,
  SAFE_CAST(proporcao_aluno_nivel_3 AS FLOAT64) AS proporcao_aluno_nivel_3,
  SAFE_CAST(proporcao_aluno_nivel_4 AS FLOAT64) AS proporcao_aluno_nivel_4,
  SAFE_CAST(proporcao_aluno_nivel_5 AS FLOAT64) AS proporcao_aluno_nivel_5,
  SAFE_CAST(proporcao_aluno_nivel_6 AS FLOAT64) AS proporcao_aluno_nivel_6,
  SAFE_CAST(proporcao_aluno_nivel_7 AS FLOAT64) AS proporcao_aluno_nivel_7,
  SAFE_CAST(proporcao_aluno_nivel_8 AS FLOAT64) AS proporcao_aluno_nivel_8,
  _ingested_at,
  CURRENT_TIMESTAMP() AS _processed_at
FROM `__PROJECT_ID__.alfabetizacao_bronze.municipio`
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY ano, id_municipio, serie, rede ORDER BY _ingested_at DESC
) = 1;

