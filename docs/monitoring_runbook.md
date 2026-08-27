# Observabilidade e runbook

## SLOs

| Indicador | Objetivo |
|---|---|
| Freshness batch | Gold disponível até 06:00 UTC em 99% dos dias executados |
| Latência streaming | evento visível na Bronze em até 5 min (P95) |
| Qualidade crítica | zero falhas críticas publicadas na Gold |
| Duplicidade Gold | zero no grão declarado |
| Backlog Pub/Sub | abaixo de 1.000 mensagens por 5 min |
| Orçamento | abaixo de 80% do budget antes dos últimos 5 dias do mês |

## Sinais

- status dos BigQuery Data Transfer configs Bronze/Silver/Gold/Quality;
- `alfabetizacao_monitoring.quality_results`;
- métrica `num_undelivered_messages` da assinatura;
- dead-letter topic;
- log-based metric `alfabetizacao_pipeline_errors`;
- bytes, linhas e duração em `artifacts/evidence/latest_run.json` no local;
- Billing Budget em 50%, 80% e 100%.

## Severidade

| Nível | Exemplo | Resposta |
|---|---|---|
| P1 | perda/corrupção de Bronze, vazamento ou custo descontrolado | interromper consumidores e escalar imediatamente |
| P2 | Gold atrasada, DQ crítica, backlog sustentado | agir em até 1 hora |
| P3 | aviso de distribuição, tendência de custo ou atraso sem impacto | corrigir no próximo ciclo |

## Procedimento: falha batch

1. Identificar o primeiro agendamento com erro; não reexecutar Gold isoladamente.
2. Abrir detalhes do job e verificar schema, permissão, localização e bytes.
3. Consultar a partição Bronze da data e compará-la ao dia anterior.
4. Corrigir a causa; iniciar manualmente Bronze → Silver → Gold → Quality.
5. Confirmar que `quality_results` não contém falhas críticas.
6. Registrar horário, causa, volume reprocessado e custo estimado.

## Procedimento: backlog ou DLQ

Antes da implantação, valide o tratamento local com
`alfabetizacao-pipeline validate-local-dlq --run-id dlq-validation-final`.
O artefato `artifacts/evidence/dlq_validation.json` comprova que uma mensagem
inválida foi isolada na DLQ local. Em produção, confirme separadamente a
assinatura/tópico DLQ no Pub/Sub, pois a simulação local não substitui esse teste.

1. Verificar se o schema JSON publicado coincide com `alunos_stream.json`.
2. Inspecionar uma mensagem da DLQ sem copiar identificadores para canais
   externos.
3. Corrigir produtor ou schema de forma retrocompatível.
4. Publicar primeiro um evento canário e observar a Bronze.
5. Reproduzir as mensagens da DLQ com o mesmo `event_id`.
6. Executar a Silver; a deduplicação evita duplicar o aluno.

## Procedimento: falha de qualidade

1. Filtrar `quality_results` pela data e `passed=false`.
2. Separar falha de contrato, chave, faixa, referência ou consistência.
3. Confirmar se o defeito já existe na fonte ou foi introduzido na Silver.
4. Não editar Bronze; corrigir transformação/contrato e reconstruir derivadas.
5. Só liberar Gold após o `ASSERT` passar.

## Procedimento: anomalia de custo

1. Identificar SKU e projeto no Billing Report.
2. Para BigQuery, consultar `INFORMATION_SCHEMA.JOBS_BY_PROJECT` e ordenar por
   `total_bytes_billed`.
3. Suspender temporariamente o agendamento responsável se o budget chegar a
   100%, preservando Bronze/streaming quando seguro.
4. Aplicar filtro de partição, projeção de colunas ou materialização.
5. Fazer dry-run e definir `maximum_bytes_billed` antes de retomar.

## Replay local

O checkpoint é atualizado somente depois da escrita da Bronze. Para um replay
controlado, copie o inbox e o checkpoint para um diretório de teste; não altere
o arquivo de produção. Bronze batch é reprocessável por `run_id` e Silver/Gold
são sempre reconstruíveis.

## Encerramento do incidente

- SLO recuperado e DQ crítica zerada;
- backlog/DLQ estabilizados;
- custo incremental registrado;
- causa raiz e ação preventiva documentadas;
- teste de regressão adicionado quando aplicável.

