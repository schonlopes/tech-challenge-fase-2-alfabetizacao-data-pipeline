# Prontidão para o Tech Challenge - Fase 2

Este documento relaciona os requisitos do enunciado à evidência verificável no
repositório. Ele não substitui itens que dependem da gravação e da submissão pelo
grupo, nem declara como executada uma validação que ainda não foi observada.

| Critério obrigatório | Estado | Evidência |
|---|---|---|
| Fonte Indicador Criança Alfabetizada / Base dos Dados | Atendido | Seis consultas Bronze usam `basedosdados.br_inep_avaliacao_alfabetizacao`; `bigquery_source.py` permite extração oficial. |
| Entidades UF, metas Brasil/UF/município, município e alunos | Atendido | `contracts.py`, CSVs de amostra e SQLs Bronze. |
| Batch e streaming | Atendido | Scheduled Queries e Pub/Sub -> BigQuery; simulador JSONL e checkpoint no modo local. |
| Medalhão Bronze, Silver e Gold | Atendido | Código Python, SQL BigQuery e produtos Gold descritos no README. |
| Limpeza, normalização, chaves e integração | Atendido | Transformações Silver e regras de qualidade. |
| Produtos analíticos | Atendido | Indicador municipal, meta x resultado, evolução, resumo por UF e monitoramento de stream. |
| Qualidade | Atendido | Duplicidade, ausências, chaves, consistência, `ASSERT` cloud e evidência de 7 regras aprovadas. |
| Monitoramento | Atendido com limitação | Logs, DQ, métricas, runbook e validação local automatizada da DLQ; alerta de backlog não foi criado por política organizacional documentada. |
| FinOps | Atendido | Parquet, partição, cluster, SQL serverless, lifecycle, estimativa, budget e procedimento para custo observado. |
| Ambiente cloud | Atendido | Infraestrutura Terraform e ciclo validado no projeto GCP `tech-challenge-fase-2-506814`. |
| README completo | Atendido | Contexto, desafio, fonte, arquitetura, diagrama, fluxo, tecnologias, trade-offs, monitoramento, FinOps e IA. |
| Aplicação em IA | Atendido | README descreve predição, análise de desigualdade e apoio a políticas públicas, com limites de uso. |
| Código, documentação e testes | Atendido | Pacote Python, SQL, Terraform, docs, CI e 8 testes automatizados aprovados. |
| Git, branches e PRs reais | Atendido | Histórico, branches e [PR #1](https://github.com/schonlopes/tech-challenge-fase-2-alfabetizacao-data-pipeline/pull/1), [PR #2](https://github.com/schonlopes/tech-challenge-fase-2-alfabetizacao-data-pipeline/pull/2) e PR #3 no GitHub. |

## Itens de responsabilidade do grupo antes da submissão

- Gravar e disponibilizar o vídeo executivo com duração máxima de cinco minutos;
- Revisar nomes e RMs nos slides;
- Consultar o Billing após o fechamento do ciclo e executar `record-cloud-cost`
  com o valor visualizado, se houver acesso à conta de faturamento;
- Quando houver janela de operação cloud, executar um evento inválido controlado
  no Pub/Sub para complementar a evidência local de DLQ já automatizada.

Esses itens não invalidam a implementação já entregue, mas dependem de ações ou
acessos que não podem ser simulados de forma honesta dentro do repositório.
