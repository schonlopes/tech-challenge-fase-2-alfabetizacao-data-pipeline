CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_gold.indicador_municipio`
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY sigla_uf, id_municipio, rede AS
WITH enriched AS (
  SELECT
    m.ano, m.id_municipio, d.nome_municipio, d.sigla_uf, d.regiao,
    m.serie, m.rede, m.taxa_alfabetizacao, m.media_portugues,
    CASE m.ano
      WHEN 2024 THEN mm.meta_alfabetizacao_2024
      WHEN 2025 THEN mm.meta_alfabetizacao_2025
      WHEN 2026 THEN mm.meta_alfabetizacao_2026
      WHEN 2027 THEN mm.meta_alfabetizacao_2027
      WHEN 2028 THEN mm.meta_alfabetizacao_2028
      WHEN 2029 THEN mm.meta_alfabetizacao_2029
      WHEN 2030 THEN mm.meta_alfabetizacao_2030
    END AS meta_ano,
    mm.nivel_alfabetizacao,
    mm.percentual_participacao
  FROM `__PROJECT_ID__.alfabetizacao_silver.municipio` m
  LEFT JOIN `__PROJECT_ID__.alfabetizacao_silver.meta_alfabetizacao_municipio` mm
    ON m.ano=mm.ano AND m.id_municipio=mm.id_municipio AND m.rede=mm.rede
  LEFT JOIN `__PROJECT_ID__.alfabetizacao_silver.dim_municipio` d
    ON m.id_municipio=d.id_municipio
)
SELECT
  *, ROUND(taxa_alfabetizacao - meta_ano, 2) AS gap_meta_pp,
  CASE
    WHEN meta_ano IS NULL THEN 'SEM_META'
    WHEN taxa_alfabetizacao >= meta_ano THEN 'ATINGIDA'
    WHEN taxa_alfabetizacao >= meta_ano - 3 THEN 'ATENCAO'
    ELSE 'CRITICO'
  END AS status_meta,
  CURRENT_TIMESTAMP() AS _gold_processed_at
FROM enriched;

