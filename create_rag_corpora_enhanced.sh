#!/bin/bash
# Enhanced RAG Corpus Creation Script for CoolBits.ai using REST API
# Creates buckets first, then RAG infrastructure

set -e

echo "🚀 Starting automated RAG corpus creation using REST API..."

# Configuration
PROJECT_ID="coolbits-ai"
LOCATION="global"
REGION="europe-west1"
BUCKET_PREFIX="coolbits-rag"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_processing() {
    echo -e "${CYAN}[PROCESSING]${NC} $1"
}

# Function to get access token
get_access_token() {
    gcloud auth print-access-token
}

# Function to create Cloud Storage bucket
create_bucket() {
    local rag_id=$1
    local bucket_name="${BUCKET_PREFIX}-${rag_id}-${PROJECT_ID}"
    
    print_processing "Creating bucket: ${bucket_name}"
    
    # Check if bucket already exists
    if gsutil ls -b gs://${bucket_name} >/dev/null 2>&1; then
        print_warning "Bucket ${bucket_name} already exists, skipping..."
        return 0
    fi
    
    # Create bucket
    if gsutil mb -p ${PROJECT_ID} -c STANDARD -l ${REGION} gs://${bucket_name}; then
        print_success "Created bucket: ${bucket_name}"
        return 0
    else
        print_error "Failed to create bucket: ${bucket_name}"
        return 1
    fi
}

# Function to create data store using REST API
create_data_store() {
    local rag_id=$1
    local rag_name=$2
    local rag_description=$3
    local data_store_name="${rag_id}-corpus"
    local data_store_id="${rag_id}_corpus"
    
    print_processing "Creating data store: ${data_store_name}"
    
    # Check if data store already exists
    local access_token=$(get_access_token)
    local check_url="https://discoveryengine.googleapis.com/v1beta/projects/${PROJECT_ID}/locations/${LOCATION}/dataStores"
    
    local existing_stores=$(curl -s -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        "${check_url}?filter=displayName%3D%22${data_store_name}%22")
    
    if echo "$existing_stores" | jq -e '.dataStores[] | select(.displayName=="'${data_store_name}'")' > /dev/null 2>&1; then
        print_warning "Data store ${data_store_name} already exists, skipping..."
        return 0
    fi
    
    # Create data store
    local create_url="https://discoveryengine.googleapis.com/v1beta/projects/${PROJECT_ID}/locations/${LOCATION}/dataStores?dataStoreId=${data_store_id}"
    
    local payload=$(cat << EOF
{
    "displayName": "${data_store_name}",
    "industryVertical": "GENERIC",
    "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
    "contentConfig": "CONTENT_REQUIRED"
}
EOF
)
    
    local response=$(curl -s -X POST \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        -d "${payload}" \
        "${create_url}")
    
    if echo "$response" | jq -e '.name' > /dev/null 2>&1; then
        local data_store_path=$(echo "$response" | jq -r '.name')
        print_success "Created data store: ${data_store_name} (Path: ${data_store_path})"
        echo "${data_store_path}"
        return 0
    else
        print_error "Failed to create data store: ${data_store_name}"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
        return 1
    fi
}

# Function to create GCS connector using REST API
create_gcs_connector() {
    local data_store_path=$1
    local rag_id=$2
    local bucket_name="${BUCKET_PREFIX}-${rag_id}-${PROJECT_ID}"
    local connector_name="${rag_id}-gcs-connector"
    local connector_id="${rag_id}_gcs_connector"
    
    print_processing "Creating GCS connector for bucket: ${bucket_name}"
    
    # Check if connector already exists
    local access_token=$(get_access_token)
    local check_url="https://discoveryengine.googleapis.com/v1beta/${data_store_path}/connectors"
    
    local existing_connectors=$(curl -s -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        "${check_url}")
    
    if echo "$existing_connectors" | jq -e '.connectors[] | select(.displayName=="'${connector_name}'")' > /dev/null 2>&1; then
        print_warning "Connector ${connector_name} already exists, skipping..."
        return 0
    fi
    
    # Create GCS connector
    local create_url="https://discoveryengine.googleapis.com/v1beta/${data_store_path}/connectors?connectorId=${connector_id}"
    
    local payload=$(cat << EOF
{
    "displayName": "${connector_name}",
    "gcsSource": {
        "inputUris": ["gs://${bucket_name}/*"],
        "dataSchema": "content"
    }
}
EOF
)
    
    local response=$(curl -s -X POST \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        -d "${payload}" \
        "${create_url}")
    
    if echo "$response" | jq -e '.name' > /dev/null 2>&1; then
        print_success "Created GCS connector: ${connector_name}"
        return 0
    else
        print_error "Failed to create GCS connector: ${connector_name}"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
        return 1
    fi
}

