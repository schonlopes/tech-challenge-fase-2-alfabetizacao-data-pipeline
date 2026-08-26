# Roteiro do vídeo executivo — duração alvo: 4min30s

## Slide 1 — Problema e objetivo (0:00–0:35)

“Este projeto cria um pipeline híbrido para acompanhar a alfabetização no
Brasil. A solução usa as seis tabelas do INEP publicadas pela Base dos Dados,
com resultados e metas do Brasil, estados, municípios e alunos. O objetivo é
transformar esses dados em indicadores confiáveis para saber onde a meta foi
atingida, onde há risco e como cada município evoluiu.”

## Slide 2 — Arquitetura (0:35–1:25)

“A arquitetura foi desenhada na Google Cloud porque a fonte já está no
BigQuery. O batch captura snapshots diários das seis tabelas. O streaming é
simulado com eventos de alunos publicados no Pub/Sub e gravados diretamente na
Bronze; mensagens inválidas seguem para uma dead-letter queue. Bronze preserva
histórico, Silver padroniza e integra, e Gold entrega as visões analíticas. A
mesma lógica roda localmente com DuckDB e Parquet, sem exigir conta cloud.”

## Slide 3 — Qualidade e confiabilidade (1:25–2:10)

“Qualidade é uma etapa bloqueante. Validamos chaves obrigatórias, duplicidades,
integridade municipal, percentuais entre zero e cem, soma dos níveis e
consistência do corte de 743 pontos. O ensaio local executou trinta e cinco checks
com score de cem por cento. No BigQuery, um ASSERT falha o agendamento se houver
problema crítico. Para o streaming, checkpoint e deduplicação tornam o
reprocessamento seguro.”

## Slide 4 — Produtos Gold e valor (2:10–3:05)

“A Gold possui cinco produtos. O indicador municipal combina taxa, média,
participação, meta do ano, gap e status. A visão meta versus resultado abre o
horizonte de 2024 a 2030, inclusive anos ainda sem avaliação. A evolução calcula
variação anual por janela. Há também resumo por UF e monitoramento da amostra de
eventos. Assim, uma equipe pode priorizar municípios críticos e acompanhar o
efeito de ações educacionais.”

## Slide 5 — Operação, FinOps e segurança (3:05–3:55)

“O desenho usa serviços serverless, tabelas particionadas e clusterizadas,
Parquet compactado e lifecycle. No cenário de referência, o custo incremental
fica abaixo de um dólar por mês, com budget de cem reais e alertas em cinquenta,
oitenta e cem por cento. Monitoring acompanha backlog, erros, qualidade e custo.
Na segurança, não há credenciais no repositório, o acesso é por service account
e a Gold não expõe identificadores de alunos.”

## Slide 6 — Evidências e próximos passos (3:55–4:30)

“O pipeline foi executado ponta a ponta: noventa e seis registros de alunos no
batch, vinte e quatro eventos, doze indicadores municipais e quarenta e duas
combinações de metas. Seis testes automatizados passaram. A implantação cloud
está pronta em Terraform, mas não foi aplicada sem credenciais para evitar
cobrança não autorizada. Os próximos passos são aplicar em um projeto GCP,
conectar um dashboard e evoluir para Dataflow caso o streaming exija janelas
complexas. Obrigado.”
