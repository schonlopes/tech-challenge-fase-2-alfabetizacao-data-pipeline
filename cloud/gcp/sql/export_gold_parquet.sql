EXPORT DATA OPTIONS(
  uri='gs://__BUCKET__/gold/indicador_municipio/latest/part-*.parquet',
  format='PARQUET',
  compression='SNAPPY',
  overwrite=true
) AS
SELECT * EXCEPT(_gold_processed_at)
FROM `__PROJECT_ID__.alfabetizacao_gold.indicador_municipio`;

