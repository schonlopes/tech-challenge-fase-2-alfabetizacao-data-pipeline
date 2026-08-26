CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_gold.monitoramento_stream`
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY sigla_uf, id_municipio, rede AS
SELECT
  a.ano, a.id_municipio, d.nome_municipio, d.sigla_uf, a.rede,
  COUNT(*) AS alunos_recebidos,
  COUNTIF(a.presenca='Presente') AS alunos_presentes,
  ROUND(100 * SAFE_DIVIDE(COUNTIF(a.alfabetizado='Sim'), COUNTIF(a.presenca='Presente')), 2)
    AS taxa_alfabetizacao_amostra,
  ROUND(AVG(IF(a.presenca='Presente', a.proficiencia, NULL)), 2) AS media_proficiencia,
  MAX(a.event_ts) AS ultimo_evento,
  CURRENT_TIMESTAMP() AS _gold_processed_at
FROM `__PROJECT_ID__.alfabetizacao_silver.alunos` a
LEFT JOIN `__PROJECT_ID__.alfabetizacao_silver.dim_municipio` d
  ON a.id_municipio=d.id_municipio
GROUP BY a.ano, a.id_municipio, d.nome_municipio, d.sigla_uf, a.rede;

