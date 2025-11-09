# CoolBits.ai Cloud Armor Security Configuration
# ===============================================

# Cloud Armor Security Policy
resource "google_compute_security_policy" "coolbits_security_policy" {
  name = "coolbits-security-policy"
  
  # Default rule (allow all)
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default rule - allow all traffic"
  }
  
  # DDoS Protection
  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      expr {
        expression = "origin.region_code == 'CN' || origin.region_code == 'RU'"
      }
    }
    description = "Block traffic from high-risk regions"
  }
  
  # Rate Limiting
  rule {
    action   = "rate_based_ban"
    priority = "2000"
    match {
      expr {
        expression = "true"
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      rate_limit_threshold {
        count        = 100
        interval_sec  = 60
      }
      ban_duration_sec = 300
    }
    description = "Rate limiting - 100 requests per minute per IP"
  }
  
  # SQL Injection Protection
  rule {
    action   = "deny(403)"
    priority = "3000"
    match {
      expr {
        expression = "request.path.matches('.*(union|select|insert|delete|update|drop|create|alter|exec|script).*')"
      }
    }
    description = "Block SQL injection attempts"
  }
  
  # XSS Protection
  rule {
    action   = "deny(403)"
    priority = "4000"
    match {
      expr {
        expression = "request.headers['user-agent'].contains('<script>') || request.query_string.contains('<script>')"
      }
    }
    description = "Block XSS attempts"
  }
  
  # Path Traversal Protection
  rule {
    action   = "deny(403)"
    priority = "5000"
    match {
      expr {
        expression = "request.path.contains('..') || request.path.contains('//')"
      }
    }
    description = "Block path traversal attempts"
  }
  
  # Bot Protection
  rule {
    action   = "deny(403)"
    priority = "6000"
    match {
      expr {
        expression = "request.headers['user-agent'].matches('.*bot.*|.*crawler.*|.*spider.*') && !request.headers['user-agent'].matches('.*Googlebot.*|.*Bingbot.*')"
      }
    }
    description = "Block malicious bots (allow search engine bots)"
  }
  
  # API Rate Limiting (stricter)
  rule {
    action   = "rate_based_ban"
    priority = "7000"
    match {
      expr {
        expression = "request.path.matches('/api/.*')"
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      rate_limit_threshold {
        count        = 50
        interval_sec  = 60
      }
      ban_duration_sec = 600
    }
    description = "API rate limiting - 50 requests per minute per IP"
  }
  
  # Admin Panel Protection
  rule {
    action   = "deny(403)"
    priority = "8000"
    match {
      expr {
        expression = "request.path.matches('/admin/.*') && !origin.region_code.matches('RO|DE|FR|GB|US')"
      }
    }
    description = "Restrict admin panel access to specific regions"
  }
  
  # Allowlist for trusted IPs
  rule {
    action   = "allow"
    priority = "100"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = var.trusted_ips
      }
    }
    description = "Allow trusted IP addresses"
  }
  
  labels = {
    env         = var.environment
    service     = "security-policy"
    owner       = "coolbits"
    cost_center = "security"
  }
}

