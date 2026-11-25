variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "bucket_name" {
  description = "Globally unique name for the GCS landing bucket"
  type        = string
}

variable "dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "logistics_analytics"
}

variable "region" {
  description = "GCP region for the bucket and BigQuery dataset"
  type        = string
  default     = "US"
}
