CREATE TABLE IF NOT EXISTS `__PROJECT_ID__.alfabetizacao_bronze.uf`
PARTITION BY DATE(_ingested_at)
CLUSTER BY ano, sigla_uf, rede
OPTIONS(description='Snapshots historicos da tabela oficial UF') AS
SELECT *, CURRENT_TIMESTAMP() AS _ingested_at,
       'basedosdados.br_inep_avaliacao_alfabetizacao.uf' AS _source
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.uf`
WHERE FALSE;

DELETE FROM `__PROJECT_ID__.alfabetizacao_bronze.uf`
WHERE DATE(_ingested_at) = CURRENT_DATE();

INSERT INTO `__PROJECT_ID__.alfabetizacao_bronze.uf`
SELECT *, CURRENT_TIMESTAMP(),
       'basedosdados.br_inep_avaliacao_alfabetizacao.uf'
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.uf`
WHERE ano BETWEEN 2023 AND 2030;

