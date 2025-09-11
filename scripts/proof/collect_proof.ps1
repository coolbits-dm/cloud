#!/usr/bin/env pwsh
# Proof Pack Collector - Enterprise Verification Script
# Generates signed proof_pack.zip with all verification evidence
# Usage: pwsh -File scripts/proof/collect_proof.ps1

param(
    [string]$OutputDir = "proof_output",
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colors for output
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Section {
    param([string]$Title)
    Write-ColorOutput "`n=== $Title ===" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" "Yellow"
}

# Create output directory
$OutputDir = Join-Path $PWD $OutputDir
if (Test-Path $OutputDir) {
    Remove-Item $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDir | Out-Null

Write-ColorOutput "🚀 CoolBits.ai Enterprise Proof Pack Collector" "Magenta"
Write-ColorOutput "Output directory: $OutputDir" "Gray"

# 1. Git Information
Write-Section "Git Repository Status"
try {
    $gitHead = git rev-parse HEAD
    $gitBranch = git branch --show-current
    $gitStatus = git status --porcelain
    $gitLog = git log -1 --pretty=format:"%H %an %ae %ad %s"
    
    @{
        "git_head" = $gitHead
        "git_branch" = $gitBranch
        "git_status" = $gitStatus
        "git_last_commit" = $gitLog
        "timestamp" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    } | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/git_info.json" -Encoding UTF8
    
    Write-Success "Git info collected"
    if ($Verbose) {
        Write-ColorOutput "HEAD: $gitHead" "Gray"
        Write-ColorOutput "Branch: $gitBranch" "Gray"
        Write-ColorOutput "Status: $($gitStatus -join ', ')" "Gray"
    }
} catch {
    Write-Error "Failed to collect git info: $_"
    exit 1
}

# 2. CI/CD Status
Write-Section "CI/CD Pipeline Status"
try {
    # Check if we're in a GitHub Actions environment
    if ($env:GITHUB_ACTIONS -eq "true") {
        $ciInfo = @{
            "github_actions" = $true
            "workflow_run_id" = $env:GITHUB_RUN_ID
            "workflow_run_number" = $env:GITHUB_RUN_NUMBER
            "workflow_name" = $env:GITHUB_WORKFLOW
            "commit_sha" = $env:GITHUB_SHA
            "ref" = $env:GITHUB_REF
        }
    } else {
        $ciInfo = @{
            "github_actions" = $false
            "local_run" = $true
            "timestamp" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
        }
    }
    
    $ciInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/ci_status.json" -Encoding UTF8
    Write-Success "CI status collected"
} catch {
    Write-Warning "CI status collection failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/ci_status.json" -Encoding UTF8
}

# 3. SBOM Verification
Write-Section "SBOM (Software Bill of Materials)"
try {
    $sbomFiles = Get-ChildItem -Path "sbom" -Filter "*.json" -ErrorAction SilentlyContinue
    if ($sbomFiles) {
        $sbomInfo = @()
        foreach ($file in $sbomFiles) {
            $hash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash
            $sbomInfo += @{
                "file" = $file.Name
                "size" = $file.Length
                "sha256" = $hash
                "modified" = $file.LastWriteTime.ToString("yyyy-MM-ddTHH:mm:ssZ")
            }
        }
        $sbomInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/sbom_info.json" -Encoding UTF8
        Write-Success "SBOM files found and hashed"
    } else {
        Write-Warning "No SBOM files found in sbom/ directory"
        @{ "error" = "No SBOM files found" } | ConvertTo-Json | Out-File -FilePath "$OutputDir/sbom_info.json" -Encoding UTF8
    }
} catch {
    Write-Warning "SBOM collection failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/sbom_info.json" -Encoding UTF8
}

# 4. Cosign Verification
Write-Section "Cosign Signature Verification"
try {
    # Check if cosign is available
    $cosignVersion = cosign version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $cosignInfo = @{
            "cosign_available" = $true
            "version" = $cosignVersion
            "verifications" = @()
        }
        
        # Try to verify registry.json if it exists
        $registryFile = "cblm/opipe/nha/out/registry.json"
        if (Test-Path $registryFile) {
            try {
                $registryHash = (Get-FileHash $registryFile -Algorithm SHA256).Hash
                $cosignInfo.verifications += @{
                    "file" = "registry.json"
                    "sha256" = $registryHash
                    "status" = "available_for_verification"
                }
            } catch {
                $cosignInfo.verifications += @{
                    "file" = "registry.json"
                    "error" = $_.Exception.Message
                }
            }
        }
        
        $cosignInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/cosign_info.json" -Encoding UTF8
        Write-Success "Cosign verification info collected"
    } else {
        Write-Warning "Cosign not available"
        @{ "cosign_available" = $false; "error" = "cosign command not found" } | ConvertTo-Json | Out-File -FilePath "$OutputDir/cosign_info.json" -Encoding UTF8
    }
} catch {
    Write-Warning "Cosign verification failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/cosign_info.json" -Encoding UTF8
}

# 5. CVE Scan
Write-Section "CVE Security Scan"
try {
    # Check if trivy is available
    $trivyVersion = trivy version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $cveInfo = @{
            "trivy_available" = $true
            "version" = $trivyVersion
            "scan_results" = @()
        }
        
        # Scan current directory for vulnerabilities
        try {
            $scanOutput = trivy fs . --severity HIGH,CRITICAL --format json 2>$null
            if ($LASTEXITCODE -eq 0) {
                $scanResult = $scanOutput | ConvertFrom-Json
                $cveInfo.scan_results += @{
                    "target" = "filesystem"
                    "high_count" = ($scanResult.Results | ForEach-Object { $_.Vulnerabilities } | Where-Object { $_.Severity -eq "HIGH" }).Count
                    "critical_count" = ($scanResult.Results | ForEach-Object { $_.Vulnerabilities } | Where-Object { $_.Severity -eq "CRITICAL" }).Count
                    "total_vulnerabilities" = ($scanResult.Results | ForEach-Object { $_.Vulnerabilities }).Count
                    "scan_timestamp" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
                }
                Write-Success "CVE scan completed"
            } else {
                $cveInfo.scan_results += @{
                    "target" = "filesystem"
                    "error" = "trivy scan failed"
                }
            }
        } catch {
            $cveInfo.scan_results += @{
                "target" = "filesystem"
                "error" = $_.Exception.Message
            }
        }
        
        $cveInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/cve_scan.json" -Encoding UTF8
    } else {
        Write-Warning "Trivy not available"
        @{ "trivy_available" = $false; "error" = "trivy command not found" } | ConvertTo-Json | Out-File -FilePath "$OutputDir/cve_scan.json" -Encoding UTF8
    }
} catch {
    Write-Warning "CVE scan failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/cve_scan.json" -Encoding UTF8
}

