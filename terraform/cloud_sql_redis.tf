# CoolBits.ai Cloud SQL High Availability Configuration
# =====================================================

# Cloud SQL Instance (Primary)
resource "google_sql_database_instance" "coolbits_db_primary" {
  name             = "coolbits-db-primary"
  database_version = "POSTGRES_15"
  region          = var.region
  
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
      location                       = var.region
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
      private_network = google_compute_network.coolbits_vpc.id
      require_ssl     = true
      
      authorized_networks {
        name  = "vpc-connector"
        value = google_vpc_access_connector.coolbits_connector.ip_cidr_range
      }
    }
    
    # Database flags
    database_flags {
      name  = "log_statement"
      value = "all"
    }
    
    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"
    }
    
    database_flags {
      name  = "shared_preload_libraries"
      value = "pg_stat_statements"
    }
    
    # Insights configuration
    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }
    
    # Performance insights
    performance_insights_config {
      query_insights_enabled = true
    }
  }
  
  deletion_protection = true
  
  labels = {
    env         = var.environment
    service     = "database-primary"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud SQL Instance (Read Replica)
resource "google_sql_database_instance" "coolbits_db_replica" {
  name                 = "coolbits-db-replica"
  database_version     = "POSTGRES_15"
  region              = var.replica_region
  master_instance_name = google_sql_database_instance.coolbits_db_primary.name
  replica_configuration {
    failover_target = true
  }
  
  settings {
    tier                        = "db-standard-1"
    availability_type           = "ZONAL"
    disk_type                  = "SSD"
    disk_size                  = 100
    disk_autoresize            = true
    disk_autoresize_limit      = 500
    
    # IP configuration
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.coolbits_vpc.id
      require_ssl     = true
    }
    
    # Maintenance window
    maintenance_window {
      day          = 7
      hour         = 4
      update_track = "stable"
    }
  }
  
  deletion_protection = false
  
  labels = {
    env         = var.environment
    service     = "database-replica"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Database
resource "google_sql_database" "coolbits_database" {
  name     = "coolbits"
  instance = google_sql_database_instance.coolbits_db_primary.name
  
  depends_on = [google_sql_database_instance.coolbits_db_primary]
}

# Database User
resource "google_sql_user" "coolbits_user" {
  name     = "coolbits_user"
  instance = google_sql_database_instance.coolbits_db_primary.name
  password = var.db_password
  
  depends_on = [google_sql_database_instance.coolbits_db_primary]
}

# Database User for Read Replica
resource "google_sql_user" "coolbits_readonly_user" {
  name     = "coolbits_readonly"
  instance = google_sql_database_instance.coolbits_db_replica.name
  password = var.db_readonly_password
  
  depends_on = [google_sql_database_instance.coolbits_db_replica]
}

# Connection Pool
resource "google_sql_database_instance" "coolbits_db_pool" {
  name             = "coolbits-db-pool"
  database_version = "POSTGRES_15"
  region          = var.region
  
  settings {
    tier = "db-standard-1"
    
    # Connection pool settings
    database_flags {
      name  = "max_connections"
      value = "200"
    }
    
    database_flags {
      name  = "shared_buffers"
      value = "256MB"
    }
    
    database_flags {
      name  = "effective_cache_size"
      value = "1GB"
    }
    
    # IP configuration
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.coolbits_vpc.id
      require_ssl     = true
    }
  }
  
  deletion_protection = false
  
  labels = {
    env         = var.environment
    service     = "database-pool"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Redis Memorystore Instance
resource "google_redis_instance" "coolbits_redis" {
  name           = "coolbits-redis"
  tier           = "STANDARD_HA"
  memory_size_gb = 4
  region         = var.region
  
  # High availability
  redis_version     = "REDIS_7_0"
  auth_enabled      = true
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  
  # Network configuration
  authorized_network = google_compute_network.coolbits_vpc.id
  
  # Maintenance policy
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
    service     = "redis"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Redis Read Replica
resource "google_redis_instance" "coolbits_redis_replica" {
  name           = "coolbits-redis-replica"
  tier           = "STANDARD_HA"
  memory_size_gb = 2
  region         = var.replica_region
  
  # High availability
  redis_version     = "REDIS_7_0"
  auth_enabled      = true
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  
  # Network configuration
  authorized_network = google_compute_network.coolbits_vpc.id
  
  # Read replica configuration
  read_replicas_mode = "READ_REPLICAS_ENABLED"
  
  labels = {
    env         = var.environment
    service     = "redis-replica"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud SQL Proxy Configuration
resource "google_compute_instance" "coolbits_sql_proxy" {
  name         = "coolbits-sql-proxy"
  machine_type = "e2-micro"
  zone         = "${var.region}-a"
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 10
    }
  }
  
  network_interface {
    network    = google_compute_network.coolbits_vpc.name
    subnetwork = google_compute_subnetwork.coolbits_subnet.name
    
    access_config {
      // Ephemeral public IP
    }
  }
  
  metadata = {
    startup-script = <<-EOF
      #!/bin/bash
      apt-get update
      apt-get install -y wget
      
      # Download Cloud SQL Proxy
      wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
      chmod +x cloud_sql_proxy
      
      # Start Cloud SQL Proxy
      ./cloud_sql_proxy -instances=${google_sql_database_instance.coolbits_db_primary.connection_name}=tcp:5432 &
    EOF
  }
  
  service_account {
    email  = google_service_account.coolbits_sql_proxy.email
    scopes = ["cloud-platform"]
  }
  
  labels = {
    env         = var.environment
    service     = "sql-proxy"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Service Account for SQL Proxy
resource "google_service_account" "coolbits_sql_proxy" {
  account_id   = "coolbits-sql-proxy"
  display_name = "CoolBits SQL Proxy Service Account"
  
  labels = {
    env         = var.environment
    service     = "sql-proxy-sa"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# IAM Binding for SQL Proxy
resource "google_project_iam_binding" "coolbits_sql_proxy_iam" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  
  members = [
    "serviceAccount:${google_service_account.coolbits_sql_proxy.email}",
  ]
}

# Database Monitoring
resource "google_monitoring_notification_channel" "coolbits_db_alerts" {
  display_name = "CoolBits Database Alerts"
  type         = "email"
  
  labels = {
    email_address = var.alert_email
  }
  
  labels = {
    env         = var.environment
    service     = "db-alerts"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Database Uptime Check
resource "google_monitoring_uptime_check_config" "coolbits_db_uptime" {
  display_name = "CoolBits Database Uptime Check"
  timeout      = "10s"
  period       = "60s"
  
  tcp_check {
    port = 5432
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = google_sql_database_instance.coolbits_db_primary.private_ip_address
    }
  }
  
  labels = {
    env         = var.environment
    service     = "db-uptime"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Variables
variable "replica_region" {
  description = "Region for read replica"
  type        = string
  default     = "europe-west1"
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

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
}

# Outputs
output "db_primary_connection_name" {
  description = "Connection name for the primary database"
  value       = google_sql_database_instance.coolbits_db_primary.connection_name
}

output "db_replica_connection_name" {
  description = "Connection name for the read replica"
  value       = google_sql_database_instance.coolbits_db_replica.connection_name
}

output "redis_host" {
  description = "Redis host address"
  value       = google_redis_instance.coolbits_redis.host
}

output "redis_port" {
  description = "Redis port"
  value       = google_redis_instance.coolbits_redis.port
}

output "sql_proxy_ip" {
  description = "SQL Proxy instance IP"
  value       = google_compute_instance.coolbits_sql_proxy.network_interface[0].access_config[0].nat_ip
}
