CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_silver.uf`
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY sigla_uf, rede AS
SELECT
  CAST(ano AS INT64) AS ano,
  UPPER(TRIM(sigla_uf)) AS sigla_uf,
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
FROM `__PROJECT_ID__.alfabetizacao_bronze.uf`
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY ano, sigla_uf, serie, rede ORDER BY _ingested_at DESC
) = 1;

