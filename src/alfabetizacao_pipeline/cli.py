"""Interface de linha de comando do projeto."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .batch import ingest_csv_snapshot, new_run_id
from .bigquery_source import extract_snapshot
from .finops import record_cloud_cost
from .gold import build_gold
from .paths import ProjectPaths
from .pipeline import run_all
from .quality import run_quality
from .sample_data import generate_sample_data
from .silver import build_silver
from .streaming import consume_local, publish_pubsub, simulate_local, validate_local_dlq


def _print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline hibrido da alfabetizacao no Brasil")
    parser.add_argument("--project-root", type=Path, help="Raiz do projeto; detectada automaticamente por padrao")
    sub = parser.add_subparsers(dest="command", required=True)

    sample = sub.add_parser("generate-sample", help="Gera a amostra sintetica local")
    sample.add_argument("--destination", type=Path)

    batch = sub.add_parser("batch", help="Carrega um snapshot CSV na Bronze")
    batch.add_argument("--source-dir", type=Path)
    batch.add_argument("--run-id")

    extract = sub.add_parser("extract-bigquery", help="Extrai o conjunto oficial para CSV")
    extract.add_argument("--billing-project", required=True)
    extract.add_argument("--destination", type=Path)
    extract.add_argument("--student-limit", type=int, default=0)

    simulate = sub.add_parser("simulate-stream", help="Publica eventos locais ou no Pub/Sub")
    simulate.add_argument("--events", type=int, default=24)
    simulate.add_argument("--target", choices=("local", "pubsub"), default="local")
    simulate.add_argument("--gcp-project")
    simulate.add_argument("--topic", default="alfabetizacao-alunos-events")
    simulate.add_argument("--source-csv", type=Path)

    consume = sub.add_parser("consume-stream", help="Consome eventos locais novos para a Bronze")
    consume.add_argument("--run-id")

    dlq = sub.add_parser("validate-local-dlq", help="Valida o encaminhamento local de evento inválido à DLQ")
    dlq.add_argument("--run-id", default="dlq-validation")

    sub.add_parser("silver", help="Reconstroi a camada Silver")
    sub.add_parser("gold", help="Reconstroi a camada Gold")

    quality = sub.add_parser("quality", help="Executa as regras de qualidade")
    quality.add_argument("--run-id")

    all_cmd = sub.add_parser("run-all", help="Executa batch + streaming + Silver + Gold + qualidade")
    all_cmd.add_argument("--source", choices=("sample", "bigquery"), default="sample")
    all_cmd.add_argument("--source-dir", type=Path)
    all_cmd.add_argument("--billing-project")
    all_cmd.add_argument("--student-limit", type=int, default=0)
    all_cmd.add_argument("--events", type=int, default=24)
    all_cmd.add_argument("--run-id")

    cost = sub.add_parser("record-cloud-cost", help="Registra custo real observado no Cloud Billing")
    cost.add_argument("--period", required=True, help="Competência no formato AAAA-MM")
    cost.add_argument("--amount-brl", type=float, required=True, help="Total exibido no Billing Reports")
    cost.add_argument("--source", required=True, help="Origem auditável do valor, por exemplo Cloud Billing Reports")
    cost.add_argument("--project-id", required=True, help="Projeto filtrado no relatório de faturamento")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = ProjectPaths.from_root(args.project_root)

    if args.command == "generate-sample":
        _print(generate_sample_data(args.destination or paths.sample))
    elif args.command == "batch":
        _print(ingest_csv_snapshot(paths, args.source_dir, args.run_id))
    elif args.command == "extract-bigquery":
        _print(extract_snapshot(args.billing_project, args.destination or paths.staging, student_limit=args.student_limit))
    elif args.command == "simulate-stream":
        if args.target == "local":
            _print({"published": simulate_local(paths, args.events, args.source_csv), "target": "local"})
        else:
            if not args.gcp_project:
                raise SystemExit("--gcp-project e obrigatorio para target=pubsub")
            _print({
                "published": publish_pubsub(paths, args.gcp_project, args.topic, args.events, args.source_csv),
                "target": "pubsub",
            })
    elif args.command == "consume-stream":
        run_id = args.run_id or new_run_id("stream")
        _print({"consumed": consume_local(paths, run_id), "run_id": run_id})
    elif args.command == "validate-local-dlq":
        _print(validate_local_dlq(paths, args.run_id))
    elif args.command == "silver":
        _print(build_silver(paths))
    elif args.command == "gold":
        _print(build_gold(paths))
    elif args.command == "quality":
        _print(run_quality(paths, args.run_id or new_run_id("quality")))
    elif args.command == "run-all":
        _print(run_all(
            paths,
            source=args.source,
            source_dir=args.source_dir,
            billing_project=args.billing_project,
            student_limit=args.student_limit,
            stream_events=args.events,
            run_id=args.run_id,
        ))
    elif args.command == "record-cloud-cost":
        _print(record_cloud_cost(
            paths,
            period=args.period,
            amount_brl=args.amount_brl,
            source=args.source,
            project_id=args.project_id,
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
