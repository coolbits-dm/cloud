# CoolBits.ai Monitoring Setup Scripts
# ====================================

#!/bin/bash
# Setup Cloud Monitoring for CoolBits.ai

set -e

PROJECT_ID="coolbits-og-bridge"
REGION="europe-west1"

echo "📊 Setting up CoolBits.ai Monitoring"
echo "===================================="

# 1. Create uptime checks
echo "🔍 Creating uptime checks..."

# Frontend uptime check
gcloud monitoring uptime-checks create http coolbits-frontend-uptime \
  --period=60s \
  --timeout=5s \
  --selected-regions=$REGION \
  --resource-type=uptime-url \
  --path="/api/health" \
  --host="https://coolbits-frontend-*.run.app"

# Bridge uptime check
gcloud monitoring uptime-checks create http coolbits-bridge-uptime \
  --period=60s \
  --timeout=5s \
  --selected-regions=$REGION \
  --resource-type=uptime-url \
  --path="/health" \
  --host="https://coolbits-bridge-*.run.app"

# Dashboard uptime check
gcloud monitoring uptime-checks create http coolbits-dashboard-uptime \
  --period=60s \
  --timeout=5s \
  --selected-regions=$REGION \
  --resource-type=uptime-url \
  --path="/api/health" \
  --host="https://coolbits-dashboard-*.run.app"

# 2. Create notification channels
echo "📧 Creating notification channels..."

# Email channel
EMAIL_CHANNEL=$(gcloud alpha monitoring channels create \
  --display-name="CoolBits Alerts" \
  --type=email \
  --channel-labels=email_address=andrei@coolbits.ai \
  --format="value(name)")

# Slack channel (if configured)
# SLACK_CHANNEL=$(gcloud alpha monitoring channels create \
#   --display-name="CoolBits Slack" \
#   --type=slack \
#   --channel-labels=channel_name=#coolbits-alerts \
#   --format="value(name)")

# 3. Create alerting policies
echo "🚨 Creating alerting policies..."

# P95 Latency > 400ms
gcloud alpha monitoring policies create \
  --display-name="CoolBits P95 Latency > 400ms" \
  --condition-display-name="Frontend P95 Latency" \
  --condition-filter='metric.type="run.googleapis.com/request_latencies" AND resource.label."service_name"="coolbits-frontend"' \
  --condition-comparison=COMPARISON_GT \
  --condition-threshold-value=0.4 \
  --condition-duration=300s \
  --notification-channels=$EMAIL_CHANNEL

# 5xx Rate > 1%
gcloud alpha monitoring policies create \
  --display-name="CoolBits 5xx Rate > 1%" \
  --condition-display-name="Frontend 5xx Rate" \
  --condition-filter='metric.type="run.googleapis.com/request_count" AND metric.label."response_code_class"="5xx" AND resource.label."service_name"="coolbits-frontend"' \
  --condition-comparison=COMPARISON_GT \
  --condition-threshold-value=0.01 \
  --condition-duration=300s \
  --notification-channels=$EMAIL_CHANNEL

# CPU Usage > 80%
gcloud alpha monitoring policies create \
  --display-name="CoolBits CPU Usage > 80%" \
  --condition-display-name="High CPU Usage" \
  --condition-filter='metric.type="run.googleapis.com/container/cpu/utilizations" AND resource.label."service_name"="coolbits-frontend"' \
  --condition-comparison=COMPARISON_GT \
  --condition-threshold-value=0.8 \
  --condition-duration=300s \
  --notification-channels=$EMAIL_CHANNEL

# Memory Usage > 80%
gcloud alpha monitoring policies create \
  --display-name="CoolBits Memory Usage > 80%" \
  --condition-display-name="High Memory Usage" \
  --condition-filter='metric.type="run.googleapis.com/container/memory/utilizations" AND resource.label."service_name"="coolbits-frontend"' \
  --condition-comparison=COMPARISON_GT \
  --condition-threshold-value=0.8 \
  --condition-duration=300s \
  --notification-channels=$EMAIL_CHANNEL

# Uptime check failure
gcloud alpha monitoring policies create \
  --display-name="CoolBits Uptime Check Failure" \
  --condition-display-name="Uptime Check Down" \
  --condition-filter='metric.type="monitoring.googleapis.com/uptime_check/check_passed" AND resource.label."check_id"=~"coolbits-.*"' \
  --condition-comparison=COMPARISON_FALSE \
  --condition-duration=60s \
  --notification-channels=$EMAIL_CHANNEL

# 4. Create SLO policies
echo "🎯 Creating SLO policies..."

# Availability SLO (99.9%)
gcloud alpha monitoring slo create \
  --display-name="CoolBits Availability SLO" \
  --goal=0.999 \
  --rolling-period=30d \
  --service-filter='service="coolbits-frontend"' \
  --slo-filter='metric.type="monitoring.googleapis.com/uptime_check/check_passed"'

# Latency SLO (P95 < 400ms)
gcloud alpha monitoring slo create \
  --display-name="CoolBits Latency SLO" \
  --goal=0.95 \
  --rolling-period=30d \
  --service-filter='service="coolbits-frontend"' \
  --slo-filter='metric.type="run.googleapis.com/request_latencies" AND metric.label."response_code_class"="2xx"'

echo "✅ Monitoring setup complete!"
echo "📊 View monitoring: https://console.cloud.google.com/monitoring"
echo "🚨 View alerts: https://console.cloud.google.com/monitoring/alerting"
echo "🎯 View SLOs: https://console.cloud.google.com/monitoring/slo"
