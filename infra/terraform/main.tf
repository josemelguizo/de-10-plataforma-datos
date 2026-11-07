# Infraestructura como código en Google Cloud (capa gratuita).
#
# Antes de usar: crea un proyecto en console.cloud.google.com, instala la CLI
# de gcloud y Terraform, y autentícate con:
#     gcloud auth application-default login
#
# Luego:
#     terraform init
#     terraform plan -var="project_id=TU_PROYECTO"
#     terraform apply -var="project_id=TU_PROYECTO"
# Y cuando termines de practicar, para no gastar:
#     terraform destroy -var="project_id=TU_PROYECTO"

terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Data lake: bucket para la capa raw/bronze.
resource "google_storage_bucket" "lake" {
  name                        = "${var.project_id}-lake"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# Warehouse: datasets de BigQuery por capa.
resource "google_bigquery_dataset" "capas" {
  for_each   = toset(["raw", "staging", "marts"])
  dataset_id = each.key
  location   = var.region
}

# TODO: agrega lo que tu arquitectura necesite. Por ejemplo, una cuenta de
# servicio para tu pipeline con permisos mínimos (google_service_account y
# google_project_iam_member con roles/bigquery.dataEditor y
# roles/storage.objectAdmin), y documenta la decisión en docs/decisiones/.
