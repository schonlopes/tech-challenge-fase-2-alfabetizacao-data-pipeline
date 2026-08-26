"""Regras de qualidade, evidencias e score do pipeline."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .contracts import CONTRACTS, LEVEL_COLUMNS, LITERACY_CUTOFF
from .duck import connect, parquet_glob
from .paths import ProjectPaths


@dataclass(frozen=True)
class CheckResult:
    name: str
    layer: str
    table: str
    severity: str
    passed: bool
    observed: int | float | str
    expectation: str


def _scalar(con, query: str):
    return con.execute(query).fetchone()[0]


def run_quality(paths: ProjectPaths, run_id: str) -> dict[str, object]:
    con = connect()
    checks: list[CheckResult] = []
    try:
        for name in (*CONTRACTS.keys(), "dim_municipio"):
            con.execute(
                f"CREATE VIEW s_{name} AS SELECT * FROM "
                f"read_parquet('{parquet_glob(paths.silver / name)}', hive_partitioning=true, union_by_name=true)"
            )
        for name in (
            "indicador_municipio",
            "meta_resultado_municipio",
            "evolucao_municipio",
            "resumo_uf",
            "monitoramento_stream",
        ):
            con.execute(
                f"CREATE VIEW g_{name} AS SELECT * FROM "
                f"read_parquet('{parquet_glob(paths.gold / name)}', hive_partitioning=true, union_by_name=true)"
            )

        for name, contract in CONTRACTS.items():
            count = _scalar(con, f"SELECT COUNT(*) FROM s_{name}")
            checks.append(CheckResult("row_count", "silver", name, "critical", count > 0, count, "> 0"))

            null_predicate = " OR ".join(
                f"{column} IS NULL OR TRIM(CAST({column} AS VARCHAR)) = ''" for column in contract.key
            )
            nulls = _scalar(con, f"SELECT COUNT(*) FROM s_{name} WHERE {null_predicate}")
            checks.append(CheckResult("not_null_key", "silver", name, "critical", nulls == 0, nulls, "= 0"))

            keys = ", ".join(contract.key)
            duplicates = _scalar(
                con,
                f"SELECT COALESCE(SUM(n - 1), 0) FROM (SELECT COUNT(*) AS n FROM s_{name} GROUP BY {keys} HAVING n > 1)",
            )
            checks.append(CheckResult("unique_key", "silver", name, "critical", duplicates == 0, duplicates, "= 0"))

        for name in (
            "uf",
            "meta_alfabetizacao_brasil",
            "meta_alfabetizacao_uf",
            "meta_alfabetizacao_municipio",
            "municipio",
        ):
            invalid = _scalar(
                con,
                f"SELECT COUNT(*) FROM s_{name} WHERE taxa_alfabetizacao NOT BETWEEN 0 AND 100",
            )
            checks.append(CheckResult("taxa_range", "silver", name, "critical", invalid == 0, invalid, "0 <= taxa <= 100"))

        for name in ("uf", "municipio"):
            level_sum = " + ".join(f"COALESCE({column}, 0)" for column in LEVEL_COLUMNS)
            invalid = _scalar(con, f"SELECT COUNT(*) FROM s_{name} WHERE ABS(({level_sum}) - 100) > 0.5")
            checks.append(CheckResult("level_distribution_sum", "silver", name, "warning", invalid == 0, invalid, "soma = 100 +/- 0.5"))

        for name in ("meta_alfabetizacao_brasil", "meta_alfabetizacao_uf", "meta_alfabetizacao_municipio"):
            invalid = _scalar(
                con,
                f"SELECT COUNT(*) FROM s_{name} WHERE percentual_participacao NOT BETWEEN 0 AND 100",
            )
            checks.append(CheckResult("participacao_range", "silver", name, "critical", invalid == 0, invalid, "0 <= percentual <= 100"))

        for name in ("municipio", "meta_alfabetizacao_municipio", "alunos"):
            orphan = _scalar(
                con,
                f"""
                SELECT COUNT(*) FROM s_{name} f
                LEFT JOIN s_dim_municipio d USING (id_municipio)
                WHERE d.id_municipio IS NULL
                """,
            )
            checks.append(CheckResult("municipality_fk", "silver", name, "critical", orphan == 0, orphan, "= 0 orfaos"))

        inconsistent_students = _scalar(
            con,
            f"""
            SELECT COUNT(*) FROM s_alunos
            WHERE presenca = 'Presente' AND proficiencia IS NOT NULL
              AND ((proficiencia >= {LITERACY_CUTOFF} AND alfabetizado <> 'Sim')
                OR (proficiencia < {LITERACY_CUTOFF} AND alfabetizado <> 'Nao'))
            """,
        )
        checks.append(
            CheckResult(
                "literacy_cutoff_consistency",
                "silver",
                "alunos",
                "critical",
                inconsistent_students == 0,
                inconsistent_students,
                f"alfabetizado equivale a proficiencia >= {LITERACY_CUTOFF:g}",
            )
        )

        inconsistent_rates = _scalar(
            con,
            """
            SELECT COUNT(*)
            FROM s_municipio r
            JOIN s_meta_alfabetizacao_municipio m
              ON r.ano=m.ano AND r.id_municipio=m.id_municipio AND r.rede=m.rede
            WHERE ABS(r.taxa_alfabetizacao - m.taxa_alfabetizacao) > 0.01
            """,
        )
        checks.append(CheckResult("cross_table_rate", "silver", "municipio", "critical", inconsistent_rates == 0, inconsistent_rates, "taxas agregadas coincidem"))

        gold_duplicates = _scalar(
            con,
            """
            SELECT COALESCE(SUM(n - 1), 0)
            FROM (
                SELECT COUNT(*) n FROM g_indicador_municipio
                GROUP BY ano, id_municipio, serie, rede HAVING n > 1
            )
            """,
        )
        checks.append(CheckResult("gold_grain", "gold", "indicador_municipio", "critical", gold_duplicates == 0, gold_duplicates, "= 0 duplicatas"))

        missing_enrichment = _scalar(
            con,
            "SELECT COUNT(*) FROM g_indicador_municipio WHERE nome_municipio IS NULL OR sigla_uf IS NULL",
        )
        checks.append(CheckResult("enrichment_complete", "gold", "indicador_municipio", "critical", missing_enrichment == 0, missing_enrichment, "= 0 sem diretorio municipal"))

        total = len(checks)
        passed = sum(1 for check in checks if check.passed)
        critical_failures = sum(1 for check in checks if not check.passed and check.severity == "critical")
        warnings = sum(1 for check in checks if not check.passed and check.severity == "warning")
        status = "FAIL" if critical_failures else ("WARN" if warnings else "PASS")
        report = {
            "run_id": run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "score_pct": round(100.0 * passed / total, 2),
            "summary": {
                "checks": total,
                "passed": passed,
                "critical_failures": critical_failures,
                "warnings": warnings,
            },
            "checks": [asdict(check) for check in checks],
        }
    finally:
        con.close()

    paths.evidence.mkdir(parents=True, exist_ok=True)
    report_path = paths.evidence / f"quality_{run_id}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (paths.evidence / "latest_quality.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report

