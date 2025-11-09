#!/bin/bash

# Fix script pentru ogpt-bridge-service
set -e

echo "🔧 Fixing oGPT Bridge Service configuration..."

# Variabile
PROJECT_ID="coolbits-ai"
REGION="europe-west1"
SERVICE_NAME="ogpt-bridge-service"

# 1. Setup proiect
echo "📋 Setting up project..."
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# 2. Enable necessary APIs
echo "🔧 Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  vpcaccess.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com

# 3. Create/Update VPC Connector with proper configuration
echo "🌐 Creating/Updating VPC Connector..."
gcloud compute networks vpc-access connectors create svpc-${REGION} \
  --region=$REGION \
  --network=default \
  --range=10.8.0.0/28 \
  --min-instances=0 \
  --max-instances=10 \
  --machine-type=e2-micro || echo "VPC Connector already exists"

# 4. Update the service with proper VPC configuration
echo "🚀 Updating service configuration..."
gcloud run services update $SERVICE_NAME \
  --region=$REGION \
  --vpc-connector=svpc-${REGION} \
  --vpc-egress=all-traffic \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=10 \
  --timeout=300 \
  --concurrency=80

# 5. Grant necessary IAM permissions
echo "🔐 Setting up IAM permissions..."
SERVICE_ACCOUNT=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(spec.template.spec.serviceAccountName)')

if [ -z "$SERVICE_ACCOUNT" ]; then
  SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"
fi

echo "Using service account: $SERVICE_ACCOUNT"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

# Grant Cloud Run invoker role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/run.invoker"

# 6. Test the service
echo "🧪 Testing service..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo "Service URL: $SERVICE_URL"

# Test health endpoint
echo "🏥 Testing health endpoint..."
curl -sSf "$SERVICE_URL/api/v1/health" || echo "Health check failed"

# Test debug endpoint
echo "🔍 Testing debug endpoint..."
curl -sSf "$SERVICE_URL/api/debug" || echo "Debug check failed"

# Test chat endpoint with error handling
echo "💬 Testing chat endpoint..."
curl -sS -X POST "$SERVICE_URL/api/ai/chat?role=ogpt01" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello CEO"}' || echo "Chat test failed"

echo "✅ Service configuration updated!"
echo "Service URL: $SERVICE_URL"
echo "Health: $SERVICE_URL/api/v1/health"
echo "Debug: $SERVICE_URL/api/debug"
echo "Chat: $SERVICE_URL/api/ai/chat?role=ogpt01"
