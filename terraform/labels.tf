# CoolBits.ai Data Classification Labels
# =====================================

# Apply data classification labels to all resources
# This ensures proper data governance and retention policies

# Cloud Storage Buckets
resource "google_storage_bucket" "coolbits_logs" {
  name     = "coolbits-logs-${var.project_id}"
  location = var.region
  
  labels = {
    env            = var.environment
    service        = "logging"
    owner          = "ogpt"
    cost_center    = "ogpt"
    data_class     = "internal"
    retention_days = "30"
    backup_scope   = "config-only"
    restore_priority = "P2"
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "coolbits_security_logs" {
  name     = "coolbits-security-logs-${var.project_id}"
  location = var.region
  
  labels = {
    env            = var.environment
    service        = "security"
    owner          = "ogpt"
    cost_center    = "ogpt"
    data_class     = "confidential"
    retention_days = "90"
    backup_scope   = "full"
    restore_priority = "P0"
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "coolbits_backup" {
  name     = "coolbits-backup-${var.project_id}"
  location = var.region
  
  labels = {
    env            = var.environment
    service        = "backup"
    owner          = "ogpt"
    cost_center    = "ogpt"
    data_class     = "confidential"
    retention_days = "365"
    backup_scope   = "full"
    restore_priority = "P0"
  }
  
  # Enable versioning for backup integrity
  versioning {
    enabled = true
  }
  
  # Enable encryption
  encryption {
    default_kms_key_name = google_kms_crypto_key.coolbits_backup_key.id
  }
}

# Cloud SQL Database
resource "google_sql_database_instance" "coolbits_db" {
  name             = "coolbits-db-${var.project_id}"
  database_version = "POSTGRES_14"
  region          = var.region
  
  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }
    
    ip_configuration {
      ipv4_enabled = true
    }
  }
  
  labels = {
    env            = var.environment
    service        = "database"
    owner          = "ogpt"
    cost_center    = "ogpt"
    data_class     = "confidential"
    retention_days = "365"
    backup_scope   = "full"
    restore_priority = "P0"
  }
}

# Cloud Run Services
resource "google_cloud_run_service" "coolbits_frontend" {
  name     = "coolbits-frontend"
  location = var.region
  
  template {
    metadata {
      labels = {
        env            = var.environment
        service        = "frontend"
        owner          = "ogpt"
        cost_center    = "ogpt"
        data_class     = "internal"
        retention_days = "30"
        backup_scope   = "config-only"
        restore_priority = "P1"
      }
    }
    
    spec {
      containers {
        image = "gcr.io/${var.project_id}/coolbits-frontend:latest"
        
        resources {
          limits = {
            cpu    = "1"
            memory = "2Gi"
          }
        }
      }
    }
  }
}

# KMS Key for backup encryption
resource "google_kms_key_ring" "coolbits_backup" {
  name     = "coolbits-backup-keyring"
  location = var.region
}

resource "google_kms_crypto_key" "coolbits_backup_key" {
  name            = "coolbits-backup-key"
  key_ring        = google_kms_key_ring.coolbits_backup.id
  rotation_period = "7776000s" # 90 days
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}
