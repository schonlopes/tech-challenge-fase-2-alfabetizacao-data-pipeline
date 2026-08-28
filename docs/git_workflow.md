# Governança Git e integração por Pull Request

Este documento descreve o fluxo de desenvolvimento adotado e preserva o vínculo entre requisitos, branches, commits e Pull Requests já integradas à `main`.

## Histórico de evolução

| Etapa | Branch | Evidência principal | Integração |
|---|---|---|---|
| Pipeline local | `main` | `ff713d3 feat: implement local medallion pipeline` | base da solução |
| Arquitetura GCP | `feat/gcp-cloud` | `32a9987 feat: add GCP batch and streaming infrastructure` | `a561e84 merge: GCP cloud architecture` |
| Documentação e materiais | `feat/documentation-delivery` | `b5848e0 docs: finalize phase 2 delivery and executive artifacts` | `356f177 merge: complete phase 2 tech challenge delivery` |
| Validação em nuvem | `main` | `d59751b fix: finalize GCP pipeline deployment configuration` e `73b33e1 fix: validate complete GCP pipeline cycle` | commits posteriores à integração anterior |
| Remoção de materiais em revisão | `chore/remove-executive-media` | `ceca691 chore: remove executive media from repository` | [PR #1](https://github.com/schonlopes/tech-challenge-fase-2-alfabetizacao-data-pipeline/pull/1), comentada e integrada em `c7c5ca0` |
| Documentação GCP e governança Git | `feat/executive-delivery-readiness` | `7633b3c docs: prepare executive delivery for PR review` | [PR #2](https://github.com/schonlopes/tech-challenge-fase-2-alfabetizacao-data-pipeline/pull/2), comentada e integrada em `a02c16d` |

## Convenção de commits

- `feat:` para funcionalidades novas;
- `fix:` para correções e validações de comportamento;
- `docs:` para documentação e materiais de entrega;
- `merge:` somente para integração de uma feature concluída.

Cada commit deve explicar o resultado da alteração, sem mensagens vagas como `update` ou `ajustes`.

## Fluxo obrigatório para a integração

1. Criar uma branch a partir da `main` para cada funcionalidade.
2. Implementar, testar e registrar commits pequenos, claros e coerentes.
3. Publicar a branch no GitHub ou GitLab.
4. Abrir uma Pull Request para `main`, usando o template do repositório.
5. Registrar na PR as evidências de teste, impacto de custo/segurança e plano de rollback.
6. Adicionar ao menos um comentário de revisão quando houver decisão técnica relevante; por exemplo, o motivo de usar Pub/Sub → BigQuery direto em vez de Dataflow.
7. Fazer merge somente após a revisão e manter a PR como evidência no remoto.

## Evidências remotas

O repositório está publicado em [GitHub](https://github.com/schonlopes/tech-challenge-fase-2-alfabetizacao-data-pipeline). As PRs #1 e #2 preservam descrição, risco/rollback, checks aprovados, comentários de revisão e os commits de merge. O arquivo `docs/pull_requests/PR-003-executive-delivery-readiness.md` é apenas o rascunho local que originou a PR #2.
