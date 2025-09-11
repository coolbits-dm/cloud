# CoolBits.ai Disaster Recovery and Automated Backups
# ====================================================

# Cloud Storage Bucket for Backups
resource "google_storage_bucket" "coolbits_backups" {
  name          = "coolbits-backups-${var.project_id}"
  location      = "EU"
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  # Versioning
  versioning {
    enabled = true
  }
  
  # Lifecycle rules
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
  
  # Encryption
  encryption {
    default_kms_key_name = google_kms_crypto_key.coolbits_backup_key.id
  }
  
  labels = {
    env         = var.environment
    service     = "backups"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# KMS Key for Backup Encryption
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

# Cloud Function for Automated Backups
resource "google_cloudfunctions_function" "coolbits_backup_function" {
  name        = "coolbits-backup-function"
  description = "Automated backup function for CoolBits infrastructure"
  runtime     = "python39"
  
  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.coolbits_backups.name
  source_archive_object = google_storage_bucket_object.coolbits_backup_code.name
  entry_point          = "backup_handler"
  
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.coolbits_backup_topic.name
  }
  
  environment_variables = {
    PROJECT_ID        = var.project_id
    BACKUP_BUCKET     = google_storage_bucket.coolbits_backups.name
    DB_INSTANCE_NAME  = google_sql_database_instance.coolbits_db_primary.name
    REDIS_INSTANCE    = google_redis_instance.coolbits_redis.name
  }
  
  labels = {
    env         = var.environment
    service     = "backup-function"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Backup Code
resource "google_storage_bucket_object" "coolbits_backup_code" {
  name   = "backup_function.zip"
  bucket = google_storage_bucket.coolbits_backups.name
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

resource "google_cloud_scheduler_job" "coolbits_weekly_backup" {
  name        = "coolbits-weekly-backup"
  description = "Weekly backup job for CoolBits infrastructure"
  schedule    = "0 3 * * 0" # Weekly on Sunday at 3 AM
  time_zone   = "Europe/Bucharest"
  
  pubsub_target {
    topic_name = google_pubsub_topic.coolbits_backup_topic.id
    data       = base64encode(jsonencode({
      backup_type = "weekly"
      timestamp   = "{{.timestamp}}"
    }))
  }
  
  labels = {
    env         = var.environment
    service     = "weekly-backup"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud Function for Disaster Recovery
resource "google_cloudfunctions_function" "coolbits_disaster_recovery" {
  name        = "coolbits-disaster-recovery"
  description = "Disaster recovery function for CoolBits infrastructure"
  runtime     = "python39"
  
  available_memory_mb   = 1024
  source_archive_bucket = google_storage_bucket.coolbits_backups.name
  source_archive_object = google_storage_bucket_object.coolbits_dr_code.name
  entry_point          = "disaster_recovery_handler"
  
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.coolbits_dr_topic.name
  }
  
  environment_variables = {
    PROJECT_ID        = var.project_id
    BACKUP_BUCKET     = google_storage_bucket.coolbits_backups.name
    PRIMARY_REGION    = var.region
    DR_REGION         = var.dr_region
    DB_INSTANCE_NAME  = google_sql_database_instance.coolbits_db_primary.name
    REDIS_INSTANCE    = google_redis_instance.coolbits_redis.name
  }
  
  labels = {
    env         = var.environment
    service     = "disaster-recovery"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Disaster Recovery Code
resource "google_storage_bucket_object" "coolbits_dr_code" {
  name   = "disaster_recovery_function.zip"
  bucket = google_storage_bucket.coolbits_backups.name
  source = "disaster_recovery_function.zip"
}

# Pub/Sub Topic for Disaster Recovery
resource "google_pubsub_topic" "coolbits_dr_topic" {
  name = "coolbits-disaster-recovery-topic"
  
  labels = {
    env         = var.environment
    service     = "dr-topic"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Disaster Recovery Region Resources
resource "google_compute_network" "coolbits_dr_vpc" {
  name                    = "coolbits-dr-vpc"
  auto_create_subnetwork  = false
  routing_mode           = "REGIONAL"
  
  labels = {
    env         = var.environment
    service     = "dr-vpc"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_compute_subnetwork" "coolbits_dr_subnet" {
  name          = "coolbits-dr-subnet"
  ip_cidr_range = "10.1.0.0/24"
  region        = var.dr_region
  network       = google_compute_network.coolbits_dr_vpc.id
  
  private_ip_google_access = true
  
  labels = {
    env         = var.environment
    service     = "dr-subnet"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud SQL Instance (Disaster Recovery)
resource "google_sql_database_instance" "coolbits_db_dr" {
  name             = "coolbits-db-dr"
  database_version = "POSTGRES_15"
  region          = var.dr_region
  
  settings {
    tier                        = "db-standard-2"
    availability_type           = "REGIONAL"
    disk_type                  = "SSD"
    disk_size                  = 100
    disk_autoresize            = true
    disk_autoresize_limit      = 500
    
    # Backup configuration
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      location                       = var.dr_region
      point_in_time_recovery_enabled = true
      transaction_log_retention_days  = 7
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }
    
    # High availability
    replication_type = "SYNCHRONOUS"
    
    # Maintenance window
    maintenance_window {
      day          = 7
      hour         = 3
      update_track = "stable"
    }
    
    # IP configuration
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.coolbits_dr_vpc.id
      require_ssl     = true
    }
  }
  
  deletion_protection = false
  
  labels = {
    env         = var.environment
    service     = "database-dr"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Redis Instance (Disaster Recovery)
resource "google_redis_instance" "coolbits_redis_dr" {
  name           = "coolbits-redis-dr"
  tier           = "STANDARD_HA"
  memory_size_gb = 4
  region         = var.dr_region
  
  redis_version     = "REDIS_7_0"
  auth_enabled      = true
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  
  authorized_network = google_compute_network.coolbits_dr_vpc.id
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
        seconds = 0
        nanos   = 0
      }
    }
  }
  
  labels = {
    env         = var.environment
    service     = "redis-dr"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Backup Monitoring and Alerting
resource "google_monitoring_alert_policy" "coolbits_backup_failure" {
  display_name = "CoolBits Backup Failure"
  combiner     = "OR"
  
  conditions {
    display_name = "Backup function failed"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_function\" AND resource.labels.function_name=\"coolbits-backup-function\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.coolbits_email_alerts.name,
    google_monitoring_notification_channel.coolbits_slack_alerts.name
  ]
  
  alert_strategy {
    auto_close = "1800s"
  }
  
  labels = {
    env         = var.environment
    service     = "backup-failure-alert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_monitoring_alert_policy" "coolbits_backup_storage_quota" {
  display_name = "CoolBits Backup Storage Quota"
  combiner     = "OR"
  
  conditions {
    display_name = "Backup storage quota exceeded"
    
    condition_threshold {
      filter          = "resource.type=\"gcs_bucket\" AND resource.labels.bucket_name=\"coolbits-backups-${var.project_id}\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 90
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.coolbits_email_alerts.name,
    google_monitoring_notification_channel.coolbits_slack_alerts.name
  ]
  
  alert_strategy {
    auto_close = "1800s"
  }
  
  labels = {
    env         = var.environment
    service     = "backup-storage-alert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Backup Retention Policy
resource "google_storage_bucket" "coolbits_backup_retention" {
  name          = "coolbits-backup-retention-${var.project_id}"
  location      = "EU"
  force_destroy = false
  
  uniform_bucket_level_access = true
  
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
  
  labels = {
    env         = var.environment
    service     = "backup-retention"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Variables
variable "dr_region" {
  description = "Disaster recovery region"
  type        = string
  default     = "europe-west1"
}

# Outputs
output "backup_bucket_name" {
  description = "Name of the backup bucket"
  value       = google_storage_bucket.coolbits_backups.name
}

output "backup_function_name" {
  description = "Name of the backup function"
  value       = google_cloudfunctions_function.coolbits_backup_function.name
}

output "dr_region" {
  description = "Disaster recovery region"
  value       = var.dr_region
}

output "backup_schedule" {
  description = "Backup schedule"
  value       = {
    daily  = google_cloud_scheduler_job.coolbits_daily_backup.schedule
    weekly = google_cloud_scheduler_job.coolbits_weekly_backup.schedule
  }
}
