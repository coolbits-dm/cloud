#!/bin/bash
# RAG Testing Script for CoolBits.ai
# Tests all created RAG corpora with sample queries

set -e

echo "🧪 Starting RAG testing for CoolBits.ai..."

# Configuration
PROJECT_ID="coolbits-ai"
REGION="europe-west1"

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

print_testing() {
    echo -e "${CYAN}[TESTING]${NC} $1"
}

# Function to test a single RAG corpus
test_rag_corpus() {
    local rag_id=$1
    local rag_name=$2
    local test_query=$3
    local search_app_name="${rag_id}-search-app"
    
    print_testing "Testing ${rag_name} (${rag_id})"
    
    # Get search app ID
    local search_app_id=$(gcloud alpha ai rag-corpora search-apps list \
        --project=${PROJECT_ID} \
        --region=${REGION} \
        --filter="displayName:${search_app_name}" \
        --format="value(name)" 2>/dev/null | head -1)
    
    if [ -z "$search_app_id" ]; then
        print_error "Search app ${search_app_name} not found"
        return 1
    fi
    
    # Test query
    print_status "Testing query: '${test_query}'"
    
    local response=$(gcloud alpha ai rag-corpora search-apps query \
        --project=${PROJECT_ID} \
        --region=${REGION} \
        --search-app=${search_app_id} \
        --query="${test_query}" \
        --page-size=3 \
        --format="json" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        local result_count=$(echo "$response" | jq '.results | length' 2>/dev/null || echo "0")
        if [ "$result_count" -gt 0 ]; then
            print_success "✅ ${rag_name} returned ${result_count} results"
            return 0
        else
            print_warning "⚠️  ${rag_name} returned no results (may need documents uploaded)"
            return 1
        fi
    else
        print_error "❌ ${rag_name} query failed"
        return 1
    fi
}

# Main testing function
main() {
    print_status "Starting RAG testing for CoolBits.ai..."
    print_status "Project: ${PROJECT_ID}"
    print_status "Region: ${REGION}"
    
    local successful_tests=0
    local total_tests=0
    
    # Test Phase 1: High Priority RAGs
    print_status "Phase 1: Testing high priority RAGs..."
    
    local phase1_tests=(
        "ai_board:AI Board:What are the best practices for AI Board management?"
        "business:Business AI Council:How should business AI councils make strategic decisions?"
        "agritech:AgTech:What are the latest trends in agricultural technology?"
        "banking:Banking:What are the key regulations in commercial banking?"
        "saas_b2b:SaaS B2B:What are the best practices for B2B SaaS companies?"
    )
    
    for test_info in "${phase1_tests[@]}"; do
        IFS=':' read -r rag_id rag_name test_query <<< "$test_info"
        total_tests=$((total_tests + 1))
        
        if test_rag_corpus "$rag_id" "$rag_name" "$test_query"; then
            successful_tests=$((successful_tests + 1))
        fi
        
        echo ""
    done
    
    # Test Phase 2: Medium Priority RAGs
    print_status "Phase 2: Testing medium priority RAGs..."
    
    local phase2_tests=(
        "healthcare:Healthcare:What are the latest developments in healthcare technology?"
        "exchanges:Exchanges:What are the security requirements for cryptocurrency exchanges?"
        "user:User:How can personal AI assistants help users?"
        "agency:Agency:What are the best practices for agency management?"
        "dev:Dev:What are the latest developer tools and frameworks?"
    )
    
    for test_info in "${phase2_tests[@]}"; do
        IFS=':' read -r rag_id rag_name test_query <<< "$test_info"
        total_tests=$((total_tests + 1))
        
        if test_rag_corpus "$rag_id" "$rag_name" "$test_query"; then
            successful_tests=$((successful_tests + 1))
        fi
        
        echo ""
    done
    
    # Test a few key industry RAGs
    print_status "Phase 3: Testing key industry RAGs..."
    
    local industry_tests=(
        "saas_b2b:SaaS B2B:What are the key metrics for SaaS companies?"
        "banking:Banking:What are the compliance requirements for banks?"
        "healthcare:Healthcare:What are the HIPAA requirements for healthcare?"
        "exchanges:Exchanges:What are the AML requirements for crypto exchanges?"
        "agritech:AgTech:What are the precision agriculture technologies?"
    )
    
    for test_info in "${industry_tests[@]}"; do
        IFS=':' read -r rag_id rag_name test_query <<< "$test_info"
        total_tests=$((total_tests + 1))
        
        if test_rag_corpus "$rag_id" "$rag_name" "$test_query"; then
            successful_tests=$((successful_tests + 1))
        fi
        
        echo ""
    done
    
    # Test Panel RAGs
    print_status "Phase 4: Testing panel RAGs..."
    
    local panel_tests=(
        "andrei-panel:Andrei Panel:What are the features of the Andrei panel?"
        "business-panel:Business Panel:What are the business panel capabilities?"
        "user-panel:User Panel:What can users do in the user panel?"
    )
    
    for test_info in "${panel_tests[@]}"; do
        IFS=':' read -r rag_id rag_name test_query <<< "$test_info"
        total_tests=$((total_tests + 1))
        
        if test_rag_corpus "$rag_id" "$rag_name" "$test_query"; then
            successful_tests=$((successful_tests + 1))
        fi
        
        echo ""
    done
    
    # Final summary
    echo ""
    print_status "=== TESTING SUMMARY ==="
    print_success "Total RAGs tested: ${total_tests}"
    print_success "Successful tests: ${successful_tests}"
    print_success "Failed tests: $((total_tests - successful_tests))"
    
    if [ $successful_tests -eq $total_tests ]; then
        print_success "🎉 All RAG tests passed!"
    else
        print_warning "⚠️  Some RAG tests failed. This may be due to:"
        print_warning "   - Missing documents in Cloud Storage buckets"
        print_warning "   - Corpus not fully indexed yet"
        print_warning "   - Search app configuration issues"
    fi
    
    print_status "Next steps:"
    print_status "1. Upload industry-specific documents to Cloud Storage buckets"
    print_status "2. Wait for corpus indexing to complete"
    print_status "3. Re-run tests after document upload"
    print_status "4. Configure API endpoints for production use"
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    print_error "jq is required but not installed. Please install jq first."
    print_status "On Ubuntu/Debian: sudo apt-get install jq"
    print_status "On macOS: brew install jq"
    exit 1
fi

# Run the main function
main "$@"
