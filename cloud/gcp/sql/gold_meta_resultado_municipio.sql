CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_gold.meta_resultado_municipio`
PARTITION BY RANGE_BUCKET(ano_meta, GENERATE_ARRAY(2024, 2031, 1))
CLUSTER BY sigla_uf, id_municipio, rede AS
WITH latest_meta AS (
  SELECT * EXCEPT(rn)
  FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY id_municipio, rede ORDER BY ano DESC) AS rn
    FROM `__PROJECT_ID__.alfabetizacao_silver.meta_alfabetizacao_municipio`
  )
  WHERE rn=1
), targets AS (
  SELECT id_municipio, rede, 2024 AS ano_meta, meta_alfabetizacao_2024 AS meta FROM latest_meta
  UNION ALL SELECT id_municipio, rede, 2025, meta_alfabetizacao_2025 FROM latest_meta
  UNION ALL SELECT id_municipio, rede, 2026, meta_alfabetizacao_2026 FROM latest_meta
  UNION ALL SELECT id_municipio, rede, 2027, meta_alfabetizacao_2027 FROM latest_meta
  UNION ALL SELECT id_municipio, rede, 2028, meta_alfabetizacao_2028 FROM latest_meta
  UNION ALL SELECT id_municipio, rede, 2029, meta_alfabetizacao_2029 FROM latest_meta
  UNION ALL SELECT id_municipio, rede, 2030, meta_alfabetizacao_2030 FROM latest_meta
)
SELECT
  t.ano_meta, t.id_municipio, d.nome_municipio, d.sigla_uf, d.regiao,
  t.rede, t.meta, r.taxa_alfabetizacao AS resultado,
  ROUND(r.taxa_alfabetizacao - t.meta, 2) AS gap_meta_pp,
  CASE
    WHEN r.taxa_alfabetizacao IS NULL THEN 'AGUARDANDO_RESULTADO'
    WHEN r.taxa_alfabetizacao >= t.meta THEN 'ATINGIDA'
    WHEN r.taxa_alfabetizacao >= t.meta - 3 THEN 'ATENCAO'
    ELSE 'CRITICO'
  END AS status_meta,
  CURRENT_TIMESTAMP() AS _gold_processed_at
FROM targets t
LEFT JOIN `__PROJECT_ID__.alfabetizacao_silver.municipio` r
  ON r.ano=t.ano_meta AND r.id_municipio=t.id_municipio AND r.rede=t.rede
LEFT JOIN `__PROJECT_ID__.alfabetizacao_silver.dim_municipio` d
  ON t.id_municipio=d.id_municipio;

