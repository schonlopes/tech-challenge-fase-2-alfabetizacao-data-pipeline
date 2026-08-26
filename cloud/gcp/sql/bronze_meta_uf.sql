CREATE TABLE IF NOT EXISTS `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_uf`
PARTITION BY DATE(_ingested_at)
CLUSTER BY ano, sigla_uf, rede
OPTIONS(description='Snapshots historicos das metas por UF') AS
SELECT *, CURRENT_TIMESTAMP() AS _ingested_at,
       'basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_uf' AS _source
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_uf`
WHERE FALSE;

DELETE FROM `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_uf`
WHERE DATE(_ingested_at) = CURRENT_DATE();

INSERT INTO `__PROJECT_ID__.alfabetizacao_bronze.meta_alfabetizacao_uf`
SELECT *, CURRENT_TIMESTAMP(),
       'basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_uf'
FROM `basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_uf`
WHERE ano BETWEEN 2023 AND 2030;

