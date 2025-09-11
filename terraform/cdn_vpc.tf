# CoolBits.ai CDN and VPC Configuration
# ======================================

# Cloud CDN Configuration
resource "google_compute_backend_service" "coolbits_cdn_backend_service" {
  name                  = "coolbits-cdn-backend-service"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  timeout_sec           = 30
  
  # CDN Configuration
  enable_cdn = true
  
  cdn_policy {
    cache_mode                   = "CACHE_ALL_STATIC"
    default_ttl                  = 3600
    client_ttl                   = 3600
    max_ttl                      = 86400
    negative_caching             = true
    serve_while_stale            = 86400
    
    # Cache key policy
    cache_key_policy {
      include_host                = true
      include_protocol            = true
      include_query_string        = false
      query_string_blacklist      = ["utm_source", "utm_medium", "utm_campaign"]
    }
    
    # Negative caching policy
    negative_caching_policy {
      code = 404
      ttl  = 60
    }
    
    negative_caching_policy {
      code = 403
      ttl  = 60
    }
  }
  
  # Backend bucket for static content
  backend {
    group = google_compute_backend_bucket.coolbits_static_backend.id
  }
  
  log_config {
    enable      = true
    sample_rate = 1.0
  }
  
  labels = {
    env         = var.environment
    service     = "cdn-backend"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Backend Bucket for Static Content
resource "google_compute_backend_bucket" "coolbits_static_backend" {
  name        = "coolbits-static-backend"
  bucket_name = google_storage_bucket.coolbits_static_content.name
  enable_cdn  = true
  
  cdn_policy {
    cache_mode                   = "CACHE_ALL_STATIC"
    default_ttl                  = 3600
    client_ttl                   = 3600
    max_ttl                      = 86400
    negative_caching             = true
    serve_while_stale            = 86400
    
    cache_key_policy {
      include_host                = true
      include_protocol            = true
      include_query_string        = false
    }
    
    negative_caching_policy {
      code = 404
      ttl  = 60
    }
  }
  
  labels = {
    env         = var.environment
    service     = "static-backend"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud Storage Bucket for Static Content
resource "google_storage_bucket" "coolbits_static_content" {
  name          = "coolbits-static-content-${var.project_id}"
  location      = "EU"
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  # CORS configuration
  cors {
    origin          = ["https://coolbits.ai", "https://www.coolbits.ai", "https://dev.coolbits.ai"]
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
  
  # Lifecycle rules
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  # Versioning
  versioning {
    enabled = true
  }
  
  labels = {
    env         = var.environment
    service     = "static-content"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# VPC Network
resource "google_compute_network" "coolbits_vpc" {
  name                    = "coolbits-vpc"
  auto_create_subnetwork  = false
  routing_mode           = "REGIONAL"
  
  labels = {
    env         = var.environment
    service     = "vpc"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Subnet for Cloud Run
resource "google_compute_subnetwork" "coolbits_subnet" {
  name          = "coolbits-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.coolbits_vpc.id
  
  # Private Google Access
  private_ip_google_access = true
  
  # Secondary IP ranges for GKE (if needed)
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }
  
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/16"
  }
  
  labels = {
    env         = var.environment
    service     = "subnet"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# VPC Connector for Cloud Run
resource "google_vpc_access_connector" "coolbits_connector" {
  name          = "coolbits-vpc-connector"
  region        = var.region
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.coolbits_vpc.name
  
  min_instances = 2
  max_instances = 10
  
  labels = {
    env         = var.environment
    service     = "vpc-connector"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud NAT for outbound traffic
resource "google_compute_router" "coolbits_router" {
  name    = "coolbits-router"
  region  = var.region
  network = google_compute_network.coolbits_vpc.id
  
  bgp {
    asn = 64514
  }
  
  labels = {
    env         = var.environment
    service     = "router"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_compute_router_nat" "coolbits_nat" {
  name                               = "coolbits-nat"
  router                            = google_compute_router.coolbits_router.name
  region                            = var.region
  nat_ip_allocate_option            = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
  
  labels = {
    env         = var.environment
    service     = "nat"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Firewall Rules
resource "google_compute_firewall" "coolbits_allow_internal" {
  name    = "coolbits-allow-internal"
  network = google_compute_network.coolbits_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "icmp"
  }
  
  source_ranges = ["10.0.0.0/24", "10.1.0.0/16", "10.2.0.0/16"]
  
  labels = {
    env         = var.environment
    service     = "firewall-internal"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_compute_firewall" "coolbits_allow_health_check" {
  name    = "coolbits-allow-health-check"
  network = google_compute_network.coolbits_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8501"]
  }
  
  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]
  target_tags   = ["coolbits-health-check"]
  
  labels = {
    env         = var.environment
    service     = "firewall-health-check"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud Run Service with VPC Connector
resource "google_cloud_run_service" "coolbits_production_vpc" {
  name     = "coolbits-production-vpc"
  location = var.region
  
  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"        = "50"
        "autoscaling.knative.dev/minScale"        = "2"
        "run.googleapis.com/cpu-throttling"      = "false"
        "run.googleapis.com/execution-environment" = "gen2"
        "run.googleapis.com/vpc-access-connector"  = google_vpc_access_connector.coolbits_connector.name
        "run.googleapis.com/vpc-access-egress"    = "private-ranges-only"
      }
      
      labels = {
        env         = var.environment
        service     = "production-vpc"
        owner       = "coolbits"
        cost_center = "infrastructure"
      }
    }
    
    spec {
      container_concurrency = 200
      timeout_seconds      = 300
      
      containers {
        image = "gcr.io/${var.project_id}/coolbits:production"
        
        ports {
          container_port = 8501
          name          = "http1"
        }
        
        env {
          name  = "OPIPE_ENV"
          value = "production"
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "VPC_CONNECTOR"
          value = google_vpc_access_connector.coolbits_connector.name
        }
        
        resources {
          limits = {
            cpu    = "4"
            memory = "8Gi"
          }
          requests = {
            cpu    = "2"
            memory = "4Gi"
          }
        }
        
        liveness_probe {
          http_get {
            path = "/_stcore/health"
            port = 8501
          }
          initial_delay_seconds = 30
          period_seconds        = 10
          timeout_seconds       = 5
          failure_threshold     = 3
        }
        
        readiness_probe {
          http_get {
            path = "/_stcore/health"
            port = 8501
          }
          initial_delay_seconds = 10
          period_seconds        = 5
          timeout_seconds       = 3
          failure_threshold     = 3
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  labels = {
    env         = var.environment
    service     = "production-vpc"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Outputs
output "vpc_network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.coolbits_vpc.name
}

output "vpc_connector_name" {
  description = "Name of the VPC connector"
  value       = google_vpc_access_connector.coolbits_connector.name
}

output "static_content_bucket" {
  description = "Name of the static content bucket"
  value       = google_storage_bucket.coolbits_static_content.name
}

output "cdn_backend_service" {
  description = "Name of the CDN backend service"
  value       = google_compute_backend_service.coolbits_cdn_backend_service.name
}
