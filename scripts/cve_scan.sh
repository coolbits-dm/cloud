#!/bin/bash
# CoolBits.ai CVE Scan Script
# M9.4 - SBOM + CVE Scan Obligatory

set -euo pipefail

# Configuration
IMAGE="$1"
SEVERITY_THRESHOLD="HIGH,CRITICAL"
EXIT_CODE=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Trivy is installed
check_trivy() {
    if ! command -v trivy &> /dev/null; then
        log_error "Trivy is not installed. Installing..."
        
        # Install Trivy
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install trivy
        else
            log_error "Unsupported OS. Please install Trivy manually."
            exit 1
        fi
        
        log_success "Trivy installed successfully"
    else
        log_info "Trivy is already installed"
    fi
}

# Run CVE scan
run_cve_scan() {
    log_info "Starting CVE scan for image: $IMAGE"
    
    # Create output directory
    mkdir -p security/scans
    
    # Run Trivy scan
    trivy image \
        --severity "$SEVERITY_THRESHOLD" \
        --format json \
        --output "security/scans/cve_scan_$(date +%Y%m%d_%H%M%S).json" \
        --exit-code 1 \
        "$IMAGE"
    
    local scan_exit_code=$?
    
    if [ $scan_exit_code -eq 0 ]; then
        log_success "CVE scan passed - no HIGH/CRITICAL vulnerabilities found"
        EXIT_CODE=0
    else
        log_error "CVE scan failed - HIGH/CRITICAL vulnerabilities found"
        EXIT_CODE=1
        
        # Create failure marker
        touch cve_fail.flag
        echo "$(date): CVE scan failed for image $IMAGE" >> cve_fail.flag
    fi
    
    return $scan_exit_code
}

# Generate SBOM
generate_sbom() {
    log_info "Generating SBOM for image: $IMAGE"
    
    # Generate SBOM with Trivy
    trivy image \
        --format spdx-json \
        --output "security/scans/sbom_$(date +%Y%m%d_%H%M%S).json" \
        "$IMAGE"
    
    log_success "SBOM generated successfully"
}

# Generate report
generate_report() {
    log_info "Generating security report"
    
    local report_file="security/scans/security_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# CoolBits.ai Security Scan Report

**Generated:** $(date)
**Image:** $IMAGE
**Scanner:** Trivy
**Severity Threshold:** $SEVERITY_THRESHOLD

## Scan Results

EOF
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ **PASSED** - No HIGH/CRITICAL vulnerabilities found" >> "$report_file"
    else
        echo "❌ **FAILED** - HIGH/CRITICAL vulnerabilities found" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "## Files Generated" >> "$report_file"
    echo "- CVE Scan: \`security/scans/cve_scan_*.json\`" >> "$report_file"
    echo "- SBOM: \`security/scans/sbom_*.json\`" >> "$report_file"
    echo "- Report: \`$report_file\`" >> "$report_file"
    
    log_success "Security report generated: $report_file"
}

# Main function
main() {
    log_info "Starting CoolBits.ai CVE scan process"
    
    if [ -z "$IMAGE" ]; then
        log_error "Usage: $0 <image_name>"
        exit 1
    fi
    
    check_trivy
    run_cve_scan
    generate_sbom
    generate_report
    
    if [ $EXIT_CODE -eq 0 ]; then
        log_success "CVE scan process completed successfully"
    else
        log_error "CVE scan process failed"
    fi
    
    exit $EXIT_CODE
}

# Run main function
main "$@"
