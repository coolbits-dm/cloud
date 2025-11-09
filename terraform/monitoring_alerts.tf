# CoolBits.ai Comprehensive Monitoring and Alerting
# ==================================================

# Cloud Monitoring Workspace
resource "google_monitoring_workspace" "coolbits_workspace" {
  display_name = "CoolBits Monitoring Workspace"
  
  labels = {
    env         = var.environment
    service     = "monitoring-workspace"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Notification Channels
resource "google_monitoring_notification_channel" "coolbits_email_alerts" {
  display_name = "CoolBits Email Alerts"
  type         = "email"
  
  labels = {
    email_address = var.alert_email
  }
  
  labels = {
    env         = var.environment
    service     = "email-alerts"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_monitoring_notification_channel" "coolbits_slack_alerts" {
  display_name = "CoolBits Slack Alerts"
  type         = "slack"
  
  labels = {
    channel_name = var.slack_channel
    webhook_url  = var.slack_webhook_url
  }
  
  labels = {
    env         = var.environment
    service     = "slack-alerts"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Alert Policies for Cloud Run
resource "google_monitoring_alert_policy" "coolbits_cloud_run_high_cpu" {
  display_name = "CoolBits Cloud Run High CPU Usage"
  combiner     = "OR"
  
  conditions {
    display_name = "CPU usage is high"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"coolbits-production\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 80
      
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
    service     = "cloud-run-cpu-alert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_monitoring_alert_policy" "coolbits_cloud_run_high_memory" {
  display_name = "CoolBits Cloud Run High Memory Usage"
  combiner     = "OR"
  
  conditions {
    display_name = "Memory usage is high"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"coolbits-production\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 85
      
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
    service     = "cloud-run-memory-alert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_monitoring_alert_policy" "coolbits_cloud_run_high_error_rate" {
  display_name = "CoolBits Cloud Run High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate is high"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"coolbits-production\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 5
      
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
    service     = "cloud-run-error-alert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Alert Policies for Load Balancer
resource "google_monitoring_alert_policy" "coolbits_load_balancer_high_latency" {
  display_name = "CoolBits Load Balancer High Latency"
  combiner     = "OR"
  
  conditions {
    display_name = "Load balancer latency is high"
    
    condition_threshold {
      filter          = "resource.type=\"https_lb_rule\" AND resource.labels.url_map_name=\"coolbits-url-map\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 2000
      
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
    service     = "lb-latency-alert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Alert Policies for Database
resource "google_monitoring_alert_policy" "coolbits_db_high_cpu" {
  display_name = "CoolBits Database High CPU Usage"
  combiner     = "OR"
  
  conditions {
    display_name = "Database CPU usage is high"
    
    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND resource.labels.instance_name=\"coolbits-db-primary\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 80
      
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
    service     = "db-cpu-alert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_monitoring_alert_policy" "coolbits_db_high_connections" {
  display_name = "CoolBits Database High Connection Count"
  combiner     = "OR"
  
  conditions {
    display_name = "Database connection count is high"
    
    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND resource.labels.instance_name=\"coolbits-db-primary\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 80
      
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
    service     = "db-connections-alert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Alert Policies for Redis
resource "google_monitoring_alert_policy" "coolbits_redis_high_memory" {
  display_name = "CoolBits Redis High Memory Usage"
  combiner     = "OR"
  
  conditions {
    display_name = "Redis memory usage is high"
    
    condition_threshold {
      filter          = "resource.type=\"redis_instance\" AND resource.labels.instance_id=\"coolbits-redis\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 85
      
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
    service     = "redis-memory-alert"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Uptime Checks
resource "google_monitoring_uptime_check_config" "coolbits_main_uptime" {
  display_name = "CoolBits Main Application Uptime Check"
  timeout      = "10s"
  period       = "60s"
  
  http_check {
    path         = "/_stcore/health"
    port         = "443"
    use_ssl      = true
    request_method = "GET"
    
    headers = {
      "User-Agent" = "Google-Cloud-Monitoring"
    }
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "coolbits.ai"
    }
  }
  
  labels = {
    env         = var.environment
    service     = "main-uptime"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_monitoring_uptime_check_config" "coolbits_api_uptime" {
  display_name = "CoolBits API Uptime Check"
  timeout      = "10s"
  period       = "60s"
  
  http_check {
    path         = "/api/v1/health"
    port         = "443"
    use_ssl      = true
    request_method = "GET"
    
    headers = {
      "User-Agent" = "Google-Cloud-Monitoring"
    }
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "api.coolbits.ai"
    }
  }
  
  labels = {
    env         = var.environment
    service     = "api-uptime"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Log-based Metrics
resource "google_logging_metric" "coolbits_error_count" {
  name   = "coolbits_error_count"
  filter = "resource.type=\"cloud_run_revision\" AND severity>=ERROR"
  
  metric_descriptor {
    metric_kind = "COUNTER"
    value_type  = "INT64"
  }
  
  value_extractor = "EXTRACT(jsonPayload.message)"
  
  labels = {
    env         = var.environment
    service     = "error-metric"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

resource "google_logging_metric" "coolbits_request_count" {
  name   = "coolbits_request_count"
  filter = "resource.type=\"cloud_run_revision\" AND httpRequest.requestMethod=\"GET\""
  
  metric_descriptor {
    metric_kind = "COUNTER"
    value_type  = "INT64"
  }
  
  value_extractor = "EXTRACT(httpRequest.requestUrl)"
  
  labels = {
    env         = var.environment
    service     = "request-metric"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Dashboard
resource "google_monitoring_dashboard" "coolbits_dashboard" {
  dashboard_json = jsonencode({
    displayName = "CoolBits Infrastructure Dashboard"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Cloud Run CPU Usage"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"coolbits-production\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_MEAN"
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Cloud Run Memory Usage"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"coolbits-production\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_MEAN"
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Request Rate"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"coolbits-production\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Error Rate"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"coolbits-production\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        }
      ]
    }
  })
  
  labels = {
    env         = var.environment
    service     = "dashboard"
    owner       = "coolbits"
    cost_center = "infrastructure"
  }
}

# Variables
variable "slack_channel" {
  description = "Slack channel for alerts"
  type        = string
  default     = "#coolbits-alerts"
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alerts"
  type        = string
  sensitive   = true
}

# Outputs
output "monitoring_workspace_name" {
  description = "Name of the monitoring workspace"
  value       = google_monitoring_workspace.coolbits_workspace.name
}

output "dashboard_url" {
  description = "URL of the monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.coolbits_dashboard.id}"
}
