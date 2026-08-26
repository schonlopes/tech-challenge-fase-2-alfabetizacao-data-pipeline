CREATE OR REPLACE TABLE `__PROJECT_ID__.alfabetizacao_silver.alunos`
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY id_municipio, rede AS
WITH unified AS (
  SELECT
    ano, id_municipio, id_escola, id_aluno, caderno, serie, rede,
    presenca, preenchimento_caderno, alfabetizado, proficiencia, peso_aluno,
    CAST(NULL AS STRING) AS event_id,
    CAST(NULL AS TIMESTAMP) AS event_ts,
    _ingested_at,
    _source
  FROM `__PROJECT_ID__.alfabetizacao_bronze.alunos`
  UNION ALL
  SELECT
    ano, id_municipio, id_escola, id_aluno, caderno, serie, rede,
    presenca, preenchimento_caderno, alfabetizado, proficiencia, peso_aluno,
    event_id, event_ts, event_ts AS _ingested_at, 'pubsub' AS _source
  FROM `__PROJECT_ID__.alfabetizacao_bronze.alunos_stream`
)
SELECT
  CAST(ano AS INT64) AS ano,
  LPAD(TRIM(id_municipio), 7, '0') AS id_municipio,
  TRIM(id_escola) AS id_escola,
  TRIM(id_aluno) AS id_aluno,
  TRIM(caderno) AS caderno,
  TRIM(serie) AS serie,
  TRIM(rede) AS rede,
  CASE WHEN LOWER(TRIM(presenca)) IN ('presente','sim','1','true') THEN 'Presente' ELSE 'Ausente' END AS presenca,
  CASE WHEN LOWER(TRIM(preenchimento_caderno)) IN ('preenchido','sim','1','true') THEN 'Preenchido' ELSE 'Nao preenchido' END AS preenchimento_caderno,
  CASE WHEN LOWER(TRIM(alfabetizado)) IN ('sim','s','1','true') THEN 'Sim' ELSE 'Nao' END AS alfabetizado,
  SAFE_CAST(proficiencia AS FLOAT64) AS proficiencia,
  SAFE_CAST(peso_aluno AS FLOAT64) AS peso_aluno,
  event_id, event_ts, _ingested_at, _source,
  CURRENT_TIMESTAMP() AS _processed_at
FROM unified
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY ano, id_aluno ORDER BY _ingested_at DESC
) = 1;

