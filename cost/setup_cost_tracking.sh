# CoolBits.ai Cost Setup Scripts
# ==============================

#!/bin/bash
# Setup cost tracking and budgeting for CoolBits.ai

set -e

PROJECT_ID="coolbits-og-bridge"
BILLING_ACCOUNT=""
REGION="europe-west1"

echo "💰 Setting up CoolBits.ai Cost Tracking"
echo "======================================="

# 1. Enable Billing Export to BigQuery
echo "📊 Setting up billing export to BigQuery..."
gcloud billing export create \
  --billing-account=$BILLING_ACCOUNT \
  --dataset-id=billing_export \
  --location=EU

# 2. Create cost views
echo "📋 Creating cost views in BigQuery..."
bq query --use_legacy_sql=false < bq/sql/cost_views.sql

# 3. Create budget and alerts
echo "🚨 Setting up budget and alerts..."
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT \
  --display-name="coolbits-monthly" \
  --budget-amount=1000EUR \
  --threshold-rule=percent=0.8 \
  --threshold-rule=percent=1.0 \
  --all-updates-rule-pubsub-topic="projects/$PROJECT_ID/topics/billing-alerts"

# 4. Create Pub/Sub topic for billing alerts
echo "📢 Creating Pub/Sub topic for billing alerts..."
gcloud pubsub topics create billing-alerts

# 5. Create notification channel
echo "📧 Creating notification channel..."
gcloud alpha monitoring channels create \
  --display-name="CoolBits Billing Alerts" \
  --type=email \
  --channel-labels=email_address=andrei@coolbits.ai

# 6. Apply labels to existing services
echo "🏷️  Applying cost labels to services..."

# Frontend service
gcloud run services update coolbits-frontend \
  --region=$REGION \
  --labels=env=prod,service=frontend,owner=ogpt,cost-center=ogpt,version=1.0.0

# Bridge service
gcloud run services update coolbits-bridge \
  --region=$REGION \
  --labels=env=prod,service=bridge,owner=ogpt,cost-center=ogpt,version=1.0.0

# Dashboard service
gcloud run services update coolbits-dashboard \
  --region=$REGION \
  --labels=env=prod,service=dashboard,owner=ogpt,cost-center=ogpt,version=1.0.0

echo "✅ Cost tracking setup complete!"
echo "📊 View costs: https://console.cloud.google.com/billing"
echo "📋 BigQuery views: https://console.cloud.google.com/bigquery"
echo "🚨 Alerts: https://console.cloud.google.com/monitoring/alerting"
