# Governança Git e integração por Pull Request

Este documento descreve o fluxo de desenvolvimento adotado e preserva o vínculo entre requisitos, branches e commits. Ele não substitui uma Pull Request hospedada: a PR deve ser criada no repositório remoto antes da integração na `main`.

## Histórico de evolução

| Etapa | Branch | Evidência principal | Integração |
|---|---|---|---|
| Pipeline local | `main` | `ff713d3 feat: implement local medallion pipeline` | base da solução |
| Arquitetura GCP | `feat/gcp-cloud` | `32a9987 feat: add GCP batch and streaming infrastructure` | `a561e84 merge: GCP cloud architecture` |
| Documentação e materiais | `feat/documentation-delivery` | `b5848e0 docs: finalize phase 2 delivery and executive artifacts` | `356f177 merge: complete phase 2 tech challenge delivery` |
| Validação em nuvem | `main` | `d59751b fix: finalize GCP pipeline deployment configuration` e `73b33e1 fix: validate complete GCP pipeline cycle` | commits posteriores à integração anterior |
| Revisão executiva | `feat/executive-delivery-readiness` | commit desta revisão | **aguarda PR remota** |

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

## Comandos para publicar esta revisão

Após criar um repositório vazio no GitHub/GitLab, configurar o endereço remoto e publicar as branches:

```bash
git remote add origin <URL_DO_REPOSITORIO>
git push -u origin main
git push -u origin feat/gcp-cloud
git push -u origin feat/documentation-delivery
git push -u origin feat/executive-delivery-readiness
```

Em seguida, abrir a PR da branch `feat/executive-delivery-readiness` para `main` com o conteúdo de `docs/pull_requests/PR-003-executive-delivery-readiness.md`.

> A criação da PR no servidor é a evidência exigida pelo critério. Um arquivo local de rascunho não deve ser apresentado como se fosse uma PR real.
