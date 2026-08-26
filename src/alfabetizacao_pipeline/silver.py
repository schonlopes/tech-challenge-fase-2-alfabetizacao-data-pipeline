"""Tratamento, tipagem, deduplicacao e integracao da camada Silver."""

from __future__ import annotations

from pathlib import Path

from .contracts import LEVEL_COLUMNS, TARGET_COLUMNS
from .duck import connect, copy_partitioned, copy_single, parquet_glob, sql_path
from .paths import ProjectPaths


def _raw_view(con, name: str, path: Path) -> None:
    con.execute(
        f"CREATE OR REPLACE VIEW raw_{name} AS "
        f"SELECT * FROM read_parquet('{parquet_glob(path)}', hive_partitioning=true, union_by_name=true)"
    )


def _latest(key: tuple[str, ...]) -> str:
    partition = ", ".join(key)
    return f"QUALIFY ROW_NUMBER() OVER (PARTITION BY {partition} ORDER BY _ingested_at DESC, _run_id DESC) = 1"


def _target_casts() -> str:
    return ",\n".join(f"num({column}) AS {column}" for column in TARGET_COLUMNS)


def _level_casts() -> str:
    return ",\n".join(f"num({column}) AS {column}" for column in LEVEL_COLUMNS)


def build_silver(paths: ProjectPaths) -> dict[str, int]:
    paths.ensure()
    paths.replace_derived_layer("silver")
    con = connect()
    counts: dict[str, int] = {}
    try:
        con.execute(
            "CREATE OR REPLACE MACRO num(x) AS "
            "TRY_CAST(REPLACE(TRIM(CAST(x AS VARCHAR)), ',', '.') AS DOUBLE)"
        )
        for name in (
            "uf",
            "meta_alfabetizacao_brasil",
            "meta_alfabetizacao_uf",
            "meta_alfabetizacao_municipio",
            "municipio",
            "alunos",
        ):
            _raw_view(con, name, paths.bronze / name)

        levels = _level_casts()
        targets = _target_casts()
        queries: dict[str, str] = {
            "uf": f"""
                SELECT
                    CAST(ano AS INTEGER) AS ano,
                    UPPER(TRIM(sigla_uf)) AS sigla_uf,
                    TRIM(serie) AS serie,
                    TRIM(rede) AS rede,
                    num(taxa_alfabetizacao) AS taxa_alfabetizacao,
                    num(media_portugues) AS media_portugues,
                    {levels},
                    _ingested_at, _run_id, _source,
                    current_timestamp AS _processed_at
                FROM raw_uf
                {_latest(("ano", "sigla_uf", "serie", "rede"))}
            """,
            "meta_alfabetizacao_brasil": f"""
                SELECT
                    CAST(ano AS INTEGER) AS ano,
                    TRIM(rede) AS rede,
                    num(taxa_alfabetizacao) AS taxa_alfabetizacao,
                    {targets},
                    num(percentual_participacao) AS percentual_participacao,
                    _ingested_at, _run_id, _source,
                    current_timestamp AS _processed_at
                FROM raw_meta_alfabetizacao_brasil
                {_latest(("ano", "rede"))}
            """,
            "meta_alfabetizacao_uf": f"""
                SELECT
                    CAST(ano AS INTEGER) AS ano,
                    UPPER(TRIM(sigla_uf)) AS sigla_uf,
                    TRIM(rede) AS rede,
                    num(taxa_alfabetizacao) AS taxa_alfabetizacao,
                    {targets},
                    num(percentual_participacao) AS percentual_participacao,
                    _ingested_at, _run_id, _source,
                    current_timestamp AS _processed_at
                FROM raw_meta_alfabetizacao_uf
                {_latest(("ano", "sigla_uf", "rede"))}
            """,
            "meta_alfabetizacao_municipio": f"""
                SELECT
                    CAST(ano AS INTEGER) AS ano,
                    LPAD(TRIM(id_municipio), 7, '0') AS id_municipio,
                    TRIM(rede) AS rede,
                    num(taxa_alfabetizacao) AS taxa_alfabetizacao,
                    {targets},
                    TRY_CAST(nivel_alfabetizacao AS INTEGER) AS nivel_alfabetizacao,
                    num(percentual_participacao) AS percentual_participacao,
                    _ingested_at, _run_id, _source,
                    current_timestamp AS _processed_at
                FROM raw_meta_alfabetizacao_municipio
                {_latest(("ano", "id_municipio", "rede"))}
            """,
            "municipio": f"""
                SELECT
                    CAST(ano AS INTEGER) AS ano,
                    LPAD(TRIM(id_municipio), 7, '0') AS id_municipio,
                    TRIM(serie) AS serie,
                    TRIM(rede) AS rede,
                    num(taxa_alfabetizacao) AS taxa_alfabetizacao,
                    num(media_portugues) AS media_portugues,
                    {levels},
                    _ingested_at, _run_id, _source,
                    current_timestamp AS _processed_at
                FROM raw_municipio
                {_latest(("ano", "id_municipio", "serie", "rede"))}
            """,
        }

        stream_files = list((paths.bronze_stream / "alunos").glob("**/*.parquet"))
        if stream_files:
            _raw_view(con, "alunos_stream", paths.bronze_stream / "alunos")
            alunos_source = """
                SELECT
                    ano, id_municipio, id_escola, id_aluno, caderno, serie, rede,
                    presenca, preenchimento_caderno, alfabetizado, proficiencia, peso_aluno,
                    NULL::VARCHAR AS event_id, NULL::TIMESTAMPTZ AS event_ts,
                    _ingested_at, _run_id, _source
                FROM raw_alunos
                UNION ALL BY NAME
                SELECT
                    ano, id_municipio, id_escola, id_aluno, caderno, serie, rede,
                    presenca, preenchimento_caderno, alfabetizado, proficiencia, peso_aluno,
                    CAST(event_id AS VARCHAR), TRY_CAST(event_ts AS TIMESTAMPTZ),
                    _ingested_at, run_id AS _run_id, _source
                FROM raw_alunos_stream
            """
        else:
            alunos_source = """
                SELECT
                    ano, id_municipio, id_escola, id_aluno, caderno, serie, rede,
                    presenca, preenchimento_caderno, alfabetizado, proficiencia, peso_aluno,
                    NULL::VARCHAR AS event_id, NULL::TIMESTAMPTZ AS event_ts,
                    _ingested_at, _run_id, _source
                FROM raw_alunos
            """

        queries["alunos"] = f"""
            WITH unified AS ({alunos_source})
            SELECT
                CAST(ano AS INTEGER) AS ano,
                LPAD(TRIM(id_municipio), 7, '0') AS id_municipio,
                TRIM(id_escola) AS id_escola,
                TRIM(id_aluno) AS id_aluno,
                TRIM(caderno) AS caderno,
                TRIM(serie) AS serie,
                TRIM(rede) AS rede,
                CASE WHEN LOWER(TRIM(presenca)) IN ('presente','sim','1','true')
                     THEN 'Presente' ELSE 'Ausente' END AS presenca,
                CASE WHEN LOWER(TRIM(preenchimento_caderno)) IN ('preenchido','sim','1','true')
                     THEN 'Preenchido' ELSE 'Nao preenchido' END AS preenchimento_caderno,
                CASE WHEN LOWER(TRIM(alfabetizado)) IN ('sim','s','1','true')
                     THEN 'Sim' ELSE 'Nao' END AS alfabetizado,
                num(proficiencia) AS proficiencia,
                num(peso_aluno) AS peso_aluno,
                event_id, event_ts, _ingested_at, _run_id, _source,
                current_timestamp AS _processed_at
            FROM unified
            {_latest(("ano", "id_aluno"))}
        """

        for name, query in queries.items():
            destination = paths.silver / name
            copy_partitioned(con, query, destination, ("ano",))
            counts[name] = con.execute(f"SELECT COUNT(*) FROM ({query})").fetchone()[0]

        reference = paths.sample / "municipios_referencia.csv"
        if not reference.exists():
            raise FileNotFoundError(f"Arquivo de enriquecimento ausente: {reference}")
        reference_query = f"""
            SELECT
                LPAD(TRIM(id_municipio), 7, '0') AS id_municipio,
                TRIM(nome_municipio) AS nome_municipio,
                UPPER(TRIM(sigla_uf)) AS sigla_uf,
                TRIM(nome_uf) AS nome_uf,
                TRIM(regiao) AS regiao,
                current_timestamp AS _processed_at
            FROM read_csv_auto('{sql_path(reference)}', header=true, all_varchar=true)
            QUALIFY ROW_NUMBER() OVER (PARTITION BY id_municipio ORDER BY id_municipio) = 1
        """
        copy_single(con, reference_query, paths.silver / "dim_municipio" / "data.parquet")
        counts["dim_municipio"] = con.execute(f"SELECT COUNT(*) FROM ({reference_query})").fetchone()[0]
    finally:
        con.close()
    return counts

