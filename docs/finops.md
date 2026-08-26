# FinOps

Preços consultados em 26/08/2026 nas páginas oficiais do Google Cloud. Valores
em dólar, sem impostos, câmbio, descontos negociados ou consumo preexistente da
conta. A calculadora do provedor deve ser refeita antes de produção.

## Premissas do cenário de referência

| Componente | Premissa mensal |
|---|---:|
| BigQuery — dados consultados | 15 GiB/dia × 30 = 450 GiB |
| BigQuery — armazenamento lógico ativo | 25 GiB |
| Pub/Sub → BigQuery | 1 GiB entregue |
| Cloud Storage Standard US | 10 GiB |
| Retenção Pub/Sub | 7 dias, backlog normal próximo de zero |

## Estimativa

| Componente | Regra pública | Estimativa |
|---|---|---:|
| BigQuery on-demand | 1 TiB/mês gratuito; depois US$ 6,25/TiB | US$ 0,00 |
| BigQuery storage | 10 GiB gratuitos; depois US$ 0,000031507/GiB-hora | ≈ US$ 0,35 |
| Assinatura Pub/Sub → BigQuery | US$ 50/TiB, sem franquia específica | ≈ US$ 0,05 |
| GCS Standard multi-region US | US$ 0,000035616/GiB-hora | ≈ US$ 0,26 |
| Export batch do BigQuery | gratuito no pool compartilhado; paga-se o GCS | US$ 0,00 |
| **Total de referência** | antes de operações, impostos e câmbio | **≈ US$ 0,66/mês** |

Se a franquia de armazenamento do BigQuery já tiver sido consumida por outros
projetos da conta, os 25 GiB custariam aproximadamente US$ 0,58 e o total iria
para cerca de US$ 0,89/mês.

Fórmulas:

```text
BigQuery storage = max(25 - 10, 0) × 0,000031507 × 730 ≈ US$ 0,35
Pub/Sub BQ       = 1 / 1024 × 50                         ≈ US$ 0,05
GCS Standard     = 10 × 0,000035616 × 730               ≈ US$ 0,26
```

## Controles implementados

### Computação

- on-demand, sem slots reservados ou cluster permanente;
- schedules diários e materialização de cada camada;
- seleção explícita de campos na Silver/Gold;
- partição por `ano` ou data de ingestão;
- cluster por `id_municipio`, `sigla_uf` e `rede`;
- cache do BigQuery aproveitado quando possível;
- `ASSERT` evita propagar e consumir dados inválidos.

### Armazenamento

- Parquet ZSTD local e Parquet/Snappy no GCS;
- Bronze preserva histórico; Silver e Gold guardam apenas o estado derivado;
- tabela de streaming expira partições após 365 dias;
- bucket passa para Nearline após 30 dias;
- versões não correntes antigas são removidas depois de 90 dias, mantendo duas.

### Governança financeira

- budget opcional de R$ 100 com alertas em 50%, 80% e 100%;
- uma service account exclusiva facilita atribuição de custo;
- nomes de agendamento e labels do extrator permitem filtrar faturamento;
- `latest_run.json` registra bytes físicos locais por camada;
- antes de consultas ad hoc, usar dry-run e `maximum_bytes_billed`.

## Limites e gatilhos de evolução

| Sinal | Ação recomendada |
|---|---|
| > 1 TiB consultado/mês com frequência | revisar projeção, partições e tabelas intermediárias |
| > 10 TiB/mês estáveis | comparar on-demand com BigQuery Editions/reservas |
| Streaming > 100 GiB/mês | revisar batching, schema e custo da assinatura BigQuery |
| Backlog retido por dias | corrigir schema antes que retenção gere custo e perda |
| Histórico Bronze cresce sem consulta | reduzir retenção ou arquivar em GCS Nearline/Coldline |

## Fontes

- [BigQuery pricing](https://cloud.google.com/bigquery/pricing)
- [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing)
- [Cloud Storage pricing](https://cloud.google.com/storage/pricing)
- [Estimate and control BigQuery costs](https://cloud.google.com/bigquery/docs/best-practices-costs)
- [Optimize BigQuery query computation](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)

