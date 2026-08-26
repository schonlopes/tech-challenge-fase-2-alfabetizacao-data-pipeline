# Implantacao no Google Cloud

Esta pasta provisiona a versao cloud do pipeline com Terraform. Ela nao cria
chaves locais: a execucao usa uma service account com privilegio minimo.

## Recursos

- quatro datasets BigQuery: Bronze, Silver, Gold e Monitoring;
- agendamentos batch em sequencia (02h, 03h, 04h e 05h UTC);
- topico Pub/Sub, assinatura direta no BigQuery e dead-letter topic;
- bucket versionado para exportacao Gold em Parquet/Snappy;
- alerta de backlog, metrica de erros e budget opcional;
- service account exclusiva para o pipeline.

## Pre-requisitos

1. Terraform 1.6 ou superior e Google Cloud CLI autenticado.
2. Projeto com faturamento habilitado e permissao para IAM, BigQuery,
   Pub/Sub, Monitoring, Storage e Budgets.
3. Copiar `terraform.tfvars.example` para `terraform.tfvars` e preencher o
   projeto. O billing account e opcional; sem ele o budget nao e criado.

## Comandos

```bash
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan
terraform apply
```

O `apply` pode gerar cobranca e por isso nao e executado automaticamente. A
fonte publica permanece no projeto `basedosdados`; `project_id` e o projeto que
processa e armazena os resultados.

Para publicar eventos de teste depois da implantacao:

```bash
pip install -e ".[cloud]"
gcloud auth application-default login
alfabetizacao-pipeline simulate-stream --target pubsub \
  --gcp-project SEU_PROJETO --topic alfabetizacao-alunos-events --events 24
```

Os scripts SQL sao idempotentes no dia: Bronze substitui somente o snapshot da
data corrente e preserva os dias anteriores; Silver e Gold sao reconstruidas a
partir do snapshot mais recente. O `quality_checks.sql` usa `ASSERT` para falhar
o job se uma regra critica nao for atendida.

