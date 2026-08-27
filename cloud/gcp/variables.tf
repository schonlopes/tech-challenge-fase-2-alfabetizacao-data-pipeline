variable "project_id" {
  description = "Projeto GCP que hospedara e faturara o pipeline."
  type        = string
}

variable "region" {
  description = "Regiao dos recursos regionais."
  type        = string
  default     = "southamerica-east1"
}

variable "bigquery_location" {
  description = "A fonte basedosdados esta em US; datasets de destino devem usar a mesma localizacao."
  type        = string
  default     = "US"
}

variable "data_bucket_name" {
  description = "Nome globalmente unico do bucket; vazio usa <project_id>-alfabetizacao-lake."
  type        = string
  default     = ""
}

variable "billing_account_id" {
  description = "Opcional: ID XXXXXX-XXXXXX-XXXXXX da conta de faturamento para criar budget."
  type        = string
  default     = ""
}

variable "monthly_budget_brl" {
  description = "Limite mensal de referencia para alertas FinOps."
  type        = number
  default     = 100
}