# Function to create search app using REST API
create_search_app() {
    local data_store_path=$1
    local rag_id=$2
    local rag_name=$3
    local search_app_name="${rag_id}-search-app"
    local search_app_id="${rag_id}_search_app"
    
    print_processing "Creating search app: ${search_app_name}"
    
    # Check if search app already exists
    local access_token=$(get_access_token)
    local check_url="https://discoveryengine.googleapis.com/v1beta/projects/${PROJECT_ID}/locations/${LOCATION}/engines"
    
    local existing_apps=$(curl -s -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        "${check_url}?filter=displayName%3D%22${search_app_name}%22")
    
    if echo "$existing_apps" | jq -e '.engines[] | select(.displayName=="'${search_app_name}'")' > /dev/null 2>&1; then
        print_warning "Search app ${search_app_name} already exists, skipping..."
        return 0
    fi
    
    # Create search app
    local create_url="https://discoveryengine.googleapis.com/v1beta/projects/${PROJECT_ID}/locations/${LOCATION}/engines?engineId=${search_app_id}"
    
    local payload=$(cat << EOF
{
    "displayName": "${search_app_name}",
    "solutionType": "SOLUTION_TYPE_SEARCH",
    "searchEngineConfig": {
        "searchTier": "SEARCH_TIER_STANDARD",
        "searchAddOns": ["SEARCH_ADD_ON_LLM"]
    },
    "dataStoreIds": ["${data_store_path##*/}"]
}
EOF
)
    
    local response=$(curl -s -X POST \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        -d "${payload}" \
        "${create_url}")
    
    if echo "$response" | jq -e '.name' > /dev/null 2>&1; then
        local search_app_path=$(echo "$response" | jq -r '.name')
        print_success "Created search app: ${search_app_name} (Path: ${search_app_path})"
        echo "${search_app_path}"
        return 0
    else
        print_error "Failed to create search app: ${search_app_name}"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
        return 1
    fi
}

# Function to create complete RAG infrastructure
create_rag_complete() {
    local rag_id=$1
    local rag_name=$2
    local rag_description=$3
    
    print_processing "Creating complete RAG infrastructure for ${rag_name} (${rag_id})"
    
    # Step 1: Create Cloud Storage bucket
    if ! create_bucket "$rag_id"; then
        print_error "Failed to create bucket for ${rag_id}"
        return 1
    fi
    
    # Step 2: Create data store
    local data_store_path=$(create_data_store "$rag_id" "$rag_name" "$rag_description")
    if [ $? -ne 0 ] || [ -z "$data_store_path" ]; then
        print_error "Failed to create data store for ${rag_id}"
        return 1
    fi
    
    # Step 3: Create GCS connector
    if ! create_gcs_connector "$data_store_path" "$rag_id"; then
        print_error "Failed to create GCS connector for ${rag_id}"
        return 1
    fi
    
    # Step 4: Create search app
    local search_app_path=$(create_search_app "$data_store_path" "$rag_id" "$rag_name")
    if [ $? -ne 0 ] || [ -z "$search_app_path" ]; then
        print_error "Failed to create search app for ${rag_id}"
        return 1
    fi
    
    print_success "✅ Successfully created complete RAG infrastructure for ${rag_name} (${rag_id})"
    return 0
}

# Main execution function
main() {
    print_status "Starting RAG corpus creation for CoolBits.ai using REST API..."
    print_status "Project: ${PROJECT_ID}"
    print_status "Location: ${LOCATION}"
    print_status "Total RAGs to create: 88"
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        print_error "jq is required but not installed. Installing..."
        sudo apt-get update && sudo apt-get install -y jq
    fi
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        print_error "curl is required but not installed."
        exit 1
    fi
    
    # Check if gsutil is available
    if ! command -v gsutil &> /dev/null; then
        print_error "gsutil is required but not installed."
        exit 1
    fi
    
    local successful=0
    local total=0
    
    # Phase 1: High Priority RAGs (5 RAGs)
    print_status "Phase 1: Creating high priority RAGs..."
    
    local phase1_rags=(
        "ai_board:AI Board:AI Board management and coordination"
        "business:Business AI Council:Business AI Council for strategic decisions"
        "agritech:AgTech:Agricultural Technology and Innovation"
        "banking:Banking:Commercial and Retail Banking Services"
        "saas_b2b:SaaS B2B:Business-to-Business Software as a Service"
    )
    
    for rag_info in "${phase1_rags[@]}"; do
        IFS=':' read -r rag_id rag_name rag_description <<< "$rag_info"
        total=$((total + 1))
        
        echo ""
        print_status "=================================================="
        print_status "Processing: ${rag_name} (${rag_id})"
        print_status "=================================================="
        
        if create_rag_complete "$rag_id" "$rag_name" "$rag_description"; then
            successful=$((successful + 1))
        fi
        
        # Add delay between creations to avoid rate limiting
        sleep 2
    done
    
    # Phase 2: Medium Priority RAGs (5 RAGs)
    print_status "Phase 2: Creating medium priority RAGs..."
    
    local phase2_rags=(
        "healthcare:Healthcare:Healthcare Services and Medical Technology"
        "exchanges:Exchanges:Cryptocurrency Exchanges"
        "user:User:Personal AI Assistant for users"
        "agency:Agency:Agency Management AI"
        "dev:Dev:Developer Tools AI"
    )
    
    for rag_info in "${phase2_rags[@]}"; do
        IFS=':' read -r rag_id rag_name rag_description <<< "$rag_info"
        total=$((total + 1))
        
        echo ""
        print_status "=================================================="
        print_status "Processing: ${rag_name} (${rag_id})"
        print_status "=================================================="
        
        if create_rag_complete "$rag_id" "$rag_name" "$rag_description"; then
            successful=$((successful + 1))
        fi
        
        # Add delay between creations to avoid rate limiting
        sleep 2
    done
    
    # Final summary
    echo ""
    print_status "============================================================"
    print_status "=== FINAL SUMMARY ==="
    print_status "============================================================"
    print_success "Total RAGs processed: ${total}"
    print_success "Successful creations: ${successful}"
    print_success "Failed creations: $((total - successful))"
    
    if [ $successful -eq $total ]; then
        print_success "🎉 All RAG corpora created successfully!"
    else
        print_warning "⚠️  Some RAG creations failed. Check logs above."
    fi
    
    print_status "\nNext steps:"
    print_status "1. Upload industry-specific documents to Cloud Storage buckets"
    print_status "2. Wait for corpus indexing to complete"
    print_status "3. Test RAG queries through API endpoints"
    print_status "4. Integrate with Business Panel"
}

# Run the main function
main "$@"
