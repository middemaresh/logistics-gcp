terraform {
  required_version = ">= 1.5.0"
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

resource "google_storage_bucket" "landing" {
  name                        = var.bucket_name
  location                    = var.region
  project                     = var.project_id
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 90 }
  }
}

resource "google_bigquery_dataset" "logistics" {
  dataset_id                 = var.dataset_id
  project                    = var.project_id
  location                   = var.region
  delete_contents_on_destroy = false
  description                = "Analytics warehouse for shipment and logistics operations"
}

output "landing_bucket" {
  value       = google_storage_bucket.landing.name
  description = "GCS bucket for raw shipment files"
}

output "bigquery_dataset" {
  value       = google_bigquery_dataset.logistics.dataset_id
  description = "BigQuery analytics dataset"
}