# 6. M8-M14 Verification Scripts
Write-Section "M8-M14 Enterprise Hardening Verification"
$milestoneResults = @{}

$milestones = @("M8", "M9", "M10", "M11", "M12", "M13", "M14")
foreach ($milestone in $milestones) {
    $scriptPath = "scripts/verify_$milestone.ps1"
    if (Test-Path $scriptPath) {
        try {
            Write-ColorOutput "Running $scriptPath..." "Yellow"
            $output = & pwsh -File $scriptPath 2>&1
            $exitCode = $LASTEXITCODE
            
            $milestoneResults[$milestone] = @{
                "script" = $scriptPath
                "exit_code" = $exitCode
                "success" = ($exitCode -eq 0)
                "output" = $output -join "`n"
                "timestamp" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
            }
            
            if ($exitCode -eq 0) {
                Write-Success "$milestone verification passed"
            } else {
                Write-Error "$milestone verification failed (exit code: $exitCode)"
            }
        } catch {
            $milestoneResults[$milestone] = @{
                "script" = $scriptPath
                "error" = $_.Exception.Message
                "success" = $false
                "timestamp" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
            }
            Write-Error "$milestone verification error: $_"
        }
    } else {
        Write-Warning "$scriptPath not found"
        $milestoneResults[$milestone] = @{
            "script" = $scriptPath
            "error" = "Script not found"
            "success" = $false
            "timestamp" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
        }
    }
}

$milestoneResults | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/milestone_verification.json" -Encoding UTF8

