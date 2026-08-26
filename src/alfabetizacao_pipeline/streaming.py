"""Simulador/consumidor de streaming local e publicador opcional no Pub/Sub."""

from __future__ import annotations

import csv
import json
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .contracts import CONTRACTS
from .duck import connect, copy_partitioned, sql_path
from .paths import ProjectPaths


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_events(sample_csv: str | Path, count: int) -> list[dict[str, object]]:
    with Path(sample_csv).open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Nao ha alunos na amostra para simular eventos.")

    started = _utc_now()
    events: list[dict[str, object]] = []
    for index in range(count):
        row = dict(rows[index % len(rows)])
        event_time = started + timedelta(seconds=index)
        row["ano"] = int(row["ano"])
        row["proficiencia"] = float(row["proficiencia"]) if row["proficiencia"] else None
        row["peso_aluno"] = float(row["peso_aluno"]) if row["peso_aluno"] else None
        row["event_id"] = str(uuid.uuid4())
        row["event_ts"] = event_time.isoformat()
        row["event_date"] = event_time.date().isoformat()
        events.append(row)
    return events


def simulate_local(paths: ProjectPaths, count: int = 24, source_csv: str | Path | None = None) -> int:
    paths.ensure()
    events = build_events(source_csv or paths.sample / "alunos.csv", count)
    with paths.stream_inbox.open("a", encoding="utf-8", newline="\n") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    return len(events)


def publish_pubsub(
    paths: ProjectPaths,
    project_id: str,
    topic_id: str,
    count: int = 24,
    source_csv: str | Path | None = None,
) -> int:
    try:
        from google.cloud import pubsub_v1
    except ImportError as exc:  # pragma: no cover - depende de credencial/extra cloud
        raise RuntimeError("Instale o extra cloud: pip install -e .[cloud]") from exc

    events = build_events(source_csv or paths.sample / "alunos.csv", count)
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    futures = [
        publisher.publish(
            topic_path,
            json.dumps(event, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
            event_type="aluno_avaliado",
        )
        for event in events
    ]
    for future in futures:
        future.result(timeout=30)
    return len(futures)


def consume_local(paths: ProjectPaths, run_id: str) -> int:
    """Consome apenas bytes novos do JSONL e persiste microbatch imutavel na Bronze."""
    paths.ensure()
    if not paths.stream_inbox.exists():
        return 0
    offset = int(paths.stream_checkpoint.read_text(encoding="utf-8")) if paths.stream_checkpoint.exists() else 0

    with paths.stream_inbox.open("rb") as handle:
        handle.seek(offset)
        payload = handle.read()
        new_offset = handle.tell()
    if not payload:
        return 0

    lines = [line for line in payload.splitlines() if line.strip()]
    events = [json.loads(line.decode("utf-8")) for line in lines]
    required = set(CONTRACTS["alunos"].fields) | {"event_id", "event_ts", "event_date"}
    for index, event in enumerate(events, 1):
        missing = sorted(required - event.keys())
        if missing:
            raise ValueError(f"Evento {index} invalido; campos ausentes: {missing}")

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".jsonl", delete=False) as temp:
        temp_path = Path(temp.name)
        for event in events:
            temp.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")

    con = connect()
    try:
        con.execute(
            f"CREATE TEMP VIEW events AS SELECT * FROM read_json_auto('{sql_path(temp_path)}', format='newline_delimited')"
        )
        duplicate_count = con.execute(
            "SELECT COUNT(*) - COUNT(DISTINCT event_id) FROM events"
        ).fetchone()[0]
        if duplicate_count:
            raise ValueError(f"Microbatch contem {duplicate_count} event_id duplicado(s).")
        destination = paths.bronze_stream / "alunos" / f"run_id={run_id}"
        copy_partitioned(
            con,
            """
            SELECT *,
                   current_timestamp AS _ingested_at,
                   'pubsub-simulado' AS _source
            FROM events
            """,
            destination,
            ("event_date", "ano"),
        )
    finally:
        con.close()
        temp_path.unlink(missing_ok=True)

    paths.stream_checkpoint.write_text(str(new_offset), encoding="utf-8")
    return len(events)
