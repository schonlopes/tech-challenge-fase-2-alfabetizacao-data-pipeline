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

## Evidências do primeiro ciclo controlado

- As 6 cargas Bronze, 6 transformações Silver e 5 produtos Gold terminaram com
  status `SUCCEEDED`;
- o evento `canary-20260827-003` foi gravado em
  `alfabetizacao_bronze.alunos_stream`; a correção subsequente foi reprocessada
  na Silver de alunos e no monitoramento Gold;
- `alfabetizacao_bronze.uf` materializou 145 linhas, de 2023 a 2024;
- a consulta de qualidade registrou 7 regras aprovadas e 0 falhas;
- a exportação gerou três arquivos Parquet em
  `gs://tech-challenge-fase-2-506814-alfabetizacao-lake/gold/indicador_municipio/latest/`;
- o budget de R$ 10 foi criado com limiares de 50%, 80% e 100%.

## Limitação da organização

O alerta de backlog do Cloud Monitoring não foi implantado porque a política da
organização bloqueou a ativação da API `cloudmonitoring.googleapis.com`.
Monitoramento por logs, regras de qualidade e DLQ permanecem implantados.
