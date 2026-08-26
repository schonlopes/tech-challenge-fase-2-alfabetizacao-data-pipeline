"""Ingestao batch para a camada Bronze append-only."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .contracts import CONTRACTS
from .duck import connect, copy_partitioned, sql_path
from .paths import ProjectPaths


SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9_.-]+$")


def new_run_id(prefix: str = "batch") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{stamp}"


def ingest_csv_snapshot(
    paths: ProjectPaths,
    source_dir: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, int]:
    """Copia as seis entidades para Bronze com metadados de rastreabilidade."""
    paths.ensure()
    source = Path(source_dir or paths.sample).resolve()
    run_id = run_id or new_run_id()
    if not SAFE_RUN_ID.match(run_id):
        raise ValueError("run_id deve conter apenas letras, numeros, ponto, hifen ou sublinhado.")

    con = connect()
    counts: dict[str, int] = {}
    ingested_at = datetime.now(timezone.utc).isoformat()

    try:
        for name, contract in CONTRACTS.items():
            csv_path = source / f"{name}.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"Fonte obrigatoria ausente: {csv_path}")

            view = f"raw_{name}"
            con.execute(
                f"CREATE OR REPLACE TEMP VIEW {view} AS "
                f"SELECT * FROM read_csv_auto('{sql_path(csv_path)}', "
                "header=true, all_varchar=true, normalize_names=false)"
            )
            actual = {row[1] for row in con.execute(f"PRAGMA table_info('{view}')").fetchall()}
            missing = sorted(set(contract.fields) - actual)
            if missing:
                raise ValueError(f"{name}: colunas obrigatorias ausentes: {missing}")

            fields = ", ".join(f'"{field}"' for field in contract.fields if field != "ano")
            query = f"""
                SELECT
                    TRY_CAST(ano AS INTEGER) AS ano,
                    {fields},
                    '{ingested_at}'::TIMESTAMPTZ AS _ingested_at,
                    '{run_id}' AS _run_id,
                    'csv:{sql_path(csv_path)}' AS _source
                FROM {view}
            """
            destination = paths.bronze / name / f"run_id={run_id}"
            copy_partitioned(con, query, destination, ("ano",))
            counts[name] = con.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
    finally:
        con.close()

    return counts