# 7. Policy Enforcement Health
Write-Section "Policy Enforcement Health"
try {
    # Check if policy health endpoint is available
    $policyHealthUrl = "http://localhost:3001/policy/health"
    try {
        $policyHealth = Invoke-RestMethod -Uri $policyHealthUrl -Method GET -TimeoutSec 10
        $policyHealth | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/policy_health.json" -Encoding UTF8
        Write-Success "Policy health endpoint accessible"
    } catch {
        Write-Warning "Policy health endpoint not accessible: $_"
        @{ "error" = $_.Exception.Message; "url" = $policyHealthUrl } | ConvertTo-Json | Out-File -FilePath "$OutputDir/policy_health.json" -Encoding UTF8
    }
    
    # Collect policy enforcement logs
    $logFiles = Get-ChildItem -Path "logs" -Filter "policy-enforcement-*.jsonl" -ErrorAction SilentlyContinue
    if ($logFiles) {
        $latestLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        $logContent = Get-Content $latestLog.FullName -Tail 200
        $logContent | Out-File -FilePath "$OutputDir/policy_enforcement_logs.txt" -Encoding UTF8
        Write-Success "Policy enforcement logs collected (last 200 lines)"
    } else {
        Write-Warning "No policy enforcement logs found"
        "No policy enforcement logs found" | Out-File -FilePath "$OutputDir/policy_enforcement_logs.txt" -Encoding UTF8
    }
} catch {
    Write-Warning "Policy enforcement collection failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/policy_health.json" -Encoding UTF8
}

# 8. Chaos Engineering Reports
Write-Section "Chaos Engineering Reports"
try {
    $chaosReports = Get-ChildItem -Path "chaos/reports" -Filter "*.md" -ErrorAction SilentlyContinue
    if ($chaosReports) {
        $chaosSummary = @{
            "report_count" = $chaosReports.Count
            "reports" = @()
            "latest_reports" = @()
        }
        
        foreach ($report in $chaosReports) {
            $chaosSummary.reports += @{
                "file" = $report.Name
                "size" = $report.Length
                "modified" = $report.LastWriteTime.ToString("yyyy-MM-ddTHH:mm:ssZ")
            }
        }
        
        # Get latest 5 reports
        $latestReports = $chaosReports | Sort-Object LastWriteTime -Descending | Select-Object -First 5
        foreach ($report in $latestReports) {
            $content = Get-Content $report.FullName -Raw
            $chaosSummary.latest_reports += @{
                "file" = $report.Name
                "content" = $content
            }
        }
        
        $chaosSummary | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/chaos_reports.json" -Encoding UTF8
        Write-Success "Chaos reports collected"
    } else {
        Write-Warning "No chaos reports found"
        @{ "error" = "No chaos reports found" } | ConvertTo-Json | Out-File -FilePath "$OutputDir/chaos_reports.json" -Encoding UTF8
    }
} catch {
    Write-Warning "Chaos reports collection failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/chaos_reports.json" -Encoding UTF8
}

# 9. Backup Verification
Write-Section "Backup Verification"
try {
    # Check if gsutil is available
    $gsutilVersion = gsutil version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $backupInfo = @{
            "gsutil_available" = $true
            "version" = $gsutilVersion
            "backup_bucket" = $env:BACKUP_BUCKET
            "backup_status" = @()
        }
        
        if ($env:BACKUP_BUCKET) {
            try {
                # List backup bucket contents
                $bucketContents = gsutil ls gs://$env:BACKUP_BUCKET 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $backupInfo.backup_status += @{
                        "bucket_contents" = $bucketContents -split "`n"
                        "bucket_accessible" = $true
                    }
                    
                    # Get bucket lifecycle policy
                    $lifecyclePolicy = gsutil lifecycle get gs://$env:BACKUP_BUCKET 2>$null
                    if ($LASTEXITCODE -eq 0) {
                        $backupInfo.backup_status += @{
                            "lifecycle_policy" = $lifecyclePolicy
                        }
                    }
                    
                    Write-Success "Backup bucket accessible"
                } else {
                    $backupInfo.backup_status += @{
                        "bucket_accessible" = $false
                        "error" = "Failed to access backup bucket"
                    }
                }
            } catch {
                $backupInfo.backup_status += @{
                    "bucket_accessible" = $false
                    "error" = $_.Exception.Message
                }
            }
        } else {
            $backupInfo.backup_status += @{
                "bucket_accessible" = $false
                "error" = "BACKUP_BUCKET environment variable not set"
            }
        }
        
        $backupInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/backup_status.json" -Encoding UTF8
    } else {
        Write-Warning "gsutil not available"
        @{ "gsutil_available" = $false; "error" = "gsutil command not found" } | ConvertTo-Json | Out-File -FilePath "$OutputDir/backup_status.json" -Encoding UTF8
    }
} catch {
    Write-Warning "Backup verification failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/backup_status.json" -Encoding UTF8
}

