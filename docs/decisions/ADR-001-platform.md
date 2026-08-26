# ADR-001 — GCP serverless com reprodução local em DuckDB

- Status: aceito
- Data: 26/08/2026

## Contexto

O desafio exige batch, streaming, Medallion, qualidade, observabilidade, FinOps
e execução em AWS, GCP ou Azure. A fonte oficial já está publicada no BigQuery.
Também é necessário permitir avaliação sem credenciais cloud.

## Decisão

Adotar BigQuery Scheduled Queries, Pub/Sub, Cloud Storage e Monitoring na GCP.
Fornecer uma implementação local equivalente em DuckDB/Parquet.

## Consequências positivas

- não há egress ou conector entre provedores para a fonte principal;
- serviços serverless eliminam cluster ocioso;
- SQL é auditável e próximo do conteúdo estudado;
- execução local é rápida, barata e reproduzível;
- Terraform cobre infraestrutura, IAM, monitoramento e budget.

## Trade-offs

- horários fixos não expressam dependência tão bem quanto um orquestrador;
- assinatura Pub/Sub → BigQuery limita transformações evento a evento;
- DuckDB não reproduz elasticidade ou falhas distribuídas;
- BigQuery cria dependência do provedor escolhido.

## Alternativas consideradas

- AWS Glue + Kinesis + S3/Athena: viável e alinhada ao curso, porém exigiria
  mover os dados do BigQuery e manter mais componentes.
- Databricks/Spark: excelente para grande volume e Delta, mas superdimensionado
  para frequência anual e aumentaria custo/operacionalização.
- Dataflow: indicado para janelas e estado complexo; não necessário no cenário
  atual de entrega direta e agregação posterior.

## Gatilhos para revisão

Revisar se houver SLA com dependências estritas, streaming acima de centenas de
GiB/mês, joins em tempo real, múltiplas fontes privadas ou exigência de
portabilidade multi-cloud.

