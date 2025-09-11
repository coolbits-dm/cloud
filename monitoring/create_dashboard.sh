#!/bin/bash
# Create CoolBits.ai monitoring dashboard

set -e

PROJECT_ID="coolbits-og-bridge"

echo "📊 Creating CoolBits.ai monitoring dashboard..."

# Create dashboard from JSON configuration
gcloud monitoring dashboards create \
  --config-from-file=monitoring/dashboard_coolbits.json \
  --project=$PROJECT_ID

echo "✅ Dashboard created successfully!"
echo "📊 View dashboard: https://console.cloud.google.com/monitoring/dashboards"
