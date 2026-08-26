"""Extracao opcional das tabelas reais da Base dos Dados via BigQuery."""

from __future__ import annotations

import csv
from pathlib import Path

from .contracts import CONTRACTS, OFFICIAL_DATASET


def extract_snapshot(
    billing_project: str,
    destination: str | Path,
    year_start: int = 2023,
    year_end: int = 2024,
    student_limit: int = 0,
) -> dict[str, int]:
    """Extrai as seis tabelas usando o projeto GCP informado para faturamento.

    ``student_limit=0`` preserva o conjunto completo. Um limite positivo e util para
    ensaios locais; a implantacao cloud consulta o conjunto integral.
    """
    try:
        from google.cloud import bigquery
    except ImportError as exc:  # pragma: no cover - depende do extra cloud
        raise RuntimeError("Instale o extra cloud: pip install -e .[cloud]") from exc

    if year_start > year_end:
        raise ValueError("year_start nao pode ser maior que year_end.")
    if student_limit < 0:
        raise ValueError("student_limit deve ser zero ou positivo.")

    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    client = bigquery.Client(project=billing_project)
    counts: dict[str, int] = {}

    for name, contract in CONTRACTS.items():
        columns = ", ".join(f"`{field}`" for field in contract.fields)
        limit = f" LIMIT {int(student_limit)}" if name == "alunos" and student_limit else ""
        query = f"""
            SELECT {columns}
            FROM `{OFFICIAL_DATASET}.{name}`
            WHERE ano BETWEEN @year_start AND @year_end
            {limit}
        """
        config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("year_start", "INT64", year_start),
                bigquery.ScalarQueryParameter("year_end", "INT64", year_end),
            ],
            labels={"pipeline": "alfabetizacao", "layer": "source"},
        )
        rows = client.query(query, job_config=config, location="US").result(page_size=10_000)
        output = destination / f"{name}.csv"
        count = 0
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=contract.fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row[field] for field in contract.fields})
                count += 1
        counts[name] = count
    return counts

