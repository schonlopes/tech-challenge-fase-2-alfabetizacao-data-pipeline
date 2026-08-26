# Matriz de atendimento ao enunciado

| Requisito | Implementação | Evidência |
|---|---|---|
| Integrar as seis entidades | contratos e ingestão de `uf`, metas Brasil/UF/município, `municipio`, `alunos` | `contracts.py`, `batch.py`, SQL Bronze |
| Pipeline batch | snapshot append-only local e scheduled queries cloud | `batch.py`, `cloud/gcp/sql/bronze_*.sql` |
| Streaming simulado | JSONL + checkpoint e Pub/Sub → BigQuery + DLQ | `streaming.py`, `main.tf` |
| Bronze histórica | partição por run/data e metadados de ingestão | `batch.py`, SQL Bronze |
| Silver tratada | tipos, normalização, chaves, deduplicação e integração | `silver.py`, SQL Silver |
| Gold municipal | indicador, meta x resultado e evolução | `gold.py`, SQL Gold |
| Duplicidades | chave natural nas seis entidades e grão Gold | `quality.py` |
| Ausências | chaves não nulas e enriquecimento completo | `quality.py` |
| Validação de chaves | integridade com dimensão municipal | `quality.py` |
| Consistência | faixa 0–100, níveis, corte 743 e taxa cruzada | `quality.py` |
| Enriquecimento externo | diretório municipal da Base dos Dados | `silver_municipio.sql`, amostra de referência |
| Monitoramento | manifestos, DQ, backlog, erros, DLQ e runbook | `latest_run.json`, `main.tf`, runbook |
| Parquet/colunar | Parquet ZSTD local, BigQuery colunar e export Snappy | `duck.py`, `export_gold_parquet.sql` |
| Particionamento/otimização | ano/data, clustering, projeção e materialização | SQLs Silver/Gold, FinOps |
| Estimativa de custo | cenário, fórmula, preços e budget | `docs/finops.md`, Terraform budget |
| Execução em nuvem | infraestrutura GCP completa | `cloud/gcp` |
| Diagrama e fluxo | diagramas Mermaid lógico/físico | README, `architecture.md` |
| Trade-offs | ADR e README | `ADR-001-platform.md` |
| Uso de IA | declaração explícita e limites | `ai_usage.md` |
| Código e organização | pacote Python, SQL, Terraform, testes e CI | estrutura do repositório |
| Histórico Git | commits e merges de branches de feature | `git log --graph --oneline --all` |
| Video executivo | slides, roteiro e MP4 de até 5 minutos | `artifacts/executive` |

## Pontos que dependem do responsável pela submissão

- executar `terraform plan/apply` em um projeto GCP autorizado;
- substituir a amostra pela extração completa oficial na evidência final, se
  exigido pela banca;
- publicar o repositório remoto e abrir o pull request — nenhum PR fictício foi
  criado;
- revisar nome, RM e integrantes nos slides antes da entrega;
- confirmar que o link/vídeo está acessível à banca.

