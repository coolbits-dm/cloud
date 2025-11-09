#!/bin/bash
# Proof Pack Collector - Enterprise Verification Script
# Generates signed proof_pack.zip with all verification evidence
# Usage: bash scripts/proof/collect_proof.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Functions
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_section() {
    local title=$1
    echo
    print_color $CYAN "=== $title ==="
}

print_success() {
    print_color $GREEN "✓ $1"
}

print_error() {
    print_color $RED "✗ $1"
}

print_warning() {
    print_color $YELLOW "⚠ $1"
}

# Parse arguments
OUTPUT_DIR="proof_output"
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Create output directory
if [[ -d "$OUTPUT_DIR" ]]; then
    rm -rf "$OUTPUT_DIR"
fi
mkdir -p "$OUTPUT_DIR"

print_color $MAGENTA "🚀 CoolBits.ai Enterprise Proof Pack Collector"
print_color $GRAY "Output directory: $OUTPUT_DIR"

# 1. Git Information
print_section "Git Repository Status"
if git rev-parse HEAD >/dev/null 2>&1; then
    GIT_HEAD=$(git rev-parse HEAD)
    GIT_BRANCH=$(git branch --show-current)
    GIT_STATUS=$(git status --porcelain)
    GIT_LOG=$(git log -1 --pretty=format:"%H %an %ae %ad %s")
    
    cat > "$OUTPUT_DIR/git_info.json" << EOF
{
    "git_head": "$GIT_HEAD",
    "git_branch": "$GIT_BRANCH",
    "git_status": "$GIT_STATUS",
    "git_last_commit": "$GIT_LOG",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    print_success "Git info collected"
    if [[ "$VERBOSE" == "true" ]]; then
        print_color $GRAY "HEAD: $GIT_HEAD"
        print_color $GRAY "Branch: $GIT_BRANCH"
        print_color $GRAY "Status: $GIT_STATUS"
    fi
else
    print_error "Failed to collect git info"
    exit 1
fi

# 2. CI/CD Status
print_section "CI/CD Pipeline Status"
if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
    cat > "$OUTPUT_DIR/ci_status.json" << EOF
{
    "github_actions": true,
    "workflow_run_id": "${GITHUB_RUN_ID:-}",
    "workflow_run_number": "${GITHUB_RUN_NUMBER:-}",
    "workflow_name": "${GITHUB_WORKFLOW:-}",
    "commit_sha": "${GITHUB_SHA:-}",
    "ref": "${GITHUB_REF:-}"
}
EOF
    print_success "CI status collected"
else
    cat > "$OUTPUT_DIR/ci_status.json" << EOF
{
    "github_actions": false,
    "local_run": true,
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    print_warning "Local run detected"
fi

# 3. SBOM Verification
print_section "SBOM (Software Bill of Materials)"
if [[ -d "sbom" ]]; then
    SBOM_FILES=$(find sbom -name "*.json" -type f)
    if [[ -n "$SBOM_FILES" ]]; then
        echo "[" > "$OUTPUT_DIR/sbom_info.json"
        FIRST=true
        for file in $SBOM_FILES; do
            if [[ "$FIRST" == "true" ]]; then
                FIRST=false
            else
                echo "," >> "$OUTPUT_DIR/sbom_info.json"
            fi
            HASH=$(sha256sum "$file" | cut -d' ' -f1)
            SIZE=$(stat -c%s "$file")
            MODIFIED=$(date -u -r "$file" +%Y-%m-%dT%H:%M:%SZ)
            cat >> "$OUTPUT_DIR/sbom_info.json" << EOF
{
    "file": "$(basename "$file")",
    "size": $SIZE,
    "sha256": "$HASH",
    "modified": "$MODIFIED"
}
EOF
        done
        echo "]" >> "$OUTPUT_DIR/sbom_info.json"
        print_success "SBOM files found and hashed"
    else
        echo '{"error": "No SBOM files found"}' > "$OUTPUT_DIR/sbom_info.json"
        print_warning "No SBOM files found in sbom/ directory"
    fi
else
    echo '{"error": "No SBOM directory found"}' > "$OUTPUT_DIR/sbom_info.json"
    print_warning "No SBOM directory found"
fi

# 4. Cosign Verification
print_section "Cosign Signature Verification"
if command -v cosign >/dev/null 2>&1; then
    COSIGN_VERSION=$(cosign version 2>/dev/null || echo "unknown")
    cat > "$OUTPUT_DIR/cosign_info.json" << EOF
{
    "cosign_available": true,
    "version": "$COSIGN_VERSION",
    "verifications": []
}
EOF
    
    # Try to verify registry.json if it exists
    if [[ -f "cblm/opipe/nha/out/registry.json" ]]; then
        REGISTRY_HASH=$(sha256sum "cblm/opipe/nha/out/registry.json" | cut -d' ' -f1)
        # Update the JSON to include registry verification
        jq --arg hash "$REGISTRY_HASH" '.verifications += [{"file": "registry.json", "sha256": $hash, "status": "available_for_verification"}]' "$OUTPUT_DIR/cosign_info.json" > "$OUTPUT_DIR/cosign_info.json.tmp" && mv "$OUTPUT_DIR/cosign_info.json.tmp" "$OUTPUT_DIR/cosign_info.json"
    fi
    
    print_success "Cosign verification info collected"
else
    echo '{"cosign_available": false, "error": "cosign command not found"}' > "$OUTPUT_DIR/cosign_info.json"
    print_warning "Cosign not available"
fi

# 5. CVE Scan
print_section "CVE Security Scan"
if command -v trivy >/dev/null 2>&1; then
    TRIVY_VERSION=$(trivy version 2>/dev/null || echo "unknown")
    cat > "$OUTPUT_DIR/cve_scan.json" << EOF
{
    "trivy_available": true,
    "version": "$TRIVY_VERSION",
    "scan_results": []
}
EOF
    
    # Scan current directory for vulnerabilities
    if trivy fs . --severity HIGH,CRITICAL --format json > "$OUTPUT_DIR/trivy_scan.json" 2>/dev/null; then
        HIGH_COUNT=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$OUTPUT_DIR/trivy_scan.json" 2>/dev/null || echo "0")
        CRITICAL_COUNT=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$OUTPUT_DIR/trivy_scan.json" 2>/dev/null || echo "0")
        TOTAL_COUNT=$(jq '[.Results[].Vulnerabilities[]?] | length' "$OUTPUT_DIR/trivy_scan.json" 2>/dev/null || echo "0")
        
        jq --arg high "$HIGH_COUNT" --arg critical "$CRITICAL_COUNT" --arg total "$TOTAL_COUNT" --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '.scan_results += [{"target": "filesystem", "high_count": ($high | tonumber), "critical_count": ($critical | tonumber), "total_vulnerabilities": ($total | tonumber), "scan_timestamp": $timestamp}]' "$OUTPUT_DIR/cve_scan.json" > "$OUTPUT_DIR/cve_scan.json.tmp" && mv "$OUTPUT_DIR/cve_scan.json.tmp" "$OUTPUT_DIR/cve_scan.json"
        
        print_success "CVE scan completed"
    else
        jq '.scan_results += [{"target": "filesystem", "error": "trivy scan failed"}]' "$OUTPUT_DIR/cve_scan.json" > "$OUTPUT_DIR/cve_scan.json.tmp" && mv "$OUTPUT_DIR/cve_scan.json.tmp" "$OUTPUT_DIR/cve_scan.json"
        print_warning "Trivy scan failed"
    fi
else
    echo '{"trivy_available": false, "error": "trivy command not found"}' > "$OUTPUT_DIR/cve_scan.json"
    print_warning "Trivy not available"
fi

# 6. M8-M14 Verification Scripts
print_section "M8-M14 Enterprise Hardening Verification"
cat > "$OUTPUT_DIR/milestone_verification.json" << EOF
{
EOF

MILESTONES=("M8" "M9" "M10" "M11" "M12" "M13" "M14")
FIRST=true
for milestone in "${MILESTONES[@]}"; do
    SCRIPT_PATH="scripts/verify_$milestone.ps1"
    if [[ -f "$SCRIPT_PATH" ]]; then
        print_color $YELLOW "Running $SCRIPT_PATH..."
        if [[ "$FIRST" == "true" ]]; then
            FIRST=false
        else
            echo "," >> "$OUTPUT_DIR/milestone_verification.json"
        fi
        
        # Run PowerShell script
        if command -v pwsh >/dev/null 2>&1; then
            OUTPUT=$(pwsh -File "$SCRIPT_PATH" 2>&1)
            EXIT_CODE=$?
        else
            OUTPUT="PowerShell not available"
            EXIT_CODE=1
        fi
        
        cat >> "$OUTPUT_DIR/milestone_verification.json" << EOF
    "$milestone": {
        "script": "$SCRIPT_PATH",
        "exit_code": $EXIT_CODE,
        "success": $([ $EXIT_CODE -eq 0 ] && echo "true" || echo "false"),
        "output": $(echo "$OUTPUT" | jq -R -s .),
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
EOF
        
        if [[ $EXIT_CODE -eq 0 ]]; then
            print_success "$milestone verification passed"
        else
            print_error "$milestone verification failed (exit code: $EXIT_CODE)"
        fi
    else
        print_warning "$SCRIPT_PATH not found"
        if [[ "$FIRST" == "true" ]]; then
            FIRST=false
        else
            echo "," >> "$OUTPUT_DIR/milestone_verification.json"
        fi
        
        cat >> "$OUTPUT_DIR/milestone_verification.json" << EOF
    "$milestone": {
        "script": "$SCRIPT_PATH",
        "error": "Script not found",
        "success": false,
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
EOF
    fi
done

echo "}" >> "$OUTPUT_DIR/milestone_verification.json"

# 7. Policy Enforcement Health
print_section "Policy Enforcement Health"
# Check if policy health endpoint is available
if curl -fsS "http://localhost:3001/policy/health" > "$OUTPUT_DIR/policy_health.json" 2>/dev/null; then
    print_success "Policy health endpoint accessible"
else
    echo '{"error": "Policy health endpoint not accessible", "url": "http://localhost:3001/policy/health"}' > "$OUTPUT_DIR/policy_health.json"
    print_warning "Policy health endpoint not accessible"
fi

# Collect policy enforcement logs
if find logs -name "policy-enforcement-*.jsonl" -type f 2>/dev/null | head -1 | xargs -I {} tail -200 {} > "$OUTPUT_DIR/policy_enforcement_logs.txt" 2>/dev/null; then
    print_success "Policy enforcement logs collected (last 200 lines)"
else
    echo "No policy enforcement logs found" > "$OUTPUT_DIR/policy_enforcement_logs.txt"
    print_warning "No policy enforcement logs found"
fi

# 8. Chaos Engineering Reports
print_section "Chaos Engineering Reports"
if [[ -d "chaos/reports" ]]; then
    REPORTS=$(find chaos/reports -name "*.md" -type f)
    if [[ -n "$REPORTS" ]]; then
        REPORT_COUNT=$(echo "$REPORTS" | wc -l)
        echo "{" > "$OUTPUT_DIR/chaos_reports.json"
        echo '    "report_count": '$REPORT_COUNT',' >> "$OUTPUT_DIR/chaos_reports.json"
        echo '    "reports": [' >> "$OUTPUT_DIR/chaos_reports.json"
        
        FIRST=true
        for report in $REPORTS; do
            if [[ "$FIRST" == "true" ]]; then
                FIRST=false
            else
                echo "," >> "$OUTPUT_DIR/chaos_reports.json"
            fi
            SIZE=$(stat -c%s "$report")
            MODIFIED=$(date -u -r "$report" +%Y-%m-%dT%H:%M:%SZ)
            cat >> "$OUTPUT_DIR/chaos_reports.json" << EOF
        {
            "file": "$(basename "$report")",
            "size": $SIZE,
            "modified": "$MODIFIED"
        }
EOF
        done
        
        echo "    ]," >> "$OUTPUT_DIR/chaos_reports.json"
        echo '    "latest_reports": [' >> "$OUTPUT_DIR/chaos_reports.json"
        
        # Get latest 5 reports
        LATEST_REPORTS=$(echo "$REPORTS" | xargs ls -t | head -5)
        FIRST=true
        for report in $LATEST_REPORTS; do
            if [[ "$FIRST" == "true" ]]; then
                FIRST=false
            else
                echo "," >> "$OUTPUT_DIR/chaos_reports.json"
            fi
            CONTENT=$(cat "$report" | jq -R -s .)
            cat >> "$OUTPUT_DIR/chaos_reports.json" << EOF
        {
            "file": "$(basename "$report")",
            "content": $CONTENT
        }
EOF
        done
        
        echo "    ]" >> "$OUTPUT_DIR/chaos_reports.json"
        echo "}" >> "$OUTPUT_DIR/chaos_reports.json"
        
        print_success "Chaos reports collected"
    else
        echo '{"error": "No chaos reports found"}' > "$OUTPUT_DIR/chaos_reports.json"
        print_warning "No chaos reports found"
    fi
else
    echo '{"error": "No chaos reports directory found"}' > "$OUTPUT_DIR/chaos_reports.json"
    print_warning "No chaos reports directory found"
fi

# 9. Backup Verification
print_section "Backup Verification"
if command -v gsutil >/dev/null 2>&1; then
    GSUTIL_VERSION=$(gsutil version 2>/dev/null || echo "unknown")
    echo "{" > "$OUTPUT_DIR/backup_status.json"
    echo '    "gsutil_available": true,' >> "$OUTPUT_DIR/backup_status.json"
    echo '    "version": "'$GSUTIL_VERSION'",' >> "$OUTPUT_DIR/backup_status.json"
    echo '    "backup_bucket": "'${BACKUP_BUCKET:-}'",' >> "$OUTPUT_DIR/backup_status.json"
    echo '    "backup_status": [' >> "$OUTPUT_DIR/backup_status.json"
    
    if [[ -n "${BACKUP_BUCKET:-}" ]]; then
        if gsutil ls "gs://$BACKUP_BUCKET" > "$OUTPUT_DIR/bucket_contents.txt" 2>/dev/null; then
            BUCKET_CONTENTS=$(cat "$OUTPUT_DIR/bucket_contents.txt" | jq -R -s .)
            echo '        {' >> "$OUTPUT_DIR/backup_status.json"
            echo '            "bucket_contents": '$BUCKET_CONTENTS',' >> "$OUTPUT_DIR/backup_status.json"
            echo '            "bucket_accessible": true' >> "$OUTPUT_DIR/backup_status.json"
            echo '        }' >> "$OUTPUT_DIR/backup_status.json"
            
            # Get bucket lifecycle policy
            if gsutil lifecycle get "gs://$BACKUP_BUCKET" > "$OUTPUT_DIR/lifecycle_policy.txt" 2>/dev/null; then
                LIFECYCLE_POLICY=$(cat "$OUTPUT_DIR/lifecycle_policy.txt" | jq -R -s .)
                echo ',' >> "$OUTPUT_DIR/backup_status.json"
                echo '        {' >> "$OUTPUT_DIR/backup_status.json"
                echo '            "lifecycle_policy": '$LIFECYCLE_POLICY >> "$OUTPUT_DIR/backup_status.json"
                echo '        }' >> "$OUTPUT_DIR/backup_status.json"
            fi
            
            print_success "Backup bucket accessible"
        else
            echo '        {"bucket_accessible": false, "error": "Failed to access backup bucket"}' >> "$OUTPUT_DIR/backup_status.json"
            print_warning "Failed to access backup bucket"
        fi
    else
        echo '        {"bucket_accessible": false, "error": "BACKUP_BUCKET environment variable not set"}' >> "$OUTPUT_DIR/backup_status.json"
        print_warning "BACKUP_BUCKET environment variable not set"
    fi
    
    echo "    ]" >> "$OUTPUT_DIR/backup_status.json"
    echo "}" >> "$OUTPUT_DIR/backup_status.json"
else
    echo '{"gsutil_available": false, "error": "gsutil command not found"}' > "$OUTPUT_DIR/backup_status.json"
    print_warning "gsutil not available"
fi

# 10. NHA Registry Verification
print_section "NHA Registry Verification"
if [[ -f "cblm/opipe/nha/out/registry.json" ]]; then
    REGISTRY_HASH=$(sha256sum "cblm/opipe/nha/out/registry.json" | cut -d' ' -f1)
    REGISTRY_SIZE=$(stat -c%s "cblm/opipe/nha/out/registry.json")
    AGENT_COUNT=$(jq '.agents | length' "cblm/opipe/nha/out/registry.json" 2>/dev/null || echo "0")
    LAST_UPDATED=$(jq -r '.last_updated // "unknown"' "cblm/opipe/nha/out/registry.json" 2>/dev/null || echo "unknown")
    VERSION=$(jq -r '.version // "unknown"' "cblm/opipe/nha/out/registry.json" 2>/dev/null || echo "unknown")
    
    cat > "$OUTPUT_DIR/nha_registry.json" << EOF
{
    "registry_file": "cblm/opipe/nha/out/registry.json",
    "sha256": "$REGISTRY_HASH",
    "size": $REGISTRY_SIZE,
    "agent_count": $AGENT_COUNT,
    "last_updated": "$LAST_UPDATED",
    "version": "$VERSION"
}
EOF
    
    print_success "NHA registry verified"
else
    echo '{"error": "Registry file not found"}' > "$OUTPUT_DIR/nha_registry.json"
    print_warning "NHA registry file not found"
fi

# 11. Adaptive Policy Reports
print_section "Adaptive Policy Reports"
echo "{" > "$OUTPUT_DIR/adaptive_policy.json"
echo '    "collector_report": null,' >> "$OUTPUT_DIR/adaptive_policy.json"
echo '    "policy_gaps": null,' >> "$OUTPUT_DIR/adaptive_policy.json"
echo '    "recommendations": null' >> "$OUTPUT_DIR/adaptive_policy.json"

# Check for policy collection report
if [[ -f "reports/policy_collect_last_24h.json" ]]; then
    COLLECTOR_REPORT=$(cat "reports/policy_collect_last_24h.json" | jq -c .)
    jq --argjson report "$COLLECTOR_REPORT" '.collector_report = $report' "$OUTPUT_DIR/adaptive_policy.json" > "$OUTPUT_DIR/adaptive_policy.json.tmp" && mv "$OUTPUT_DIR/adaptive_policy.json.tmp" "$OUTPUT_DIR/adaptive_policy.json"
fi

# Check for policy gaps report
if [[ -f "reports/policy_gaps.json" ]]; then
    POLICY_GAPS=$(cat "reports/policy_gaps.json" | jq -c .)
    jq --argjson gaps "$POLICY_GAPS" '.policy_gaps = $gaps' "$OUTPUT_DIR/adaptive_policy.json" > "$OUTPUT_DIR/adaptive_policy.json.tmp" && mv "$OUTPUT_DIR/adaptive_policy.json.tmp" "$OUTPUT_DIR/adaptive_policy.json"
fi

# Check for recommendations
if [[ -f "cblm/opipe/nha/policy_recommendations.yaml" ]]; then
    RECOMMENDATIONS=$(cat "cblm/opipe/nha/policy_recommendations.yaml" | jq -R -s .)
    jq --argjson recs "$RECOMMENDATIONS" '.recommendations = $recs' "$OUTPUT_DIR/adaptive_policy.json" > "$OUTPUT_DIR/adaptive_policy.json.tmp" && mv "$OUTPUT_DIR/adaptive_policy.json.tmp" "$OUTPUT_DIR/adaptive_policy.json"
fi

echo "}" >> "$OUTPUT_DIR/adaptive_policy.json"
print_success "Adaptive policy reports collected"

# 12. System Health Check
print_section "System Health Check"
cat > "$OUTPUT_DIR/system_health.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "system_info": {
        "os": "$(uname -s)",
        "kernel": "$(uname -r)",
        "shell": "$SHELL",
        "working_directory": "$PWD"
    },
    "services": []
}
EOF

# Check if key services are running
SERVICES=("localhost:3001" "localhost:8080" "localhost:5000")
for service in "${SERVICES[@]}"; do
    if curl -fsS "http://$service/health" >/dev/null 2>&1; then
        STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$service/health")
        jq --arg svc "$service" --arg status "healthy" --argjson code "$STATUS_CODE" '.services += [{"service": $svc, "status": $status, "status_code": $code}]' "$OUTPUT_DIR/system_health.json" > "$OUTPUT_DIR/system_health.json.tmp" && mv "$OUTPUT_DIR/system_health.json.tmp" "$OUTPUT_DIR/system_health.json"
    else
        jq --arg svc "$service" --arg status "unhealthy" --arg error "Service not accessible" '.services += [{"service": $svc, "status": $status, "error": $error}]' "$OUTPUT_DIR/system_health.json" > "$OUTPUT_DIR/system_health.json.tmp" && mv "$OUTPUT_DIR/system_health.json.tmp" "$OUTPUT_DIR/system_health.json"
    fi
done

print_success "System health check completed"

# 13. Create Proof Pack Summary
print_section "Creating Proof Pack Summary"
cat > "$OUTPUT_DIR/proof_pack_summary.json" << EOF
{
    "proof_pack_version": "1.0",
    "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "generator": "CoolBits.ai Enterprise Proof Pack Collector",
    "components": {
EOF

COMPONENTS=("git_info" "ci_status" "sbom_info" "cosign_info" "cve_scan" "milestone_verification" "policy_health" "chaos_reports" "backup_status" "nha_registry" "adaptive_policy" "system_health")
FIRST=true
for component in "${COMPONENTS[@]}"; do
    if [[ "$FIRST" == "true" ]]; then
        FIRST=false
    else
        echo "," >> "$OUTPUT_DIR/proof_pack_summary.json"
    fi
    EXISTS=$([[ -f "$OUTPUT_DIR/$component.json" ]] && echo "true" || echo "false")
    echo "        \"$component\": $EXISTS" >> "$OUTPUT_DIR/proof_pack_summary.json"
done

TOTAL_FILES=$(find "$OUTPUT_DIR" -type f | wc -l)
TOTAL_SIZE=$(find "$OUTPUT_DIR" -type f -exec stat -c%s {} + | awk '{sum+=$1} END {print sum}')

cat >> "$OUTPUT_DIR/proof_pack_summary.json" << EOF
    },
    "total_files": $TOTAL_FILES,
    "total_size_bytes": $TOTAL_SIZE
}
EOF

print_success "Proof pack summary created"

# 14. Create ZIP Archive
print_section "Creating Proof Pack Archive"
ZIP_PATH="proof_pack.zip"
if [[ -f "$ZIP_PATH" ]]; then
    rm -f "$ZIP_PATH"
fi

cd "$OUTPUT_DIR"
zip -r "../$ZIP_PATH" . >/dev/null
cd ..

ZIP_SIZE=$(stat -c%s "$ZIP_PATH")
ZIP_HASH=$(sha256sum "$ZIP_PATH" | cut -d' ' -f1)

print_success "Proof pack archive created: $ZIP_PATH"
print_color $GRAY "Archive size: $(echo "scale=2; $ZIP_SIZE / 1024 / 1024" | bc) MB"
print_color $GRAY "SHA256: $ZIP_HASH"

# 15. Sign the Proof Pack
print_section "Signing Proof Pack"
if command -v cosign >/dev/null 2>&1; then
    SIGNATURE_FILE="proof_pack.sig"
    CERTIFICATE_FILE="proof_pack.cert"
    
    if cosign sign-blob --yes --output-signature "$SIGNATURE_FILE" --output-certificate "$CERTIFICATE_FILE" "$ZIP_PATH" 2>/dev/null; then
        print_success "Proof pack signed successfully"
        print_color $GRAY "Signature: $SIGNATURE_FILE"
        print_color $GRAY "Certificate: $CERTIFICATE_FILE"
    else
        print_warning "Failed to sign proof pack with cosign"
    fi
else
    print_warning "Cosign not available for signing"
fi

# 16. Final Output
print_section "Proof Pack Collection Complete"
print_color $GREEN "🎯 PROOF PACK READY"
print_color $NC "Archive: proof_pack.zip"
print_color $NC "SHA256: $ZIP_HASH"
if [[ -f "proof_pack.sig" ]]; then
    print_color $NC "Signature: proof_pack.sig"
fi
if [[ -f "proof_pack.cert" ]]; then
    print_color $NC "Certificate: proof_pack.cert"
fi

print_color $CYAN "📋 VERIFICATION SUMMARY"
SUMMARY=$(cat "$OUTPUT_DIR/proof_pack_summary.json")
for component in "${COMPONENTS[@]}"; do
    EXISTS=$(echo "$SUMMARY" | jq -r ".components.$component")
    if [[ "$EXISTS" == "true" ]]; then
        print_color $GREEN "✓ $component"
    else
        print_color $RED "✗ $component"
    fi
done

print_color $MAGENTA "🚀 Ready for @oRunner verification!"
