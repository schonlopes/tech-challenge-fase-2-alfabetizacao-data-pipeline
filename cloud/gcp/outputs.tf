output "bucket" {
  value       = google_storage_bucket.lake.name
  description = "Bucket versionado para exportacoes Parquet."
}

output "datasets" {
  value = {
    bronze    = google_bigquery_dataset.bronze.dataset_id
    silver    = google_bigquery_dataset.silver.dataset_id
    gold      = google_bigquery_dataset.gold.dataset_id
    monitoring = google_bigquery_dataset.monitoring.dataset_id
  }
}

output "streaming_topic" {
  value = google_pubsub_topic.alunos.name
}

output "pipeline_service_account" {
  value = google_service_account.pipeline.email
}

