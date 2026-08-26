# Segurança, privacidade e LGPD

## Natureza dos dados

O conjunto é público e informa que os códigos de escola são fictícios. Ainda
assim, `id_aluno`, localização municipal, rede e resultado educacional devem ser
tratados como dados pseudonimizados. Pseudonimização não elimina todo o risco de
reidentificação quando bases são combinadas.

## Princípios aplicados

- finalidade restrita ao monitoramento agregado da alfabetização;
- minimização: a Gold não expõe `id_aluno` nem `id_escola`;
- nenhuma tentativa de reidentificar estudantes ou escolas;
- segregação Bronze/Silver/Gold e privilégio mínimo;
- rastreabilidade por fonte, horário e run;
- retenção explícita e expiração da tabela de streaming;
- credenciais fora do repositório e chaves bloqueadas por `.gitignore`/testes.

## IAM

A service account do pipeline recebe apenas edição de dados BigQuery, execução
de jobs, escrita de logs e objetos no bucket. O produtor recebe somente
`pubsub.publisher` no tópico. A service agent do Pub/Sub recebe acesso de edição
somente ao dataset Bronze e leitura de metadados.

Em produção, recomenda-se:

1. Workload Identity Federation em vez de chaves JSON;
2. grupos separados para engenharia, análise e auditoria;
3. acesso à Bronze restrito; consumo humano apenas na Gold;
4. Data Access Audit Logs e alertas de alteração IAM;
5. VPC Service Controls se houver outros dados sensíveis no mesmo perímetro.

## Criptografia e rede

Os serviços GCP usam criptografia em repouso e trânsito por padrão. CMEK pode
ser adicionado quando houver requisito regulatório. A arquitetura evita egress:
fonte e destino BigQuery ficam na localização `US`; o bucket também usa `US`.

## Resposta a incidente de privacidade

Interromper o compartilhamento/consumo, preservar logs, identificar tabelas e
principais acessos, acionar o responsável por privacidade e seguir o plano
organizacional de notificação. Não apagar evidências antes da orientação legal.

