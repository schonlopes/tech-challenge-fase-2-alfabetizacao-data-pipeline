CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_silver.meta_alfabetizacao_brasil`
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY rede AS
SELECT
  CAST(ano AS INT64) AS ano,
  TRIM(rede) AS rede,
  SAFE_CAST(taxa_alfabetizacao AS FLOAT64) AS taxa_alfabetizacao,
  SAFE_CAST(meta_alfabetizacao_2024 AS FLOAT64) AS meta_alfabetizacao_2024,
  SAFE_CAST(meta_alfabetizacao_2025 AS FLOAT64) AS meta_alfabetizacao_2025,
  SAFE_CAST(meta_alfabetizacao_2026 AS FLOAT64) AS meta_alfabetizacao_2026,
  SAFE_CAST(meta_alfabetizacao_2027 AS FLOAT64) AS meta_alfabetizacao_2027,
  SAFE_CAST(meta_alfabetizacao_2028 AS FLOAT64) AS meta_alfabetizacao_2028,
  SAFE_CAST(meta_alfabetizacao_2029 AS FLOAT64) AS meta_alfabetizacao_2029,
  SAFE_CAST(meta_alfabetizacao_2030 AS FLOAT64) AS meta_alfabetizacao_2030,
  SAFE_CAST(percentual_participacao AS FLOAT64) AS percentual_participacao,
  _ingested_at,
  CURRENT_TIMESTAMP() AS _processed_at
FROM `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_brasil`
QUALIFY ROW_NUMBER() OVER (PARTITION BY ano, rede ORDER BY _ingested_at DESC) = 1;

