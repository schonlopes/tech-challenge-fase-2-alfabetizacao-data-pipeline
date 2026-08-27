data "google_project" "current" {}

locals {
  bucket_name = var.data_bucket_name != "" ? var.data_bucket_name : "${var.project_id}-alfabetizacao-lake"

  required_apis = toset([
    "bigquery.googleapis.com",
    "bigquerydatatransfer.googleapis.com",
    "cloudbilling.googleapis.com",
    "billingbudgets.googleapis.com",
    "logging.googleapis.com",
    "pubsub.googleapis.com",
  ])

  bronze_queries = {
    uf                           = "bronze_uf.sql"
    meta_alfabetizacao_brasil    = "bronze_meta_brasil.sql"
    meta_alfabetizacao_uf        = "bronze_meta_uf.sql"
    meta_alfabetizacao_municipio = "bronze_meta_municipio.sql"
    municipio                    = "bronze_municipio.sql"
    alunos                       = "bronze_alunos.sql"
  }

  silver_queries = {
    uf                           = "silver_uf.sql"
    meta_alfabetizacao_brasil    = "silver_meta_brasil.sql"
    meta_alfabetizacao_uf        = "silver_meta_uf.sql"
    meta_alfabetizacao_municipio = "silver_meta_municipio.sql"
    municipio                    = "silver_municipio.sql"
    alunos                       = "silver_alunos.sql"
  }

  gold_queries = {
    indicador_municipio      = "gold_indicador_municipio.sql"
    meta_resultado_municipio = "gold_meta_resultado_municipio.sql"
    evolucao_municipio       = "gold_evolucao_municipio.sql"
    resumo_uf                = "gold_resumo_uf.sql"
    monitoramento_stream     = "gold_monitoramento_stream.sql"
  }
}

resource "google_project_service" "apis" {
  for_each           = local.required_apis
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_storage_bucket" "lake" {
  name                        = local.bucket_name
  project                     = var.project_id
  location                    = var.bigquery_location
  uniform_bucket_level_access = true
  force_destroy               = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age                = 90
      with_state         = "ARCHIVED"
      num_newer_versions = 2
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset" "bronze" {
  dataset_id                 = "alfabetizacao_bronze"
  friendly_name              = "Alfabetizacao Bronze"
  description                = "Snapshots brutos historicos e eventos de alunos."
  location                   = var.bigquery_location
  delete_contents_on_destroy = false
}

resource "google_bigquery_dataset" "silver" {
  dataset_id                 = "alfabetizacao_silver"
  friendly_name              = "Alfabetizacao Silver"
  description                = "Dados tipados, deduplicados, validados e enriquecidos."
  location                   = var.bigquery_location
  delete_contents_on_destroy = false
}

resource "google_bigquery_dataset" "gold" {
  dataset_id                 = "alfabetizacao_gold"
  friendly_name              = "Alfabetizacao Gold"
  description                = "Produtos analiticos para acompanhamento de metas e evolucao."
  location                   = var.bigquery_location
  delete_contents_on_destroy = false
}

resource "google_bigquery_dataset" "monitoring" {
  dataset_id                 = "alfabetizacao_monitoring"
  friendly_name              = "Alfabetizacao Monitoring"
  description                = "Resultados de qualidade e observabilidade."
  location                   = var.bigquery_location
  delete_contents_on_destroy = false
}

resource "google_service_account" "pipeline" {
  account_id   = "alfabetizacao-pipeline"
  display_name = "Pipeline Alfabetizacao"
}

