CREATE TABLE IF NOT EXISTS `__PROJECT_ID__.alfabetizacao_bronze.alunos`
PARTITION BY DATE(_ingested_at)
CLUSTER BY ano, id_municipio, rede
OPTIONS(description='Snapshots historicos dos microdados pseudonimizados') AS
SELECT *, CURRENT_TIMESTAMP() AS _ingested_at,
       'basedosdados.br_inep_avaliacao_alfabetizacao.alunos' AS _source
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.alunos`
WHERE FALSE;

DELETE FROM `__PROJECT_ID__.alfabetizacao_bronze.alunos`
WHERE DATE(_ingested_at) = CURRENT_DATE();

INSERT INTO `__PROJECT_ID__.alfabetizacao_bronze.alunos`
SELECT *, CURRENT_TIMESTAMP(),
       'basedosdados.br_inep_avaliacao_alfabetizacao.alunos'
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.alunos`
WHERE ano BETWEEN 2023 AND 2030;

