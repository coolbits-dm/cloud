#!/bin/bash
# Automated RAG Corpus Creation Script for CoolBits.ai using REST API
# For use in Google Cloud Shell

set -e

echo "🚀 Starting automated RAG corpus creation using REST API..."

# Configuration
PROJECT_ID="coolbits-ai"
LOCATION="global"  # Discovery Engine uses 'global' location
REGION="europe-west1"  # For Cloud Storage buckets
BUCKET_PREFIX="coolbits-rag"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to create data store using REST API
create_data_store() {
    local rag_id=$1
    local rag_name=$2
    local rag_description=$3
    local data_store_name="${rag_id}-corpus"
    local data_store_id="${rag_id}_corpus"  # Replace hyphens with underscores
    
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
    
    # Step 1: Create data store
    local data_store_path=$(create_data_store "$rag_id" "$rag_name" "$rag_description")
    if [ $? -ne 0 ] || [ -z "$data_store_path" ]; then
        print_error "Failed to create data store for ${rag_id}"
        return 1
    fi
    
    # Step 2: Create GCS connector
    if ! create_gcs_connector "$data_store_path" "$rag_id"; then
        print_error "Failed to create GCS connector for ${rag_id}"
        return 1
    fi
    
    # Step 3: Create search app
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
    
    local successful=0
    local total=0
    
    # Define all RAGs to create
    local all_rags=(
        # Phase 1: High Priority RAGs
        "ai_board:AI Board:AI Board management and coordination"
        "business:Business AI Council:Business AI Council for strategic decisions"
        "agritech:AgTech:Agricultural Technology and Innovation"
        "banking:Banking:Commercial and Retail Banking Services"
        "saas_b2b:SaaS B2B:Business-to-Business Software as a Service"
        
        # Phase 2: Medium Priority RAGs
        "healthcare:Healthcare:Healthcare Services and Medical Technology"
        "exchanges:Exchanges:Cryptocurrency Exchanges"
        "user:User:Personal AI Assistant for users"
        "agency:Agency:Agency Management AI"
        "dev:Dev:Developer Tools AI"
        
        # Phase 3: All remaining Industry RAGs
        "agri_inputs:Agri Inputs:Agricultural Inputs and Supplies"
        "aftermarket_service:Aftermarket Service:Aftermarket Services"
        "capital_markets:Capital Markets:Capital Markets and Investment Banking"
        "payments_fintech:Payments FinTech:Payments and Financial Technology"
        "wealth_asset:Wealth Asset:Wealth and Asset Management"
        "insurtech:InsurTech:Insurance Technology"
        "defi:DeFi:Decentralized Finance"
        "ai_ml_platforms:AI ML Platforms:AI and Machine Learning Platforms"
        "devtools_cloud:DevTools Cloud:Developer Tools and Cloud Services"
        "data_infra:Data Infrastructure:Data Infrastructure and Analytics"
        "identity_access:Identity Access:Identity and Access Management"
        "threat_intel:Threat Intelligence:Threat Intelligence and Security"
        "mssp:MSSP:Managed Security Service Providers"
        "physical_security:Physical Security:Physical Security Solutions"
        "digital_health:Digital Health:Digital Health Solutions"
        "hospitals_clinics:Hospitals Clinics:Hospitals and Clinics"
        "med_devices:Medical Devices:Medical Devices"
        "pharma_branded:Pharma Branded:Branded Pharmaceuticals"
        "generics:Generics:Generic Pharmaceuticals"
        "biotech_cro_cdmo:Biotech CRO CDMO:Biotechnology and Contract Research"
        "electronics_mfg:Electronics Manufacturing:Electronics Manufacturing"
        "automation_robotics:Automation Robotics:Automation and Robotics"
        "industrial_equipment:Industrial Equipment:Industrial Equipment"
        "auto_oem:Auto OEM:Automotive Original Equipment Manufacturers"
        "food_bev_mfg:Food Bev Manufacturing:Food and Beverage Manufacturing"
        "cement_glass:Cement Glass:Cement and Glass Manufacturing"
        "specialty_chem:Specialty Chemicals:Specialty Chemicals"
        "mining_metals:Mining Metals:Mining and Metals"
        "power_gen:Power Generation:Power Generation"
        "renewables:Renewables:Renewable Energy"
        "oil_gas:Oil Gas:Oil and Gas"
        "water_wastewater:Water Wastewater:Water and Wastewater Management"
        "waste_management:Waste Management:Waste Management"
        "recycling_circular:Recycling Circular:Recycling and Circular Economy"
        "carbon_esg:Carbon ESG:Carbon and ESG Solutions"
        "ev_charging:EV Charging:Electric Vehicle Charging"
        "freight_logistics:Freight Logistics:Freight and Logistics"
        "rail_logistics:Rail Logistics:Rail Logistics"
        "maritime_ports:Maritime Ports:Maritime and Ports"
        "commercial_aviation:Commercial Aviation:Commercial Aviation"
        "airlines_travel:Airlines Travel:Airlines and Travel"
        "otas_traveltech:OTAs TravelTech:Online Travel Agencies and Travel Technology"
        "proptech_realestate:PropTech Real Estate:Property Technology and Real Estate"
        "commercial_construction:Commercial Construction:Commercial Construction"
        "residential_construction:Residential Construction:Residential Construction"
        "home_improvement:Home Improvement:Home Improvement"
        "fashion_retail:Fashion Retail:Fashion and Retail"
        "grocery_retail:Grocery Retail:Grocery Retail"
        "marketplaces_d2c:Marketplaces D2C:Marketplaces and Direct-to-Consumer"
        "beauty_cosmetics:Beauty Cosmetics:Beauty and Cosmetics"
        "personal_care_fmcg:Personal Care FMCG:Personal Care and FMCG"
        "household_fmcg:Household FMCG:Household FMCG"
        "beverages_snacks:Beverages Snacks:Beverages and Snacks"
        "foodservice:Food Service:Food Service"
        "gaming_esports:Gaming Esports:Gaming and Esports"
        "streaming_ott:Streaming OTT:Streaming and Over-the-Top Media"
        "music_sports_media:Music Sports Media:Music, Sports, and Media"
        "publishing:Publishing:Publishing"
        "higher_ed:Higher Education:Higher Education"
        "k12_edtech:K12 EdTech:K-12 Education Technology"
        "consulting:Consulting:Consulting Services"
        "law_firms:Law Firms:Law Firms"
        "accounting_audit:Accounting Audit:Accounting and Audit"
        "marketing_agencies:Marketing Agencies:Marketing Agencies"
        "hr_staffing:HR Staffing:Human Resources and Staffing"
        "gov_services:Government Services:Government Services"
        "defense:Defense:Defense and Military"
        "intl_aid:International Aid:International Aid"
        "foundations:Foundations:Foundations"
        "faith_based:Faith Based:Faith-Based Organizations"
        "wallets_infra:Wallets Infrastructure:Cryptocurrency Wallets and Infrastructure"
        "smart_home:Smart Home:Smart Home Technology"
        "fitness_wellness:Fitness Wellness:Fitness and Wellness"
        "hotels_resorts:Hotels Resorts:Hotels and Resorts"
        "clubs_leagues:Clubs Leagues:Clubs and Leagues"
        "ip_patents:IP Patents:Intellectual Property and Patents"
        "regtech_ediscovery:RegTech E-Discovery:Regulatory Technology and E-Discovery"
        "space_newspace:Space NewSpace:Space and New Space Technology"
        "fixed_isp:Fixed ISP:Fixed Internet Service Providers"
        "mobile_operators:Mobile Operators:Mobile Network Operators"
        "network_equipment:Network Equipment:Network Equipment"
        
        # Phase 4: Panel RAGs
        "andrei-panel:Andrei Panel:RAG for Andrei Panel"
        "user-panel:User Panel:RAG for User Panel"
        "business-panel:Business Panel:RAG for Business Panel"
        "agency-panel:Agency Panel:RAG for Agency Panel"
        "dev-panel:Dev Panel:RAG for Dev Panel"
        "admin-panel:Admin Panel:RAG for Admin Panel"
    )
    
    # Process RAGs in phases
    local phases=(
        "Phase 1: High Priority RAGs:0:5"
        "Phase 2: Medium Priority RAGs:5:10"
        "Phase 3: All remaining Industry RAGs:10:85"
        "Phase 4: Panel RAGs:85:91"
    )
    
    for phase_info in "${phases[@]}"; do
        IFS=':' read -r phase_name start_idx end_idx <<< "$phase_info"
        print_status "\n${phase_name}..."
        
        for ((i=$start_idx; i<$end_idx; i++)); do
            local rag_info="${all_rags[$i]}"
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