# Cloud Armor Backend Security Policy
resource "google_compute_backend_service" "coolbits_backend_with_armor" {
  name                  = "coolbits-backend-service-armor"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  timeout_sec           = 30
  
  # Health check
  health_checks = [google_compute_health_check.coolbits_health_check.id]
  
  # Cloud Run NEG
  backend {
    group = google_compute_region_network_endpoint_group.coolbits_neg.id
  }
  
  # Security policy
  security_policy = google_compute_security_policy.coolbits_security_policy.id
  
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
    service     = "backend-armor"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# WAF (Web Application Firewall) Rules
resource "google_compute_security_policy" "coolbits_waf_policy" {
  name = "coolbits-waf-policy"
  
  # OWASP Top 10 Protection
  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      expr {
        expression = <<-EOT
          request.path.matches('.*(union|select|insert|delete|update|drop|create|alter|exec|script|javascript|vbscript|onload|onerror|onclick).*') ||
          request.query_string.matches('.*(union|select|insert|delete|update|drop|create|alter|exec|script|javascript|vbscript|onload|onerror|onclick).*') ||
          request.headers['user-agent'].matches('.*(union|select|insert|delete|update|drop|create|alter|exec|script|javascript|vbscript|onload|onerror|onclick).*')
        EOT
      }
    }
    description = "OWASP Top 10 - Injection attacks"
  }
  
  # Broken Authentication Protection
  rule {
    action   = "deny(403)"
    priority = "2000"
    match {
      expr {
        expression = "request.path.matches('/api/auth/.*') && request.headers['authorization'].size() == 0"
      }
    }
    description = "Broken Authentication - Missing authorization header"
  }
  
  # Sensitive Data Exposure Protection
  rule {
    action   = "deny(403)"
    priority = "3000"
    match {
      expr {
        expression = "request.path.matches('.*\\.(env|config|key|pem|p12|pfx|jks|keystore).*')"
      }
    }
    description = "Sensitive Data Exposure - Block config files"
  }
  
  # XML External Entities (XXE) Protection
  rule {
    action   = "deny(403)"
    priority = "4000"
    match {
      expr {
        expression = "request.headers['content-type'].matches('.*xml.*') && request.body.matches('.*<!DOCTYPE.*SYSTEM.*>.*')"
      }
    }
    description = "XXE Protection - Block malicious XML"
  }
  
  # Broken Access Control Protection
  rule {
    action   = "deny(403)"
    priority = "5000"
    match {
      expr {
        expression = "request.path.matches('/admin/.*') && !request.headers['x-admin-token'].matches('.*')"
      }
    }
    description = "Broken Access Control - Admin panel protection"
  }
  
  # Security Misconfiguration Protection
  rule {
    action   = "deny(403)"
    priority = "6000"
    match {
      expr {
        expression = "request.path.matches('.*(phpmyadmin|adminer|wp-admin|administrator|manager|login).*')"
      }
    }
    description = "Security Misconfiguration - Block common admin paths"
  }
  
  # Cross-Site Scripting (XSS) Protection
  rule {
    action   = "deny(403)"
    priority = "7000"
    match {
      expr {
        expression = <<-EOT
          request.query_string.matches('.*<script.*>.*</script>.*') ||
          request.body.matches('.*<script.*>.*</script>.*') ||
          request.headers['referer'].matches('.*<script.*>.*</script>.*')
        EOT
      }
    }
    description = "XSS Protection - Block script tags"
  }
  
  # Insecure Deserialization Protection
  rule {
    action   = "deny(403)"
    priority = "8000"
    match {
      expr {
        expression = "request.headers['content-type'].matches('.*application/java.*') || request.headers['content-type'].matches('.*application/x-java.*')"
      }
    }
    description = "Insecure Deserialization - Block Java serialization"
  }
  
  # Using Components with Known Vulnerabilities Protection
  rule {
    action   = "deny(403)"
    priority = "9000"
    match {
      expr {
        expression = "request.headers['user-agent'].matches('.*(curl|wget|python-requests|go-http-client).*') && request.path.matches('/api/.*')"
      }
    }
    description = "Known Vulnerabilities - Block suspicious user agents for API"
  }
  
  # Insufficient Logging & Monitoring Protection
  rule {
    action   = "deny(403)"
    priority = "10000"
    match {
      expr {
        expression = "request.path.matches('.*(logs|log|debug|trace|monitor).*')"
      }
    }
    description = "Insufficient Logging - Block log access attempts"
  }
  
  labels = {
    env         = var.environment
    service     = "waf-policy"
    owner       = "coolbits"
    cost_center = "security"
  }
}

# Variables
variable "trusted_ips" {
  description = "List of trusted IP addresses"
  type        = list(string)
  default     = [
    "0.0.0.0/0"  # Allow all for now, should be restricted in production
  ]
}

# Outputs
output "security_policy_name" {
  description = "Name of the Cloud Armor security policy"
  value       = google_compute_security_policy.coolbits_security_policy.name
}

output "waf_policy_name" {
  description = "Name of the WAF policy"
  value       = google_compute_security_policy.coolbits_waf_policy.name
}
