output "bucket_lake" {
  value = google_storage_bucket.lake.name
}

output "datasets" {
  value = [for d in google_bigquery_dataset.capas : d.dataset_id]
}
