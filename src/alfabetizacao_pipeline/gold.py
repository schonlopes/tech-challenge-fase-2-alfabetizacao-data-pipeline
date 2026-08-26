"""Modelos analiticos da camada Gold."""

from __future__ import annotations

from .duck import connect, copy_partitioned, parquet_glob, sql_path
from .paths import ProjectPaths


def build_gold(paths: ProjectPaths) -> dict[str, int]:
    paths.ensure()
    paths.replace_derived_layer("gold")
    con = connect()
    counts: dict[str, int] = {}
    try:
        for name in (
            "uf",
            "meta_alfabetizacao_uf",
            "meta_alfabetizacao_municipio",
            "municipio",
            "alunos",
        ):
            con.execute(
                f"CREATE VIEW s_{name} AS SELECT * FROM "
                f"read_parquet('{parquet_glob(paths.silver / name)}', hive_partitioning=true, union_by_name=true)"
            )
        con.execute(
            f"CREATE VIEW dim_municipio AS SELECT * FROM "
            f"read_parquet('{parquet_glob(paths.silver / 'dim_municipio')}', union_by_name=true)"
        )

        queries = {
            "indicador_municipio": """
                WITH enriched AS (
                    SELECT
                        m.ano, m.id_municipio, d.nome_municipio, d.sigla_uf,
                        d.nome_uf, d.regiao, m.serie, m.rede,
                        m.taxa_alfabetizacao, m.media_portugues,
                        CASE m.ano
                            WHEN 2024 THEN mm.meta_alfabetizacao_2024
                            WHEN 2025 THEN mm.meta_alfabetizacao_2025
                            WHEN 2026 THEN mm.meta_alfabetizacao_2026
                            WHEN 2027 THEN mm.meta_alfabetizacao_2027
                            WHEN 2028 THEN mm.meta_alfabetizacao_2028
                            WHEN 2029 THEN mm.meta_alfabetizacao_2029
                            WHEN 2030 THEN mm.meta_alfabetizacao_2030
                        END AS meta_ano,
                        mm.nivel_alfabetizacao,
                        mm.percentual_participacao
                    FROM s_municipio m
                    LEFT JOIN s_meta_alfabetizacao_municipio mm
                      ON m.ano = mm.ano
                     AND m.id_municipio = mm.id_municipio
                     AND m.rede = mm.rede
                    LEFT JOIN dim_municipio d
                      ON m.id_municipio = d.id_municipio
                )
                SELECT *,
                       ROUND(taxa_alfabetizacao - meta_ano, 2) AS gap_meta_pp,
                       CASE
                           WHEN meta_ano IS NULL THEN 'SEM_META'
                           WHEN taxa_alfabetizacao >= meta_ano THEN 'ATINGIDA'
                           WHEN taxa_alfabetizacao >= meta_ano - 3 THEN 'ATENCAO'
                           ELSE 'CRITICO'
                       END AS status_meta,
                       current_timestamp AS _gold_processed_at
                FROM enriched
            """,
            "meta_resultado_municipio": """
                WITH latest_meta AS (
                    SELECT * EXCLUDE (rn)
                    FROM (
                        SELECT *, ROW_NUMBER() OVER (
                            PARTITION BY id_municipio, rede ORDER BY ano DESC
                        ) AS rn
                        FROM s_meta_alfabetizacao_municipio
                    )
                    WHERE rn = 1
                ), targets AS (
                    SELECT id_municipio, rede, 2024 AS ano_meta, meta_alfabetizacao_2024 AS meta FROM latest_meta
                    UNION ALL SELECT id_municipio, rede, 2025, meta_alfabetizacao_2025 FROM latest_meta
                    UNION ALL SELECT id_municipio, rede, 2026, meta_alfabetizacao_2026 FROM latest_meta
                    UNION ALL SELECT id_municipio, rede, 2027, meta_alfabetizacao_2027 FROM latest_meta
                    UNION ALL SELECT id_municipio, rede, 2028, meta_alfabetizacao_2028 FROM latest_meta
                    UNION ALL SELECT id_municipio, rede, 2029, meta_alfabetizacao_2029 FROM latest_meta
                    UNION ALL SELECT id_municipio, rede, 2030, meta_alfabetizacao_2030 FROM latest_meta
                )
                SELECT
                    t.ano_meta, t.id_municipio, d.nome_municipio, d.sigla_uf,
                    d.regiao, t.rede, t.meta,
                    r.taxa_alfabetizacao AS resultado,
                    ROUND(r.taxa_alfabetizacao - t.meta, 2) AS gap_meta_pp,
                    CASE
                        WHEN r.taxa_alfabetizacao IS NULL THEN 'AGUARDANDO_RESULTADO'
                        WHEN r.taxa_alfabetizacao >= t.meta THEN 'ATINGIDA'
                        WHEN r.taxa_alfabetizacao >= t.meta - 3 THEN 'ATENCAO'
                        ELSE 'CRITICO'
                    END AS status_meta,
                    current_timestamp AS _gold_processed_at
                FROM targets t
                LEFT JOIN s_municipio r
                  ON r.ano = t.ano_meta
                 AND r.id_municipio = t.id_municipio
                 AND r.rede = t.rede
                LEFT JOIN dim_municipio d
                  ON t.id_municipio = d.id_municipio
            """,
            "evolucao_municipio": """
                SELECT
                    m.ano, m.id_municipio, d.nome_municipio, d.sigla_uf,
                    d.regiao, m.rede, m.taxa_alfabetizacao,
                    LAG(m.taxa_alfabetizacao) OVER (
                        PARTITION BY m.id_municipio, m.rede ORDER BY m.ano
                    ) AS taxa_ano_anterior,
                    ROUND(m.taxa_alfabetizacao - LAG(m.taxa_alfabetizacao) OVER (
                        PARTITION BY m.id_municipio, m.rede ORDER BY m.ano
                    ), 2) AS variacao_anual_pp,
                    current_timestamp AS _gold_processed_at
                FROM s_municipio m
                LEFT JOIN dim_municipio d USING (id_municipio)
            """,
            "resumo_uf": """
                SELECT
                    u.ano, u.sigla_uf, u.rede, u.taxa_alfabetizacao,
                    u.media_portugues, mu.percentual_participacao,
                    CASE u.ano WHEN 2024 THEN mu.meta_alfabetizacao_2024 END AS meta_ano,
                    ROUND(u.taxa_alfabetizacao -
                        CASE u.ano WHEN 2024 THEN mu.meta_alfabetizacao_2024 END, 2
                    ) AS gap_meta_pp,
                    current_timestamp AS _gold_processed_at
                FROM s_uf u
                LEFT JOIN s_meta_alfabetizacao_uf mu
                  ON u.ano = mu.ano AND u.sigla_uf = mu.sigla_uf AND u.rede = mu.rede
            """,
            "monitoramento_stream": """
                SELECT
                    a.ano, a.id_municipio, d.nome_municipio, d.sigla_uf, a.rede,
                    COUNT(*) AS alunos_recebidos,
                    COUNT(*) FILTER (WHERE a.presenca = 'Presente') AS alunos_presentes,
                    ROUND(100.0 * COUNT(*) FILTER (WHERE a.alfabetizado = 'Sim') /
                          NULLIF(COUNT(*) FILTER (WHERE a.presenca = 'Presente'), 0), 2
                    ) AS taxa_alfabetizacao_amostra,
                    ROUND(AVG(a.proficiencia) FILTER (WHERE a.presenca = 'Presente'), 2) AS media_proficiencia,
                    MAX(a.event_ts) AS ultimo_evento,
                    current_timestamp AS _gold_processed_at
                FROM s_alunos a
                LEFT JOIN dim_municipio d USING (id_municipio)
                GROUP BY a.ano, a.id_municipio, d.nome_municipio, d.sigla_uf, a.rede
            """,
        }

        partition_by = {
            "indicador_municipio": ("ano",),
            "meta_resultado_municipio": ("ano_meta",),
            "evolucao_municipio": ("ano",),
            "resumo_uf": ("ano",),
            "monitoramento_stream": ("ano",),
        }
        for name, query in queries.items():
            copy_partitioned(con, query, paths.gold / name, partition_by[name])
            counts[name] = con.execute(f"SELECT COUNT(*) FROM ({query})").fetchone()[0]

        preview = paths.evidence / "gold_indicador_municipio.csv"
        preview.parent.mkdir(parents=True, exist_ok=True)
        preview.unlink(missing_ok=True)
        con.execute(
            f"COPY (SELECT * FROM ({queries['indicador_municipio']}) ORDER BY ano, sigla_uf, nome_municipio) "
            f"TO '{sql_path(preview)}' (FORMAT CSV, HEADER TRUE)"
        )
    finally:
        con.close()
    return counts
