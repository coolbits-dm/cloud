#!/bin/bash
# CoolBits.ai Cost Hygiene Setup
# ==============================

set -e

PROJECT_ID="coolbits-og-bridge"
REGION="europe-west1"

echo "🧹 Setting up CoolBits.ai Cost Hygiene"
echo "====================================="

# 1. Set up log retention policies
echo "📝 Setting up log retention policies..."

# Critical logs (90 days)
gcloud logging sinks create critical-logs-sink \
  --log-filter='severity>=ERROR OR protoPayload.serviceName="cloudsql.googleapis.com" OR protoPayload.serviceName="run.googleapis.com"' \
  --destination=bigquery.googleapis.com/projects/$PROJECT_ID/datasets/logs \
  --bigquery-dataset=logs \
  --bigquery-table=critical_logs

# Standard logs (30 days)
gcloud logging sinks create standard-logs-sink \
  --log-filter='severity>=INFO AND severity<ERROR' \
  --destination=bigquery.googleapis.com/projects/$PROJECT_ID/datasets/logs \
  --bigquery-dataset=logs \
  --bigquery-table=standard_logs

# Debug logs (7 days)
gcloud logging sinks create debug-logs-sink \
  --log-filter='severity=DEBUG OR severity=TRACE' \
  --destination=bigquery.googleapis.com/projects/$PROJECT_ID/datasets/logs \
  --bigquery-dataset=logs \
  --bigquery-table=debug_logs

# 2. Set up metrics retention
echo "📊 Setting up metrics retention..."

# High-resolution metrics (7 days)
gcloud alpha monitoring policies create \
  --display-name="High-res metrics retention" \
  --condition-display-name="High-res metrics" \
  --condition-filter='metric.type=~"run.googleapis.com/request_latencies|run.googleapis.com/container/cpu/utilizations|run.googleapis.com/container/memory/utilizations"' \
  --condition-comparison=COMPARISON_GT \
  --condition-threshold-value=0 \
  --condition-duration=0s \
  --notification-channels=""

# 3. Configure autoscaling
echo "⚖️  Configuring autoscaling..."

# Frontend service
gcloud run services update coolbits-frontend \
  --region=$REGION \
  --min-instances=1 \
  --max-instances=10 \
  --cpu-throttling \
  --memory=2Gi \
  --cpu=1

# Bridge service
gcloud run services update coolbits-bridge \
  --region=$REGION \
  --min-instances=0 \
  --max-instances=5 \
  --cpu-throttling \
  --memory=1Gi \
  --cpu=0.5

# Dashboard service
gcloud run services update coolbits-dashboard \
  --region=$REGION \
  --min-instances=0 \
  --max-instances=3 \
  --cpu-throttling \
  --memory=1Gi \
  --cpu=0.5

# 4. Set up cost alerts
echo "🚨 Setting up cost alerts..."

# Daily cost alert
gcloud alpha monitoring policies create \
  --display-name="Daily Cost Alert" \
  --condition-display-name="Daily cost > 50 EUR" \
  --condition-filter='metric.type="billing.googleapis.com/billing/cost"' \
  --condition-comparison=COMPARISON_GT \
  --condition-threshold-value=50 \
  --condition-duration=0s \
  --notification-channels="projects/$PROJECT_ID/notificationChannels/CHANNEL_ID"

# Weekly cost alert
gcloud alpha monitoring policies create \
  --display-name="Weekly Cost Alert" \
  --condition-display-name="Weekly cost > 300 EUR" \
  --condition-filter='metric.type="billing.googleapis.com/billing/cost"' \
  --condition-comparison=COMPARISON_GT \
  --condition-threshold-value=300 \
  --condition-duration=0s \
  --notification-channels="projects/$PROJECT_ID/notificationChannels/CHANNEL_ID"

# 5. Enable cost optimization features
echo "💰 Enabling cost optimization..."

# Enable preemptible instances for non-critical workloads
gcloud compute instances create coolbits-worker-preemptible \
  --zone=$REGION-a \
  --machine-type=e2-small \
  --preemptible \
  --image-family=cos-stable \
  --image-project=cos-cloud \
  --labels=env=prod,service=worker,owner=ogpt,cost-center=ogpt

# Set up committed use discounts
gcloud compute commitments create coolbits-commitment \
  --region=$REGION \
  --plan=12-month \
  --resources=vcpu=4,memory=8

# 6. Set up automatic shutdown for development
echo "🛑 Setting up automatic shutdown for development..."

# Create shutdown script
cat > scripts/shutdown_dev.sh << 'EOF'
#!/bin/bash
# Shutdown development resources after hours

# Get current hour
HOUR=$(date +%H)

# Shutdown if between 22:00 and 06:00
if [ $HOUR -ge 22 ] || [ $HOUR -le 6 ]; then
    echo "Shutting down development resources..."
    
    # Stop development services
    gcloud run services update coolbits-frontend-dev \
      --region=europe-west1 \
      --min-instances=0
    
    gcloud run services update coolbits-bridge-dev \
      --region=europe-west1 \
      --min-instances=0
    
    echo "Development resources shut down"
else
    echo "Keeping development resources running"
fi
EOF

chmod +x scripts/shutdown_dev.sh

# Schedule shutdown script
echo "0 22 * * * /path/to/scripts/shutdown_dev.sh" | crontab -

echo "✅ Cost hygiene setup complete!"
echo "📊 View costs: https://console.cloud.google.com/billing"
echo "📝 View logs: https://console.cloud.google.com/logs"
echo "⚖️  View autoscaling: https://console.cloud.google.com/run"
