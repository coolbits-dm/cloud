#!/bin/bash

# Test script pentru ogpt-bridge-service
set -e

echo "🧪 Testing oGPT Bridge Service..."

# Variabile
PROJECT_ID="coolbits-ai"
REGION="europe-west1"
SERVICE_NAME="ogpt-bridge-service"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "Service URL: $SERVICE_URL"

# Test 1: Health endpoint
echo "🏥 Test 1: Health endpoint"
curl -sSf "$SERVICE_URL/api/v1/health" | jq '.' || echo "Health check failed"

# Test 2: Debug endpoint
echo "🔍 Test 2: Debug endpoint"
curl -sSf "$SERVICE_URL/api/debug" | jq '.' || echo "Debug check failed"

# Test 3: Chat endpoint with valid role
echo "💬 Test 3: Chat endpoint with valid role"
curl -sS -X POST "$SERVICE_URL/api/ai/chat?role=ogpt01" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello CEO"}' | jq '.' || echo "Chat test failed"

# Test 4: Chat endpoint with invalid role
echo "❌ Test 4: Chat endpoint with invalid role"
curl -sS -X POST "$SERVICE_URL/api/ai/chat?role=invalid" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}' | jq '.' || echo "Invalid role test failed"

# Test 5: Chat endpoint without role
echo "❌ Test 5: Chat endpoint without role"
curl -sS -X POST "$SERVICE_URL/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}' | jq '.' || echo "No role test failed"

echo "✅ All tests completed!"
