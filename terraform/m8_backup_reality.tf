# CoolBits.ai M8 Reality Check - Backup Implementation
# =====================================================

# Create backup bucket with encryption
resource "google_storage_bucket" "coolbits_backups_reality" {
  name          = "coolbits-backups-${var.project_id}"
  location      = "EU"
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  # Versioning for backup integrity
  versioning {
    enabled = true
  }
  
  # Lifecycle rules for retention
  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type = "Delete"
    }
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
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
  
  # CMEK Encryption
  encryption {
    default_kms_key_name = google_kms_crypto_key.coolbits_backup_key.id
  }
  
  labels = {
    env         = var.environment
    service     = "backups"
    owner       = "coolbits"
    cost_center = "infrastructure"
    compliance  = "encrypted"
  }
}

# KMS Key for backup encryption
resource "google_kms_key_ring" "coolbits_backup_keyring" {
  name     = "coolbits-backup-keyring"
  location = var.region
  
  labels = {
    env         = var.environment
    service     = "backup-keyring"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_kms_crypto_key" "coolbits_backup_key" {
  name            = "coolbits-backup-key"
  key_ring        = google_kms_key_ring.coolbits_backup_keyring.id
  rotation_period = "7776000s" # 90 days
  
  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
  
  labels = {
    env         = var.environment
    service     = "backup-key"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud Function for automated backups
resource "google_cloudfunctions_function" "coolbits_backup_function" {
  name        = "coolbits-backup-function"
  description = "Automated backup function for CoolBits infrastructure"
  runtime     = "python39"
  
  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.coolbits_backups_reality.name
  source_archive_object = google_storage_bucket_object.coolbits_backup_code.name
  entry_point          = "backup_handler"
  
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.coolbits_backup_topic.name
  }
  
  environment_variables = {
    PROJECT_ID        = var.project_id
    BACKUP_BUCKET     = google_storage_bucket.coolbits_backups_reality.name
    DB_INSTANCE_NAME  = google_sql_database_instance.coolbits_db_primary.name
    REDIS_INSTANCE    = google_redis_instance.coolbits_redis.name
    KMS_KEY_NAME      = google_kms_crypto_key.coolbits_backup_key.id
  }
  
  labels = {
    env         = var.environment
    service     = "backup-function"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Backup code with encryption
resource "google_storage_bucket_object" "coolbits_backup_code" {
  name   = "backup_function.zip"
  bucket = google_storage_bucket.coolbits_backups_reality.name
  source = "backup_function.zip"
}

# Pub/Sub Topic for Backup Triggers
resource "google_pubsub_topic" "coolbits_backup_topic" {
  name = "coolbits-backup-topic"
  
  labels = {
    env         = var.environment
    service     = "backup-topic"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud Scheduler for Automated Backups
resource "google_cloud_scheduler_job" "coolbits_daily_backup" {
  name        = "coolbits-daily-backup"
  description = "Daily backup job for CoolBits infrastructure"
  schedule    = "0 2 * * *" # Daily at 2 AM
  time_zone   = "Europe/Bucharest"
  
  pubsub_target {
    topic_name = google_pubsub_topic.coolbits_backup_topic.id
    data       = base64encode(jsonencode({
      backup_type = "daily"
      timestamp   = "{{.timestamp}}"
    }))
  }
  
  labels = {
    env         = var.environment
    service     = "daily-backup"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Outputs for M8 verification
output "backup_bucket_name" {
  description = "Name of the backup bucket for M8 verification"
  value       = google_storage_bucket.coolbits_backups_reality.name
}

output "kms_key_name" {
  description = "KMS key name for encryption verification"
  value       = google_kms_crypto_key.coolbits_backup_key.id
}
