# Status da implantação GCP

## Implantado em 27/08/2026

Projeto: `tech-challenge-fase-2-506814`.

- BigQuery: datasets `alfabetizacao_bronze`, `alfabetizacao_silver`,
  `alfabetizacao_gold` e `alfabetizacao_monitoring`;
- Cloud Storage: bucket `tech-challenge-fase-2-506814-alfabetizacao-lake`, com
  versionamento e regras de ciclo de vida;
- Pub/Sub: tópico de eventos, tópico DLQ, assinatura direta para BigQuery e
  permissões da conta de serviço gerenciada;
- BigQuery: tabela `alfabetizacao_bronze.alunos_stream`;
- Orquestração: seis consultas Bronze, seis Silver, cinco Gold, qualidade e
  exportação Parquet, programadas diariamente;
- IAM: conta de serviço dedicada e papéis mínimos para o pipeline;
- Observabilidade: métrica de erros no Cloud Logging.

## Pendências operacionais

- Executar e evidenciar o primeiro ciclo das consultas agendadas e o evento
  canário do Pub/Sub;
- confirmar a entrega da exportação Parquet ao final do primeiro ciclo;
- criar o budget de R$ 10. O código Terraform e a API já estão configurados,
  mas o provedor local recebeu erro de quota da API de budgets na criação.

O alerta de backlog do Cloud Monitoring não foi implantado porque a política da
organização bloqueou a ativação da API `cloudmonitoring.googleapis.com`. O
monitoramento por logs, as regras de qualidade e a DLQ permanecem implantados.
