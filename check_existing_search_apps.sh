#!/bin/bash

# Script to check existing Search Apps and Data Stores in Discovery Engine
# Run this in Cloud Shell

PROJECT_ID="coolbits-ai"
LOCATION="global"

echo "🔍 Checking existing Discovery Engine infrastructure..."
echo "Project: $PROJECT_ID"
echo "Location: $LOCATION"
echo ""

# Get access token
ACCESS_TOKEN=$(gcloud auth print-access-token)

echo "📋 Checking Data Stores..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://discoveryengine.googleapis.com/v1beta/projects/${PROJECT_ID}/locations/${LOCATION}/dataStores" \
  | jq '.dataStores[]? | {name: .name, displayName: .displayName, industryVertical: .industryVertical, solutionTypes: .solutionTypes}' 2>/dev/null || echo "No data stores found or jq not available"

echo ""
echo "🔍 Checking Search Apps..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://discoveryengine.googleapis.com/v1beta/projects/${PROJECT_ID}/locations/${LOCATION}/searchApps" \
  | jq '.searchApps[]? | {name: .name, displayName: .displayName, dataStoreIds: .dataStoreIds}' 2>/dev/null || echo "No search apps found or jq not available"

echo ""
echo "🎯 Checking Engines..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://discoveryengine.googleapis.com/v1beta/projects/${PROJECT_ID}/locations/${LOCATION}/engines" \
  | jq '.engines[]? | {name: .name, displayName: .displayName, solutionType: .solutionType}' 2>/dev/null || echo "No engines found or jq not available"

echo ""
echo "✅ Discovery Engine infrastructure check complete!"
