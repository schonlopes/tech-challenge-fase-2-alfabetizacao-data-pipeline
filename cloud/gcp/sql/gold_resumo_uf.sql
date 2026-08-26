CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_gold.resumo_uf`
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY sigla_uf, rede AS
SELECT
  u.ano, u.sigla_uf, u.rede, u.taxa_alfabetizacao, u.media_portugues,
  mu.percentual_participacao,
  CASE u.ano WHEN 2024 THEN mu.meta_alfabetizacao_2024 END AS meta_ano,
  ROUND(u.taxa_alfabetizacao -
    CASE u.ano WHEN 2024 THEN mu.meta_alfabetizacao_2024 END, 2
  ) AS gap_meta_pp,
  CURRENT_TIMESTAMP() AS _gold_processed_at
FROM `__PROJECT_ID__.alfabetizacao_silver.uf` u
LEFT JOIN `__PROJECT_ID__.alfabetizacao_silver.meta_alfabetizacao_uf` mu
  ON u.ano=mu.ano AND u.sigla_uf=mu.sigla_uf AND u.rede=mu.rede;

