#!/bin/bash

# Deploy script pentru ogpt-bridge-service
set -e

echo "🚀 Deploying oGPT Bridge Service..."

# Variabile
PROJECT_ID="coolbits-ai"
REGION="europe-west1"
SERVICE_NAME="ogpt-bridge-service"
AR_REPO="ogpt-repo"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}:prod"

# 1. Setup proiect
echo "📋 Setting up project..."
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# 2. Enable APIs
echo "🔧 Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  vpcaccess.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com

# 3. Create Artifact Registry
echo "📦 Creating Artifact Registry..."
gcloud artifacts repositories create $AR_REPO \
  --repository-format=docker \
  --location=$REGION \
  --description="Containers oGPT" || echo "Repository already exists"

# 4. Configure Docker
echo "🐳 Configuring Docker..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# 5. Build and push image
echo "🔨 Building and pushing image..."
docker build -t "$IMAGE_URI" .
docker push "$IMAGE_URI"

# 6. Create VPC Connector (if not exists)
echo "🌐 Creating VPC Connector..."
gcloud compute networks vpc-access connectors create svpc-${REGION} \
  --region=$REGION \
  --network=default \
  --range=10.8.0.0/28 || echo "VPC Connector already exists"

# 7. Deploy service
echo "🚀 Deploying service..."
gcloud run deploy $SERVICE_NAME \
  --image="$IMAGE_URI" \
  --region=$REGION \
  --allow-unauthenticated \
  --vpc-connector=svpc-${REGION} \
  --vpc-egress=all-traffic \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=10

# 8. Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "✅ Service deployed at: $SERVICE_URL"

# 9. Test health endpoint
echo "🏥 Testing health endpoint..."
curl -sSf "$SERVICE_URL/api/v1/health" || echo "Health check failed"

# 10. Test chat endpoint
echo "💬 Testing chat endpoint..."
curl -sS -X POST "$SERVICE_URL/api/ai/chat?role=ogpt01" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello CEO"}' || echo "Chat test failed"

echo "🎉 Deployment complete!"
echo "Service URL: $SERVICE_URL"
echo "Health: $SERVICE_URL/api/v1/health"
echo "Chat: $SERVICE_URL/api/ai/chat?role=ogpt01"
