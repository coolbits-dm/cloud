# CoolBits.ai Terraform Infrastructure Automation
# ================================================

# Main Terraform Configuration
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "coolbits-terraform-state"
    prefix = "terraform/state"
  }
}

# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
  
  # Enable beta features
  beta = true
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west3"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "europe-west3-a"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alerts"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Password for the database user"
  type        = string
  sensitive   = true
}

variable "db_readonly_password" {
  description = "Password for the readonly database user"
  type        = string
  sensitive   = true
}

variable "trusted_ips" {
  description = "List of trusted IP addresses"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "replica_region" {
  description = "Region for read replica"
  type        = string
  default     = "europe-west1"
}

variable "dr_region" {
  description = "Disaster recovery region"
  type        = string
  default     = "europe-west1"
}

variable "slack_channel" {
  description = "Slack channel for alerts"
  type        = string
  default     = "#coolbits-alerts"
}

# Local Values
locals {
  common_labels = {
    env         = var.environment
    project     = "coolbits"
    owner       = "coolbits"
    cost_center = "infrastructure"
    managed_by  = "terraform"
  }
  
  # Resource naming convention
  name_prefix = "coolbits-${var.environment}"
  
  # Regions
  regions = {
    primary = var.region
    replica = var.replica_region
    dr      = var.dr_region
  }
}

# Enable Required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "pubsub.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "storage.googleapis.com",
    "cloudkms.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
    "cloudbuild.googleapis.com",
    "container.googleapis.com",
    "artifactregistry.googleapis.com"
  ])
  
  service = each.value
  
  disable_on_destroy = false
}

# Service Accounts
resource "google_service_account" "coolbits_cloud_run" {
  account_id   = "coolbits-cloud-run"
  display_name = "CoolBits Cloud Run Service Account"
  
  labels = local.common_labels
}

resource "google_service_account" "coolbits_monitoring" {
  account_id   = "coolbits-monitoring"
  display_name = "CoolBits Monitoring Service Account"
  
  labels = local.common_labels
}

resource "google_service_account" "coolbits_backup" {
  account_id   = "coolbits-backup"
  display_name = "CoolBits Backup Service Account"
  
  labels = local.common_labels
}

# IAM Bindings
resource "google_project_iam_binding" "coolbits_cloud_run_iam" {
  project = var.project_id
  role    = "roles/run.invoker"
  
  members = [
    "serviceAccount:${google_service_account.coolbits_cloud_run.email}",
  ]
}

resource "google_project_iam_binding" "coolbits_monitoring_iam" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  
  members = [
    "serviceAccount:${google_service_account.coolbits_monitoring.email}",
  ]
}

resource "google_project_iam_binding" "coolbits_backup_iam" {
  project = var.project_id
  role    = "roles/storage.admin"
  
  members = [
    "serviceAccount:${google_service_account.coolbits_backup.email}",
  ]
}

# Cloud Build Trigger for CI/CD
resource "google_cloudbuild_trigger" "coolbits_deploy" {
  name        = "coolbits-deploy"
  description = "Deploy CoolBits application"
  
  github {
    owner = "coolbits-ai"
    name  = "coolbits"
    
    push {
      branch = "^main$"
    }
  }
  
  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build",
        "-t",
        "gcr.io/${var.project_id}/coolbits:$COMMIT_SHA",
        "."
      ]
    }
    
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "push",
        "gcr.io/${var.project_id}/coolbits:$COMMIT_SHA"
      ]
    }
    
    step {
      name = "gcr.io/cloud-builders/gcloud"
      args = [
        "run",
        "deploy",
        "coolbits-production",
        "--image",
        "gcr.io/${var.project_id}/coolbits:$COMMIT_SHA",
        "--region",
        var.region,
        "--platform",
        "managed",
        "--allow-unauthenticated"
      ]
    }
  }
  
  labels = local.common_labels
}

# Artifact Registry Repository
resource "google_artifact_registry_repository" "coolbits_repo" {
  location      = var.region
  repository_id = "coolbits"
  description   = "CoolBits Docker repository"
  format        = "DOCKER"
  
  labels = local.common_labels
}

# Cloud Storage Bucket for Terraform State
resource "google_storage_bucket" "coolbits_terraform_state" {
  name          = "coolbits-terraform-state-${var.project_id}"
  location      = "EU"
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  labels = local.common_labels
}

# Outputs
output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "environment" {
  description = "Environment"
  value       = var.environment
}

output "service_accounts" {
  description = "Service account emails"
  value = {
    cloud_run  = google_service_account.coolbits_cloud_run.email
    monitoring = google_service_account.coolbits_monitoring.email
    backup     = google_service_account.coolbits_backup.email
  }
}

output "artifact_registry_repo" {
  description = "Artifact Registry repository"
  value       = google_artifact_registry_repository.coolbits_repo.name
}

output "terraform_state_bucket" {
  description = "Terraform state bucket"
  value       = google_storage_bucket.coolbits_terraform_state.name
}
