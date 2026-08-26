CREATE TABLE IF NOT EXISTS `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_brasil`
PARTITION BY DATE(_ingested_at)
CLUSTER BY ano, rede
OPTIONS(description='Snapshots historicos das metas nacionais') AS
SELECT *, CURRENT_TIMESTAMP() AS _ingested_at,
       'basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_brasil' AS _source
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_brasil`
WHERE FALSE;

DELETE FROM `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_brasil`
WHERE DATE(_ingested_at) = CURRENT_DATE();

INSERT INTO `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_brasil`
SELECT *, CURRENT_TIMESTAMP(),
       'basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_brasil'
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_brasil`
WHERE ano BETWEEN 2023 AND 2030;

