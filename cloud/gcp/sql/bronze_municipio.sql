CREATE TABLE IF NOT EXISTS `__PROJECT_ID__.alfabetizacao_bronze.municipio`
PARTITION BY DATE(_ingested_at)
CLUSTER BY ano, id_municipio, rede
OPTIONS(description='Snapshots historicos dos resultados municipais') AS
SELECT *, CURRENT_TIMESTAMP() AS _ingested_at,
       'basedosdados.br_inep_avaliacao_alfabetizacao.municipio' AS _source
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.municipio`
WHERE FALSE;

DELETE FROM `__PROJECT_ID__.alfabetizacao_bronze.municipio`
WHERE DATE(_ingested_at) = CURRENT_DATE();

INSERT INTO `__PROJECT_ID__.alfabetizacao_bronze.municipio`
SELECT *, CURRENT_TIMESTAMP(),
       'basedosdados.br_inep_avaliacao_alfabetizacao.municipio'
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.municipio`
WHERE ano BETWEEN 2023 AND 2030;

