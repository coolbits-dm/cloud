#!/bin/bash
# Automated RAG Corpus Creation Script for CoolBits.ai
# Creates all 88 RAG corpora using gcloud CLI

set -e

echo "🚀 Starting automated RAG corpus creation for CoolBits.ai..."

# Configuration
PROJECT_ID="coolbits-ai"
REGION="europe-west1"  # Using europe-west1 as recommended by Gemini
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

# Function to create a single RAG corpus
create_rag_corpus() {
    local rag_id=$1
    local rag_name=$2
    local rag_description=$3
    local corpus_name="${rag_id}-corpus"
    local bucket_name="${BUCKET_PREFIX}-${rag_id}-${PROJECT_ID}"
    
    print_processing "Creating corpus for ${rag_name} (${rag_id})"
    
    # Check if corpus already exists
    if gcloud alpha ai rag-corpora list --project=${PROJECT_ID} --region=${REGION} --filter="displayName:${corpus_name}" --format="value(name)" | grep -q "${corpus_name}"; then
        print_warning "Corpus ${corpus_name} already exists, skipping..."
        return 0
    fi
    
    # Create the corpus
    print_status "Creating corpus: ${corpus_name}"
    
    local corpus_id=$(gcloud alpha ai rag-corpora create \
        --project=${PROJECT_ID} \
        --region=${REGION} \
        --display-name="${corpus_name}" \
        --description="${rag_description}" \
        --embedding-model-publisher="google" \
        --embedding-model-name="text-embedding-004" \
        --embedding-model-version="1" \
        --format="value(name)" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$corpus_id" ]; then
        print_success "Created corpus: ${corpus_name} (ID: ${corpus_id})"
        
        # Create data source pointing to Cloud Storage bucket
        print_status "Creating data source for bucket: ${bucket_name}"
        
        gcloud alpha ai rag-corpora data-sources create \
            --project=${PROJECT_ID} \
            --region=${REGION} \
            --rag-corpus=${corpus_id} \
            --display-name="${rag_id}-data-source" \
            --gcs-source="gs://${bucket_name}/" \
            --file-type="PDF,TXT,DOC,DOCX" \
            --chunk-size=1024 \
            --chunk-overlap=200 \
            --format="value(name)" >/dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            print_success "Created data source for ${bucket_name}"
        else
            print_warning "Data source creation failed for ${bucket_name} (bucket may not exist yet)"
        fi
        
        return 0
    else
        print_error "Failed to create corpus: ${corpus_name}"
        return 1
    fi
}

# Function to create Search App for a corpus
create_search_app() {
    local rag_id=$1
    local rag_name=$2
    local search_app_name="${rag_id}-search-app"
    
    print_processing "Creating search app for ${rag_name} (${rag_id})"
    
    # Check if search app already exists
    if gcloud alpha ai rag-corpora search-apps list --project=${PROJECT_ID} --region=${REGION} --filter="displayName:${search_app_name}" --format="value(name)" | grep -q "${search_app_name}"; then
        print_warning "Search app ${search_app_name} already exists, skipping..."
        return 0
    fi
    
    # Get corpus ID
    local corpus_name="${rag_id}-corpus"
    local corpus_id=$(gcloud alpha ai rag-corpora list --project=${PROJECT_ID} --region=${REGION} --filter="displayName:${corpus_name}" --format="value(name)" | head -1)
    
    if [ -z "$corpus_id" ]; then
        print_error "Corpus ${corpus_name} not found, cannot create search app"
        return 1
    fi
    
    # Create search app
    local search_app_id=$(gcloud alpha ai rag-corpora search-apps create \
        --project=${PROJECT_ID} \
        --region=${REGION} \
        --rag-corpus=${corpus_id} \
        --display-name="${search_app_name}" \
        --description="Search app for ${rag_name}" \
        --format="value(name)" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$search_app_id" ]; then
        print_success "Created search app: ${search_app_name} (ID: ${search_app_id})"
        return 0
    else
        print_error "Failed to create search app: ${search_app_name}"
        return 1
    fi
}

# Main execution function
main() {
    print_status "Starting RAG corpus creation for CoolBits.ai..."
    print_status "Project: ${PROJECT_ID}"
    print_status "Region: ${REGION}"
    print_status "Total RAGs to create: 88"
    
    local successful_corpora=0
    local successful_search_apps=0
    local total_rags=0
    
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
        total_rags=$((total_rags + 1))
        
        if create_rag_corpus "$rag_id" "$rag_name" "$rag_description"; then
            successful_corpora=$((successful_corpora + 1))
        fi
        
        if create_search_app "$rag_id" "$rag_name"; then
            successful_search_apps=$((successful_search_apps + 1))
        fi
        
        echo ""
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
        total_rags=$((total_rags + 1))
        
        if create_rag_corpus "$rag_id" "$rag_name" "$rag_description"; then
            successful_corpora=$((successful_corpora + 1))
        fi
        
        if create_search_app "$rag_id" "$rag_name"; then
            successful_search_apps=$((successful_search_apps + 1))
        fi
        
        echo ""
    done
    
    # Phase 3: All remaining Industry RAGs (75 RAGs)
    print_status "Phase 3: Creating all remaining industry RAGs..."
    
    local industry_rags=(
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
    )
    
    for rag_info in "${industry_rags[@]}"; do
        IFS=':' read -r rag_id rag_name rag_description <<< "$rag_info"
        total_rags=$((total_rags + 1))
        
        if create_rag_corpus "$rag_id" "$rag_name" "$rag_description"; then
            successful_corpora=$((successful_corpora + 1))
        fi
        
        if create_search_app "$rag_id" "$rag_name"; then
            successful_search_apps=$((successful_search_apps + 1))
        fi
        
        echo ""
    done
    
    # Phase 4: Panel RAGs (6 RAGs)
    print_status "Phase 4: Creating panel RAGs..."
    
    local panel_rags=(
        "andrei-panel:Andrei Panel:RAG for Andrei Panel"
        "user-panel:User Panel:RAG for User Panel"
        "business-panel:Business Panel:RAG for Business Panel"
        "agency-panel:Agency Panel:RAG for Agency Panel"
        "dev-panel:Dev Panel:RAG for Dev Panel"
        "admin-panel:Admin Panel:RAG for Admin Panel"
    )
    
    for rag_info in "${panel_rags[@]}"; do
        IFS=':' read -r rag_id rag_name rag_description <<< "$rag_info"
        total_rags=$((total_rags + 1))
        
        if create_rag_corpus "$rag_id" "$rag_name" "$rag_description"; then
            successful_corpora=$((successful_corpora + 1))
        fi
        
        if create_search_app "$rag_id" "$rag_name"; then
            successful_search_apps=$((successful_search_apps + 1))
        fi
        
        echo ""
    done
    
    # Final summary
    echo ""
    print_status "=== FINAL SUMMARY ==="
    print_success "Total RAGs processed: ${total_rags}"
    print_success "Successful corpora created: ${successful_corpora}"
    print_success "Successful search apps created: ${successful_search_apps}"
    
    if [ $successful_corpora -eq $total_rags ]; then
        print_success "🎉 All RAG corpora created successfully!"
    else
        print_warning "⚠️  Some corpora creation failed. Check logs above."
    fi
    
    if [ $successful_search_apps -eq $total_rags ]; then
        print_success "🎉 All search apps created successfully!"
    else
        print_warning "⚠️  Some search apps creation failed. Check logs above."
    fi
    
    print_status "Next steps:"
    print_status "1. Upload industry-specific documents to Cloud Storage buckets"
    print_status "2. Test RAG queries through API endpoints"
    print_status "3. Integrate with Business Panel"
}

# Run the main function
main "$@"
