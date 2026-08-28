# Checklist de entrega e implantação

## Antes da submissão acadêmica

- [ ] Confirmar se a instituição exige nomes e RMs na capa dos slides.
- [ ] Revisar o vídeo e confirmar duração menor ou igual a 5 minutos.
- [ ] Confirmar ausência de `.env`, chaves JSON e `terraform.tfstate`.
- [x] Executar `python -m unittest discover -s tests -v`.
- [x] Executar `run-all` e verificar `status=PASS`.
- [x] Conferir `git log --graph --oneline --all`.
- [x] Publicar o repositório remoto e integrar PRs de feature na `main`.

## Antes do Terraform

- [x] Projeto e faturamento aprovados pelo responsável.
- [x] APIs e permissões IAM aprovadas para os recursos implantados.
- [x] Nome de bucket globalmente único.
- [x] Localização BigQuery `US`, compatível com a fonte.
- [x] Budget e moeda revisados para a conta.
- [x] `terraform fmt -check -recursive`.
- [x] `terraform validate`.
- [x] `terraform plan` revisado antes do apply.

## Depois do apply

- [x] Executar manualmente um snapshot Bronze.
- [x] Validar materialização das seis tabelas Bronze.
- [x] Executar Silver, Gold e Quality na ordem.
- [x] Publicar um evento canário no Pub/Sub.
- [x] Confirmar Bronze streaming; canário gravado no BigQuery.
- [x] Validar localmente evento inválido e evidência de DLQ (`artifacts/evidence/dlq_validation.json`).
- [ ] Enviar um evento inválido controlado e verificar a DLQ no Pub/Sub, quando houver janela de operação cloud.
- [x] Conferir export Parquet no bucket.
- [x] Conferir budget; alert policy de backlog bloqueada pela política da organização.
- [ ] Consultar o custo do primeiro ciclo no Billing e registrar com `record-cloud-cost` (procedimento em `docs/cost_observation.md`).

## Evidência final para a banca

- [x] URL do repositório acessível.
- [ ] README renderizando Mermaid corretamente.
- [ ] Link ou arquivo do vídeo acessível.
- [ ] Relatório `latest_quality.json` anexado/visível.
- [ ] `terraform plan` ou screenshots da implantação, se exigidos.
- [x] Limitação “cloud não aplicado” removida: infraestrutura central criada.