resource "google_project_iam_member" "pipeline_roles" {
  for_each = toset([
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/logging.logWriter",
    "roles/storage.objectAdmin",
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_project_iam_member" "transfer_impersonation" {
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-bigquerydatatransfer.iam.gserviceaccount.com"

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_data_transfer_config" "bronze" {
  for_each = local.bronze_queries

  display_name           = "alfabetizacao-bronze-${each.key}"
  location               = var.bigquery_location
  data_source_id         = "scheduled_query"
  schedule               = "every day 02:00"
  service_account_name   = google_service_account.pipeline.email
  destination_dataset_id = google_bigquery_dataset.bronze.dataset_id
  params = {
    query = replace(file("${path.module}/sql/${each.value}"), "__PROJECT_ID__", var.project_id)
  }

  depends_on = [
    google_project_service.apis,
    google_project_iam_member.pipeline_roles,
    google_project_iam_member.transfer_impersonation,
  ]
}

resource "google_bigquery_data_transfer_config" "silver" {
  for_each = local.silver_queries

  display_name           = "alfabetizacao-silver-${each.key}"
  location               = var.bigquery_location
  data_source_id         = "scheduled_query"
  schedule               = "every day 03:00"
  service_account_name   = google_service_account.pipeline.email
  destination_dataset_id = google_bigquery_dataset.silver.dataset_id
  params = {
    query = replace(file("${path.module}/sql/${each.value}"), "__PROJECT_ID__", var.project_id)
  }

  depends_on = [google_bigquery_data_transfer_config.bronze]
}

resource "google_bigquery_data_transfer_config" "gold" {
  for_each = local.gold_queries

  display_name           = "alfabetizacao-gold-${each.key}"
  location               = var.bigquery_location
  data_source_id         = "scheduled_query"
  schedule               = "every day 04:00"
  service_account_name   = google_service_account.pipeline.email
  destination_dataset_id = google_bigquery_dataset.gold.dataset_id
  params = {
    query = replace(file("${path.module}/sql/${each.value}"), "__PROJECT_ID__", var.project_id)
  }

  depends_on = [google_bigquery_data_transfer_config.silver]
}

resource "google_bigquery_data_transfer_config" "quality" {
  display_name           = "alfabetizacao-quality"
  location               = var.bigquery_location
  data_source_id         = "scheduled_query"
  schedule               = "every day 05:00"
  service_account_name   = google_service_account.pipeline.email
  destination_dataset_id = google_bigquery_dataset.monitoring.dataset_id
  params = {
    query = replace(file("${path.module}/sql/quality_checks.sql"), "__PROJECT_ID__", var.project_id)
  }

  depends_on = [google_bigquery_data_transfer_config.gold]
}

resource "google_bigquery_data_transfer_config" "export_parquet" {
  display_name           = "alfabetizacao-export-gold-parquet"
  location               = var.bigquery_location
  data_source_id         = "scheduled_query"
  schedule               = "every day 04:30"
  service_account_name   = google_service_account.pipeline.email
  destination_dataset_id = google_bigquery_dataset.gold.dataset_id
  params = {
    query = replace(
      replace(file("${path.module}/sql/export_gold_parquet.sql"), "__PROJECT_ID__", var.project_id),
      "__BUCKET__",
      google_storage_bucket.lake.name,
    )
  }

  depends_on = [google_bigquery_data_transfer_config.gold]
}

# Streaming: produtor -> Pub/Sub -> assinatura BigQuery -> Bronze.
resource "google_pubsub_topic" "alunos" {
  name = "alfabetizacao-alunos-events"
}

resource "google_pubsub_topic" "dead_letter" {
  name = "alfabetizacao-alunos-dead-letter"
}

resource "google_bigquery_table" "alunos_stream" {
  dataset_id          = google_bigquery_dataset.bronze.dataset_id
  table_id            = "alunos_stream"
  deletion_protection = true
  schema              = file("${path.module}/schemas/alunos_stream.json")
  clustering          = ["id_municipio", "rede"]

  time_partitioning {
    type          = "DAY"
    field         = "event_date"
    expiration_ms = 31536000000
  }
}

resource "google_bigquery_dataset_iam_member" "pubsub_data_editor" {
  dataset_id = google_bigquery_dataset.bronze.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "pubsub_metadata_viewer" {
  project = var.project_id
  role    = "roles/bigquery.metadataViewer"
  member  = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "pubsub_token_creator" {
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_pubsub_topic_iam_member" "dead_letter_publisher" {
  topic  = google_pubsub_topic.dead_letter.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_pubsub_subscription" "alunos_bigquery" {
  name  = "alfabetizacao-alunos-to-bigquery"
  topic = google_pubsub_topic.alunos.name

  ack_deadline_seconds       = 60
  message_retention_duration = "604800s"

  bigquery_config {
    table               = "${var.project_id}.${google_bigquery_dataset.bronze.dataset_id}.${google_bigquery_table.alunos_stream.table_id}"
    use_table_schema    = true
    drop_unknown_fields = false
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  depends_on = [
    google_bigquery_dataset_iam_member.pubsub_data_editor,
    google_project_iam_member.pubsub_metadata_viewer,
    google_project_iam_member.pubsub_token_creator,
    google_pubsub_topic_iam_member.dead_letter_publisher,
  ]
}

resource "google_pubsub_subscription_iam_member" "dead_letter_subscriber" {
  subscription = google_pubsub_subscription.alunos_bigquery.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_pubsub_topic_iam_member" "pipeline_publisher" {
  topic  = google_pubsub_topic.alunos.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_logging_metric" "pipeline_errors" {
  name   = "alfabetizacao_pipeline_errors"
  filter = "severity>=ERROR AND (resource.type=\"bigquery_dts_config\" OR resource.type=\"pubsub_subscription\")"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

resource "google_billing_budget" "monthly" {
  count           = var.billing_account_id == "" ? 0 : 1
  billing_account = var.billing_account_id
  display_name    = "Tech Challenge Alfabetizacao"

  amount {
    specified_amount {
      currency_code = "BRL"
      units         = tostring(var.monthly_budget_brl)
    }
  }

  budget_filter {
    projects = ["projects/${data.google_project.current.number}"]
  }

  threshold_rules {
    threshold_percent = 0.5
  }
  threshold_rules {
    threshold_percent = 0.8
  }
  threshold_rules {
    threshold_percent = 1.0
  }
}