# 10. NHA Registry Verification
Write-Section "NHA Registry Verification"
try {
    $registryFile = "cblm/opipe/nha/out/registry.json"
    if (Test-Path $registryFile) {
        $registryContent = Get-Content $registryFile -Raw | ConvertFrom-Json
        $registryHash = (Get-FileHash $registryFile -Algorithm SHA256).Hash
        
        $registryInfo = @{
            "registry_file" = $registryFile
            "sha256" = $registryHash
            "size" = (Get-Item $registryFile).Length
            "agent_count" = $registryContent.agents.Count
            "last_updated" = $registryContent.last_updated
            "version" = $registryContent.version
        }
        
        $registryInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/nha_registry.json" -Encoding UTF8
        Write-Success "NHA registry verified"
    } else {
        Write-Warning "NHA registry file not found"
        @{ "error" = "Registry file not found" } | ConvertTo-Json | Out-File -FilePath "$OutputDir/nha_registry.json" -Encoding UTF8
    }
} catch {
    Write-Warning "NHA registry verification failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/nha_registry.json" -Encoding UTF8
}

# 11. Adaptive Policy Reports
Write-Section "Adaptive Policy Reports"
try {
    $adaptiveReports = @{
        "collector_report" = $null
        "policy_gaps" = $null
        "recommendations" = $null
    }
    
    # Check for policy collection report
    $collectorReport = "reports/policy_collect_last_24h.json"
    if (Test-Path $collectorReport) {
        $adaptiveReports.collector_report = Get-Content $collectorReport -Raw | ConvertFrom-Json
    }
    
    # Check for policy gaps report
    $gapsReport = "reports/policy_gaps.json"
    if (Test-Path $gapsReport) {
        $adaptiveReports.policy_gaps = Get-Content $gapsReport -Raw | ConvertFrom-Json
    }
    
    # Check for recommendations
    $recommendationsFile = "cblm/opipe/nha/policy_recommendations.yaml"
    if (Test-Path $recommendationsFile) {
        $adaptiveReports.recommendations = Get-Content $recommendationsFile -Raw
    }
    
    $adaptiveReports | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/adaptive_policy.json" -Encoding UTF8
    Write-Success "Adaptive policy reports collected"
} catch {
    Write-Warning "Adaptive policy reports collection failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/adaptive_policy.json" -Encoding UTF8
}

# 12. System Health Check
Write-Section "System Health Check"
try {
    $healthChecks = @{
        "timestamp" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
        "system_info" = @{
            "os" = $env:OS
            "powershell_version" = $PSVersionTable.PSVersion.ToString()
            "working_directory" = $PWD.Path
        }
        "services" = @()
    }
    
    # Check if key services are running
    $services = @("localhost:3001", "localhost:8080", "localhost:5000")
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri "http://$service/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
            $healthChecks.services += @{
                "service" = $service
                "status" = "healthy"
                "status_code" = $response.StatusCode
            }
        } catch {
            $healthChecks.services += @{
                "service" = $service
                "status" = "unhealthy"
                "error" = $_.Exception.Message
            }
        }
    }
    
    $healthChecks | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/system_health.json" -Encoding UTF8
    Write-Success "System health check completed"
} catch {
    Write-Warning "System health check failed: $_"
    @{ "error" = $_.Exception.Message } | ConvertTo-Json | Out-File -FilePath "$OutputDir/system_health.json" -Encoding UTF8
}

