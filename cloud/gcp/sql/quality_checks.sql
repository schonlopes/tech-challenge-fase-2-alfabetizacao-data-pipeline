CREATE TABLE IF NOT EXISTS `__PROJECT_ID__.alfabetizacao_monitoring.quality_results` (
  check_name STRING,
  layer STRING,
  table_name STRING,
  severity STRING,
  passed BOOL,
  observed INT64,
  expectation STRING,
  checked_at TIMESTAMP
)
PARTITION BY DATE(checked_at)
CLUSTER BY layer, table_name, severity;

DELETE FROM `__PROJECT_ID__.alfabetizacao_monitoring.quality_results`
WHERE DATE(checked_at)=CURRENT_DATE();

INSERT INTO `__PROJECT_ID__.alfabetizacao_monitoring.quality_results`
WITH checks AS (
  SELECT 'municipio_unique_key' AS check_name, 'silver' AS layer, 'municipio' AS table_name,
         'critical' AS severity,
         COUNT(*) - COUNT(DISTINCT STRUCT(ano,id_municipio,serie,rede)) AS observed,
         '= 0' AS expectation
  FROM `__PROJECT_ID__.alfabetizacao_silver.municipio`
  UNION ALL
  SELECT 'alunos_not_null_key','silver','alunos','critical',
         COUNTIF(ano IS NULL OR id_aluno IS NULL OR TRIM(id_aluno)=''), '= 0'
  FROM `__PROJECT_ID__.alfabetizacao_silver.alunos`
  UNION ALL
  SELECT 'municipio_taxa_range','silver','municipio','critical',
         COUNTIF(taxa_alfabetizacao NOT BETWEEN 0 AND 100), '= 0'
  FROM `__PROJECT_ID__.alfabetizacao_silver.municipio`
  UNION ALL
  SELECT 'municipio_fk','silver','municipio','critical', COUNTIF(d.id_municipio IS NULL), '= 0'
  FROM `__PROJECT_ID__.alfabetizacao_silver.municipio` m
  LEFT JOIN `__PROJECT_ID__.alfabetizacao_silver.dim_municipio` d USING(id_municipio)
  UNION ALL
  SELECT 'literacy_cutoff_consistency','silver','alunos','critical',
         COUNTIF(presenca='Presente' AND proficiencia IS NOT NULL AND
           ((proficiencia>=743 AND alfabetizado!='Sim') OR (proficiencia<743 AND alfabetizado!='Nao'))),
         'alfabetizado equivale a proficiencia >= 743'
  FROM `__PROJECT_ID__.alfabetizacao_silver.alunos`
  UNION ALL
  SELECT 'gold_unique_key','gold','indicador_municipio','critical',
         COUNT(*) - COUNT(DISTINCT STRUCT(ano,id_municipio,serie,rede)), '= 0'
  FROM `__PROJECT_ID__.alfabetizacao_gold.indicador_municipio`
  UNION ALL
  SELECT 'gold_enrichment','gold','indicador_municipio','critical',
         COUNTIF(nome_municipio IS NULL OR sigla_uf IS NULL), '= 0'
  FROM `__PROJECT_ID__.alfabetizacao_gold.indicador_municipio`
)
SELECT check_name, layer, table_name, severity, observed=0 AS passed,
       observed, expectation, CURRENT_TIMESTAMP()
FROM checks;

ASSERT (
  SELECT COUNTIF(NOT passed AND severity='critical')
  FROM `__PROJECT_ID__.alfabetizacao_monitoring.quality_results`
  WHERE DATE(checked_at)=CURRENT_DATE()
) = 0 AS 'Falha critica nas regras de qualidade da alfabetizacao';

