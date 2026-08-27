# Evidência de custo real no GCP

Este procedimento fecha o ciclo FinOps entre estimativa e custo efetivamente
observado. O repositório não registra valores fictícios: o arquivo de evidência só
é criado depois da consulta ao relatório de faturamento da conta autorizada.

## Coleta mensal

1. No Cloud Billing, abrir **Reports** e filtrar o projeto
   `tech-challenge-fase-2-506814` e o período fechado.
2. Registrar o total da moeda exibida, a referência do relatório e a competência
   no comando abaixo. Para o primeiro ciclo, usar o mês em que os jobs foram
   executados, mesmo que o valor seja R$ 0,00.
3. Anexar ou manter um screenshot do relatório apenas fora do repositório se ele
   expuser dados de faturamento pessoais.

```powershell
alfabetizacao-pipeline record-cloud-cost `
  --period 2026-08 `
  --amount-brl VALOR_EXIBIDO_NO_BILLING `
  --source "Cloud Billing Reports - projeto filtrado" `
  --project-id tech-challenge-fase-2-506814
```

O comando cria `artifacts/evidence/gcp_cost_observation.json`, com período,
valor, moeda, fonte, projeto, horário do registro e status `observed`.

## Interpretação

- Compare o total observado com a estimativa de referência de aproximadamente
  US$ 0,66/mês em [FinOps](finops.md).
- Se o orçamento atingir 80%, siga o procedimento de anomalia de custo do
  [runbook](monitoring_runbook.md).
- Não substitua a estimativa nem o custo observado por valores de créditos,
  impostos ou câmbio sem identificá-los na fonte.
