# CoolBits.ai HTTP(S) Load Balancer Configuration
# ================================================

# Global HTTP(S) Load Balancer
resource "google_compute_global_address" "coolbits_lb_ip" {
  name         = "coolbits-lb-ip"
  ip_version   = "IPV4"
  address_type = "EXTERNAL"
  
  labels = {
    env         = var.environment
    service     = "load-balancer"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Backend Service for Cloud Run
resource "google_compute_backend_service" "coolbits_backend" {
  name                  = "coolbits-backend-service"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  timeout_sec           = 30
  
  # Health check
  health_checks = [google_compute_health_check.coolbits_health_check.id]
  
  # Cloud Run NEG (Network Endpoint Group)
  backend {
    group = google_compute_region_network_endpoint_group.coolbits_neg.id
  }
  
  # Load balancing policy
  locality_lb_policy = "ROUND_ROBIN"
  
  # Session affinity
  session_affinity = "NONE"
  
  # Connection draining
  connection_draining_timeout_sec = 30
  
  log_config {
    enable      = true
    sample_rate = 1.0
  }
  
  labels = {
    env         = var.environment
    service     = "backend"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Network Endpoint Group for Cloud Run
resource "google_compute_region_network_endpoint_group" "coolbits_neg" {
  name                  = "coolbits-neg"
  network_endpoint_type = "SERVERLESS"
  region               = var.region
  
  cloud_run {
    service = google_cloud_run_service.coolbits_production.name
  }
  
  labels = {
    env         = var.environment
    service     = "neg"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Health Check
resource "google_compute_health_check" "coolbits_health_check" {
  name               = "coolbits-health-check"
  check_interval_sec = 10
  timeout_sec        = 5
  healthy_threshold  = 2
  unhealthy_threshold = 3
  
  http_health_check {
    request_path = "/_stcore/health"
    port         = "8501"
  }
  
  labels = {
    env         = var.environment
    service     = "health-check"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# URL Map
resource "google_compute_url_map" "coolbits_url_map" {
  name            = "coolbits-url-map"
  default_service = google_compute_backend_service.coolbits_backend.id
  
  # Host rules
  host_rule {
    hosts        = ["coolbits.ai", "www.coolbits.ai", "dev.coolbits.ai"]
    path_matcher = "coolbits-paths"
  }
  
  # Path matcher
  path_matcher {
    name            = "coolbits-paths"
    default_service = google_compute_backend_service.coolbits_backend.id
    
    # API routes
    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.coolbits_backend.id
    }
    
    # Admin routes
    path_rule {
      paths   = ["/admin/*"]
      service = google_compute_backend_service.coolbits_backend.id
    }
    
    # Static content (CDN)
    path_rule {
      paths   = ["/static/*", "/assets/*", "/*.css", "/*.js", "/*.png", "/*.jpg", "/*.ico"]
      service = google_compute_backend_service.coolbits_cdn_backend.id
    }
  }
  
  labels = {
    env         = var.environment
    service     = "url-map"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# HTTPS Proxy
resource "google_compute_target_https_proxy" "coolbits_https_proxy" {
  name             = "coolbits-https-proxy"
  url_map          = google_compute_url_map.coolbits_url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.coolbits_ssl_cert.id]
  
  labels = {
    env         = var.environment
    service     = "https-proxy"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# HTTP Proxy (redirect to HTTPS)
resource "google_compute_target_http_proxy" "coolbits_http_proxy" {
  name    = "coolbits-http-proxy"
  url_map = google_compute_url_map.coolbits_http_redirect.id
  
  labels = {
    env         = var.environment
    service     = "http-proxy"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# HTTP to HTTPS redirect URL map
resource "google_compute_url_map" "coolbits_http_redirect" {
  name = "coolbits-http-redirect"
  
  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
  
  labels = {
    env         = var.environment
    service     = "http-redirect"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# SSL Certificate
resource "google_compute_managed_ssl_certificate" "coolbits_ssl_cert" {
  name = "coolbits-ssl-cert"
  
  managed {
    domains = ["coolbits.ai", "www.coolbits.ai", "dev.coolbits.ai"]
  }
  
  labels = {
    env         = var.environment
    service     = "ssl-cert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Global Forwarding Rule (HTTPS)
resource "google_compute_global_forwarding_rule" "coolbits_https_forwarding" {
  name       = "coolbits-https-forwarding"
  target     = google_compute_target_https_proxy.coolbits_https_proxy.id
  port_range = "443"
  ip_address = google_compute_global_address.coolbits_lb_ip.address
  
  labels = {
    env         = var.environment
    service     = "https-forwarding"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Global Forwarding Rule (HTTP)
resource "google_compute_global_forwarding_rule" "coolbits_http_forwarding" {
  name       = "coolbits-http-forwarding"
  target     = google_compute_target_http_proxy.coolbits_http_proxy.id
  port_range = "80"
  ip_address = google_compute_global_address.coolbits_lb_ip.address
  
  labels = {
    env         = var.environment
    service     = "http-forwarding"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# CDN Backend Service for static content
resource "google_compute_backend_bucket" "coolbits_cdn_backend" {
  name        = "coolbits-cdn-backend"
  bucket_name = google_storage_bucket.coolbits_static_content.name
  enable_cdn  = true
  
  cdn_policy {
    cache_mode                   = "CACHE_ALL_STATIC"
    default_ttl                  = 3600
    client_ttl                   = 3600
    max_ttl                      = 86400
    negative_caching             = true
    serve_while_stale            = 86400
    negative_caching_policy {
      code = 404
      ttl  = 60
    }
  }
  
  labels = {
    env         = var.environment
    service     = "cdn-backend"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Cloud Storage bucket for static content
resource "google_storage_bucket" "coolbits_static_content" {
  name          = "coolbits-static-content-${var.project_id}"
  location      = "EU"
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  cors {
    origin          = ["https://coolbits.ai", "https://www.coolbits.ai", "https://dev.coolbits.ai"]
    method          = ["GET", "HEAD"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    env         = var.environment
    service     = "static-content"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Outputs
output "load_balancer_ip" {
  description = "IP address of the load balancer"
  value       = google_compute_global_address.coolbits_lb_ip.address
}

output "load_balancer_url" {
  description = "URL of the load balancer"
  value       = "https://${google_compute_global_address.coolbits_lb_ip.address}"
}
