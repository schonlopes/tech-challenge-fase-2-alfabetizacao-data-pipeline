# Checklist de entrega e implantação

## Antes de publicar o repositório

- [ ] Substituir “Nome / RM” nos slides.
- [ ] Revisar o vídeo e confirmar duração menor ou igual a 5 minutos.
- [ ] Confirmar ausência de `.env`, chaves JSON e `terraform.tfstate`.
- [ ] Executar `python -m unittest discover -s tests -v`.
- [ ] Executar `run-all` e verificar `status=PASS`.
- [ ] Conferir `git log --graph --oneline --all`.
- [ ] Criar o repositório remoto e abrir PR a partir de uma branch de feature.

## Antes do Terraform

- [ ] Projeto e faturamento aprovados pelo responsável.
- [ ] APIs e permissões IAM aprovadas.
- [ ] Nome de bucket globalmente único.
- [ ] Localização BigQuery `US`, compatível com a fonte.
- [ ] Budget e moeda revisados para a conta.
- [ ] `terraform fmt -check -recursive`.
- [ ] `terraform validate`.
- [ ] `terraform plan` revisado por segunda pessoa.

## Depois do apply

- [ ] Executar manualmente um snapshot Bronze.
- [ ] Validar contagem e schema das seis tabelas.
- [ ] Executar Silver, Gold e Quality na ordem.
- [ ] Publicar um evento canário no Pub/Sub.
- [ ] Confirmar Bronze streaming e backlog zero.
- [ ] Enviar um evento inválido controlado e verificar DLQ.
- [ ] Conferir export Parquet no bucket.
- [ ] Conferir alert policy e budget.
- [ ] Registrar custo do primeiro ciclo.

## Evidência final para a banca

- [ ] URL do repositório acessível.
- [ ] README renderizando Mermaid corretamente.
- [ ] Link ou arquivo do vídeo acessível.
- [ ] Relatório `latest_quality.json` anexado/visível.
- [ ] `terraform plan` ou screenshots da implantação, se exigidos.
- [ ] Limitação “cloud não aplicado” removida somente após teste real.

