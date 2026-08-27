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


def _append_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


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
    """Consome bytes novos; eventos inválidos são enviados à DLQ local auditável."""
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
    required = set(CONTRACTS["alunos"].fields) | {"event_id", "event_ts", "event_date"}
    events: list[dict[str, object]] = []
    dead_letters: list[dict[str, object]] = []
    for index, line in enumerate(lines, 1):
        raw = line.decode("utf-8", errors="replace")
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            dead_letters.append({
                "run_id": run_id,
                "line_number": index,
                "reason": "invalid_json",
                "detail": exc.msg,
                "payload": raw,
                "received_at": _utc_now().isoformat(),
            })
            continue
        if not isinstance(event, dict):
            dead_letters.append({
                "run_id": run_id,
                "line_number": index,
                "reason": "invalid_payload_type",
                "detail": "O evento deve ser um objeto JSON.",
                "payload": raw,
                "received_at": _utc_now().isoformat(),
            })
            continue
        missing = sorted(required - event.keys())
        if missing:
            dead_letters.append({
                "run_id": run_id,
                "line_number": index,
                "reason": "missing_required_fields",
                "detail": ", ".join(missing),
                "payload": event,
                "received_at": _utc_now().isoformat(),
            })
            continue
        events.append(event)

    if dead_letters:
        _append_jsonl(paths.stream_dlq, dead_letters)
    if not events:
        paths.stream_checkpoint.write_text(str(new_offset), encoding="utf-8")
        return 0

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


def validate_local_dlq(paths: ProjectPaths, run_id: str) -> dict[str, object]:
    """Publica um evento controladamente inválido e comprova seu envio à DLQ local."""
    paths.ensure()
    event = build_events(paths.sample / "alunos.csv", 1)[0]
    event.pop("event_id")
    _append_jsonl(paths.stream_inbox, [event])
    accepted = consume_local(paths, run_id)

    records = [
        json.loads(line)
        for line in paths.stream_dlq.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    matches = [record for record in records if record["run_id"] == run_id]
    result = {
        "run_id": run_id,
        "status": "PASS" if accepted == 0 and len(matches) == 1 else "FAIL",
        "accepted_events": accepted,
        "dlq_events": len(matches),
        "reason": matches[0]["reason"] if matches else None,
        "evidence_path": str(paths.stream_dlq),
        "validated_at": _utc_now().isoformat(),
        "scope": "Simulação local equivalente ao encaminhamento para DLQ; não substitui a confirmação no Pub/Sub em produção.",
    }
    (paths.evidence / "dlq_validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result
