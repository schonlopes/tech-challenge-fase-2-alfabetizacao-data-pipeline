"""Registro auditável de custo observado no ambiente cloud.

O valor é informado manualmente a partir do relatório de faturamento do provedor.
O módulo não consulta nem estima uma cobrança real: isso evita registrar um custo
como observado antes de ele estar disponível na conta de faturamento.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime

from .paths import ProjectPaths


def record_cloud_cost(
    paths: ProjectPaths,
    *,
    period: str,
    amount_brl: float,
    source: str,
    project_id: str,
) -> dict[str, object]:
    """Registra uma observação mensal de custo confirmada no Cloud Billing."""
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", period):
        raise ValueError("period deve estar no formato AAAA-MM.")
    if amount_brl < 0:
        raise ValueError("amount_brl não pode ser negativo.")
    if not source.strip():
        raise ValueError("source é obrigatória para auditar o valor observado.")
    if not project_id.strip():
        raise ValueError("project_id é obrigatório.")

    paths.ensure()
    observation = {
        "period": period,
        "amount_brl": round(amount_brl, 2),
        "currency": "BRL",
        "source": source.strip(),
        "project_id": project_id.strip(),
        "recorded_at": datetime.now(UTC).isoformat(),
        "status": "observed",
        "note": "Valor informado a partir do relatório de faturamento; não é estimativa.",
    }
    output = paths.evidence / "gcp_cost_observation.json"
    output.write_text(json.dumps(observation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"output": str(output), **observation}
