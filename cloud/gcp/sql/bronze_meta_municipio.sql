CREATE TABLE IF NOT EXISTS `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_municipio`
PARTITION BY DATE(_ingested_at)
CLUSTER BY ano, id_municipio, rede
OPTIONS(description='Snapshots historicos das metas por municipio') AS
SELECT *, CURRENT_TIMESTAMP() AS _ingested_at,
       'basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio' AS _source
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio`
WHERE FALSE;

DELETE FROM `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_municipio`
WHERE DATE(_ingested_at) = CURRENT_DATE();

INSERT INTO `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_municipio`
SELECT *, CURRENT_TIMESTAMP(),
       'basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio'
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio`
WHERE ano BETWEEN 2023 AND 2030;

