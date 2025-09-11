#!/bin/bash
# Setup RAG infrastructure for all industries in CoolBits.ai

set -e

echo "🚀 Setting up RAG infrastructure for all industries..."

# Configuration
PROJECT_ID="coolbits-ai"
REGION="europe-west3"
BUCKET_PREFIX="coolbits-rag"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Function to create Cloud Storage bucket
create_bucket() {
    local industry_id=$1
    local bucket_name="${BUCKET_PREFIX}-${industry_id}-${PROJECT_ID}"
    
    print_status "Creating bucket for ${industry_id}: ${bucket_name}"
    
    if gsutil ls -b gs://${bucket_name} >/dev/null 2>&1; then
        print_warning "Bucket ${bucket_name} already exists"
        return 0
    fi
    
    if gsutil mb -p ${PROJECT_ID} -c STANDARD -l ${REGION} gs://${bucket_name}; then
        print_success "Created bucket: ${bucket_name}"
        return 0
    else
        print_error "Failed to create bucket: ${bucket_name}"
        return 1
    fi
}

# Function to upload sample documents
upload_documents() {
    local industry_id=$1
    local bucket_name="${BUCKET_PREFIX}-${industry_id}-${PROJECT_ID}"
    
    print_status "Uploading sample documents for ${industry_id}"
    
    # Create sample document content
    local sample_doc="sample_${industry_id}_document.txt"
    cat > ${sample_doc} << EOF
# ${industry_id^} Industry Documentation

## Industry Overview
This is a sample document for the ${industry_id} industry RAG system.

## Key Topics
- Industry-specific knowledge
- Best practices
- Market trends
- Regulatory information

## Sample Content
This document contains placeholder content for RAG integration.
Replace with actual industry-specific documentation.

Generated on: $(date)
EOF
    
    # Upload to bucket
    if gsutil cp ${sample_doc} gs://${bucket_name}/; then
        print_success "Uploaded sample document for ${industry_id}"
        rm ${sample_doc}
        return 0
    else
        print_error "Failed to upload document for ${industry_id}"
        rm ${sample_doc}
        return 1
    fi
}

# Function to create Vertex AI Search app
create_search_app() {
    local industry_id=$1
    
    print_status "Creating Vertex AI Search app for ${industry_id}"
    
    # This would create a Vertex AI Search app
    # Implementation depends on Vertex AI Search API
    print_warning "Vertex AI Search app creation not implemented yet"
    return 0
}

# Function to set up RAG for a single industry
setup_industry_rag() {
    local industry_id=$1
    
    print_status "Setting up RAG for industry: ${industry_id}"
    
    # Create bucket
    if ! create_bucket ${industry_id}; then
        return 1
    fi
    
    # Upload documents
    if ! upload_documents ${industry_id}; then
        return 1
    fi
    
    # Create search app
    if ! create_search_app ${industry_id}; then
        return 1
    fi
    
    print_success "RAG setup complete for ${industry_id}"
    return 0
}

# Main execution
main() {
    print_status "Starting RAG setup for all industries..."
    
    # List of all industries
    industries=(
        "agritech" "agri_inputs" "food_bev_mfg" "foodservice"
        "oil_gas" "power_gen" "renewables" "water_wastewater"
        "industrial_equipment" "electronics_mfg" "automation_robotics"
        "residential_construction" "commercial_construction" "proptech_realestate"
        "freight_logistics" "maritime_ports" "rail_logistics" "auto_oem" "ev_charging" "aftermarket_service"
        "commercial_aviation" "defense" "space_newspace"
        "hospitals_clinics" "med_devices" "digital_health" "pharma_branded" "generics" "biotech_cro_cdmo"
        "grocery_retail" "fashion_retail" "marketplaces_d2c" "personal_care_fmcg" "household_fmcg" "beverages_snacks"
        "hotels_resorts" "airlines_travel" "otas_traveltech"
        "saas_b2b" "devtools_cloud" "ai_ml_platforms" "data_infra"
        "mobile_operators" "fixed_isp" "network_equipment"
        "banking" "payments_fintech" "wealth_asset" "capital_markets" "pnc_insurance" "life_health_insurance" "insurtech"
        "streaming_ott" "publishing" "music_sports_media"
        "k12_edtech" "higher_ed"
        "gov_services" "intl_aid" "foundations" "faith_based"
        "law_firms" "regtech_ediscovery" "ip_patents" "consulting" "accounting_audit" "hr_staffing" "marketing_agencies"
        "mssp" "identity_access" "threat_intel" "physical_security"
        "waste_management" "recycling_circular" "carbon_esg"
        "mining_metals" "cement_glass" "specialty_chem"
        "clubs_leagues" "fitness_wellness" "gaming_esports" "beauty_cosmetics" "home_improvement" "smart_home"
        "exchanges" "defi" "wallets_infra"
    )
    
    local successful=0
    local total=${#industries[@]}
    
    print_status "Setting up RAG for ${total} industries..."
    
    for industry in "${industries[@]}"; do
        if setup_industry_rag ${industry}; then
            ((successful++))
        else
            print_error "Failed to set up RAG for ${industry}"
        fi
    done
    
    print_status "RAG setup complete!"
    print_success "Successfully configured: ${successful}/${total} industries"
    
    if [ ${successful} -eq ${total} ]; then
        print_success "All industries configured successfully! 🎉"
    else
        print_warning "Some industries failed to configure. Check logs above."
    fi
}

# Check if gcloud is installed and authenticated
check_prerequisites() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed"
        exit 1
    fi
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "No active gcloud authentication found"
        exit 1
    fi
    
    if ! command -v gsutil &> /dev/null; then
        print_error "gsutil is not installed"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Run the script
check_prerequisites
main
