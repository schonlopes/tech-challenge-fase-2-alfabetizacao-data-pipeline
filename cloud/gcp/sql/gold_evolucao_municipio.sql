CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_gold.evolucao_municipio`
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY sigla_uf, id_municipio, rede AS
SELECT
  m.ano, m.id_municipio, d.nome_municipio, d.sigla_uf, d.regiao,
  m.rede, m.taxa_alfabetizacao,
  LAG(m.taxa_alfabetizacao) OVER (
    PARTITION BY m.id_municipio, m.rede ORDER BY m.ano
  ) AS taxa_ano_anterior,
  ROUND(m.taxa_alfabetizacao - LAG(m.taxa_alfabetizacao) OVER (
    PARTITION BY m.id_municipio, m.rede ORDER BY m.ano
  ), 2) AS variacao_anual_pp,
  CURRENT_TIMESTAMP() AS _gold_processed_at
FROM `__PROJECT_ID__.alfabetizacao_silver.municipio` m
LEFT JOIN `__PROJECT_ID__.alfabetizacao_silver.dim_municipio` d
  ON m.id_municipio=d.id_municipio;

