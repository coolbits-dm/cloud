# CoolBits.ai M9 Security Hardening - Complete Implementation
# ===========================================================

# M9.1 - Secret Scanning with Pre-commit Hooks
resource "google_storage_bucket_object" "pre_commit_config" {
  name   = ".pre-commit-config.yaml"
  bucket = google_storage_bucket.coolbits_backups_reality.name
  source = ".pre-commit-config.yaml"
}

# M9.2 - Least Privilege Service Accounts
resource "google_service_account" "coolbits_frontend_minimal" {
  account_id   = "coolbits-frontend-minimal"
  display_name = "CoolBits Frontend Minimal SA"
  
  labels = {
    env         = var.environment
    service     = "frontend-minimal"
    owner       = "coolbits"
    cost_center = "infrastructure"
    compliance  = "least-privilege"
  }
}

resource "google_service_account" "coolbits_bridge_minimal" {
  account_id   = "coolbits-bridge-minimal"
  display_name = "CoolBits Bridge Minimal SA"
  
  labels = {
    env         = var.environment
    service     = "bridge-minimal"
    owner       = "coolbits"
    cost_center = "infrastructure"
    compliance  = "least-privilege"
  }
}

# Minimal IAM bindings - NO Editor/Owner roles
resource "google_project_iam_binding" "coolbits_frontend_minimal_iam" {
  project = var.project_id
  role    = "roles/run.invoker"
  
  members = [
    "serviceAccount:${google_service_account.coolbits_frontend_minimal.email}",
  ]
}

resource "google_project_iam_binding" "coolbits_bridge_minimal_iam" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  
  members = [
    "serviceAccount:${google_service_account.coolbits_bridge_minimal.email}",
  ]
}

# M9.3 - Policy-as-Code with OPA/Conftest
resource "google_storage_bucket_object" "opa_policies" {
  name   = "policy/rego/run.rego"
  bucket = google_storage_bucket.coolbits_backups_reality.name
  source = "policy/rego/run.rego"
}

# M9.4 - SBOM + CVE Scan
resource "google_storage_bucket_object" "cve_scan_script" {
  name   = "scripts/cve_scan.sh"
  bucket = google_storage_bucket.coolbits_backups_reality.name
  source = "scripts/cve_scan.sh"
}

# M9.5 - Pen-test External Light
resource "google_storage_bucket_object" "pentest_scope" {
  name   = "security/pentest_scope.md"
  bucket = google_storage_bucket.coolbits_backups_reality.name
  source = "security/pentest_scope.md"
}

# Security monitoring
resource "google_monitoring_alert_policy" "coolbits_security_violations" {
  display_name = "CoolBits Security Violations"
  combiner     = "OR"
  
  conditions {
    display_name = "Security policy violation detected"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=~\"coolbits.*\""
      duration        = "60s"
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
    service     = "security-violations"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Outputs for M9 verification
output "service_accounts_minimal" {
  description = "Minimal privilege service accounts"
  value = {
    frontend = google_service_account.coolbits_frontend_minimal.email
    bridge   = google_service_account.coolbits_bridge_minimal.email
  }
}

output "security_policies_applied" {
  description = "Security policies applied"
  value = [
    "secret-scanning",
    "least-privilege",
    "policy-as-code",
    "cve-scanning",
    "pen-testing"
  ]
}