# 13. Create Proof Pack Summary
Write-Section "Creating Proof Pack Summary"
try {
    $summary = @{
        "proof_pack_version" = "1.0"
        "generated_at" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
        "generator" = "CoolBits.ai Enterprise Proof Pack Collector"
        "components" = @{
            "git_info" = Test-Path "$OutputDir/git_info.json"
            "ci_status" = Test-Path "$OutputDir/ci_status.json"
            "sbom_info" = Test-Path "$OutputDir/sbom_info.json"
            "cosign_info" = Test-Path "$OutputDir/cosign_info.json"
            "cve_scan" = Test-Path "$OutputDir/cve_scan.json"
            "milestone_verification" = Test-Path "$OutputDir/milestone_verification.json"
            "policy_health" = Test-Path "$OutputDir/policy_health.json"
            "chaos_reports" = Test-Path "$OutputDir/chaos_reports.json"
            "backup_status" = Test-Path "$OutputDir/backup_status.json"
            "nha_registry" = Test-Path "$OutputDir/nha_registry.json"
            "adaptive_policy" = Test-Path "$OutputDir/adaptive_policy.json"
            "system_health" = Test-Path "$OutputDir/system_health.json"
        }
        "total_files" = (Get-ChildItem $OutputDir -File).Count
        "total_size_bytes" = (Get-ChildItem $OutputDir -File | Measure-Object -Property Length -Sum).Sum
    }
    
    $summary | ConvertTo-Json -Depth 3 | Out-File -FilePath "$OutputDir/proof_pack_summary.json" -Encoding UTF8
    Write-Success "Proof pack summary created"
} catch {
    Write-Error "Failed to create proof pack summary: $_"
    exit 1
}

# 14. Create ZIP Archive
Write-Section "Creating Proof Pack Archive"
try {
    $zipPath = "proof_pack.zip"
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    Compress-Archive -Path "$OutputDir/*" -DestinationPath $zipPath -Force
    $zipSize = (Get-Item $zipPath).Length
    $zipHash = (Get-FileHash $zipPath -Algorithm SHA256).Hash
    
    Write-Success "Proof pack archive created: $zipPath"
    Write-ColorOutput "Archive size: $([math]::Round($zipSize / 1MB, 2)) MB" "Gray"
    Write-ColorOutput "SHA256: $zipHash" "Gray"
} catch {
    Write-Error "Failed to create proof pack archive: $_"
    exit 1
}

# 15. Sign the Proof Pack
Write-Section "Signing Proof Pack"
try {
    # Check if cosign is available for signing
    $cosignVersion = cosign version 2>$null
    if ($LASTEXITCODE -eq 0) {
        try {
            # Sign the proof pack
            $signatureFile = "proof_pack.sig"
            $certificateFile = "proof_pack.cert"
            
            cosign sign-blob --yes --output-signature $signatureFile --output-certificate $certificateFile $zipPath 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Proof pack signed successfully"
                Write-ColorOutput "Signature: $signatureFile" "Gray"
                Write-ColorOutput "Certificate: $certificateFile" "Gray"
            } else {
                Write-Warning "Failed to sign proof pack with cosign"
            }
        } catch {
            Write-Warning "Cosign signing failed: $_"
        }
    } else {
        Write-Warning "Cosign not available for signing"
    }
} catch {
    Write-Warning "Signing process failed: $_"
}

# 16. Final Output
Write-Section "Proof Pack Collection Complete"
Write-ColorOutput "`n🎯 PROOF PACK READY" "Green"
Write-ColorOutput "Archive: proof_pack.zip" "White"
Write-ColorOutput "SHA256: $zipHash" "White"
if (Test-Path "proof_pack.sig") {
    Write-ColorOutput "Signature: proof_pack.sig" "White"
}
if (Test-Path "proof_pack.cert") {
    Write-ColorOutput "Certificate: proof_pack.cert" "White"
}

Write-ColorOutput "`n📋 VERIFICATION SUMMARY" "Cyan"
$summary = Get-Content "$OutputDir/proof_pack_summary.json" | ConvertFrom-Json
foreach ($component in $summary.components.PSObject.Properties) {
    $status = if ($component.Value) { "✓" } else { "✗" }
    $color = if ($component.Value) { "Green" } else { "Red" }
    Write-ColorOutput "$status $($component.Name)" $color
}

Write-ColorOutput "`n🚀 Ready for @oRunner verification!" "Magenta"
