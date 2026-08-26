"""Orquestracao local ponta a ponta e geracao de evidencias."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .batch import ingest_csv_snapshot, new_run_id
from .bigquery_source import extract_snapshot
from .gold import build_gold
from .paths import ProjectPaths
from .quality import run_quality
from .sample_data import generate_sample_data
from .silver import build_silver
from .streaming import consume_local, simulate_local


def _layer_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.glob("**/*") if item.is_file())


def run_all(
    paths: ProjectPaths,
    source: str = "sample",
    source_dir: str | Path | None = None,
    billing_project: str | None = None,
    student_limit: int = 0,
    stream_events: int = 24,
    run_id: str | None = None,
) -> dict[str, object]:
    run_id = run_id or new_run_id("run")
    paths.ensure()
    started_at = datetime.now(timezone.utc)
    timings: dict[str, float] = {}

    if source == "sample":
        actual_source = Path(source_dir or paths.sample)
        if not all((actual_source / f"{name}.csv").exists() for name in (
            "uf", "meta_alfabetizacao_brasil", "meta_alfabetizacao_uf",
            "meta_alfabetizacao_municipio", "municipio", "alunos",
        )):
            generate_sample_data(actual_source)
    elif source == "bigquery":
        if not billing_project:
            raise ValueError("--billing-project e obrigatorio para source=bigquery.")
        actual_source = paths.staging / run_id
        t0 = time.perf_counter()
        extract_snapshot(billing_project, actual_source, student_limit=student_limit)
        timings["extract_bigquery_seconds"] = round(time.perf_counter() - t0, 3)
        reference = paths.sample / "municipios_referencia.csv"
        if not reference.exists():
            generate_sample_data(paths.sample)
    else:
        raise ValueError(f"Fonte desconhecida: {source}")

    t0 = time.perf_counter()
    bronze_counts = ingest_csv_snapshot(paths, actual_source, run_id)
    timings["batch_bronze_seconds"] = round(time.perf_counter() - t0, 3)

    stream_count = 0
    if stream_events > 0:
        t0 = time.perf_counter()
        simulate_local(paths, stream_events, actual_source / "alunos.csv")
        stream_count = consume_local(paths, run_id)
        timings["stream_microbatch_seconds"] = round(time.perf_counter() - t0, 3)

    t0 = time.perf_counter()
    silver_counts = build_silver(paths)
    timings["silver_seconds"] = round(time.perf_counter() - t0, 3)

    t0 = time.perf_counter()
    gold_counts = build_gold(paths)
    timings["gold_seconds"] = round(time.perf_counter() - t0, 3)

    t0 = time.perf_counter()
    quality = run_quality(paths, run_id)
    timings["quality_seconds"] = round(time.perf_counter() - t0, 3)
    timings["total_seconds"] = round((datetime.now(timezone.utc) - started_at).total_seconds(), 3)

    manifest = {
        "run_id": run_id,
        "source": source,
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "status": quality["status"],
        "quality_score_pct": quality["score_pct"],
        "row_counts": {
            "bronze_batch": bronze_counts,
            "bronze_stream": stream_count,
            "silver": silver_counts,
            "gold": gold_counts,
        },
        "storage_bytes": {
            "bronze": _layer_bytes(paths.bronze),
            "bronze_stream": _layer_bytes(paths.bronze_stream),
            "silver": _layer_bytes(paths.silver),
            "gold": _layer_bytes(paths.gold),
        },
        "timings": timings,
    }
    manifest_path = paths.evidence / f"run_{run_id}.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (paths.evidence / "latest_run.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if quality["status"] == "FAIL":
        raise RuntimeError(f"Pipeline interrompido por falha critica de qualidade. Veja {manifest_path}")
    return manifest

