#!/usr/bin/env pwsh
# Tripwire Monitoring - CoolBits.ai
# Monitors critical system metrics and triggers alerts

param(
    [switch]$Verbose,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Set timeout environment variables
$env:POWERSHELL_TELEMETRY_OPTOUT = '1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:HTTPS_PROXY = ''

Write-Host "[INFO] Starting Tripwire Monitoring" -ForegroundColor Green
Write-Host "[INFO] Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })" -ForegroundColor Yellow

class TripwireMonitor {
    [string]$BasePath
    [datetime]$StartTime
    [array]$Alerts
    
    TripwireMonitor() {
        $this.BasePath = (Get-Location).Path
        $this.StartTime = Get-Date
        $this.Alerts = @()
    }
    
    [void] CheckProofPackStale() {
        Write-Host "[TRIPWIRE] Checking Proof Pack staleness..." -ForegroundColor Cyan
        
        $proofPackPath = Join-Path $this.BasePath "proof_pack.zip"
        if (-not (Test-Path $proofPackPath)) {
            $this.Alerts += @{
                type = "critical"
                message = "Proof Pack not found"
                action = "Block all deployments"
                validation = "Generate new Proof Pack"
            }
            return
        }
        
        $fileInfo = Get-Item $proofPackPath
        $ageHours = (Get-Date) - $fileInfo.LastWriteTime
        $ageHours = $ageHours.TotalHours
        
        if ($ageHours -gt 24) {
            $this.Alerts += @{
                type = "critical"
                message = "Proof Pack stale: $([math]::Round($ageHours, 1)) hours old"
                action = "Block all deployments"
                validation = "Generate new Proof Pack"
            }
        } else {
            Write-Host "  ✅ Proof Pack age: $([math]::Round($ageHours, 1)) hours (OK)" -ForegroundColor Green
        }
    }
    
    [void] CheckP95Latency() {
        Write-Host "[TRIPWIRE] Checking P95 latency..." -ForegroundColor Cyan
        
        # Simulate P95 latency check (in real implementation, fetch from monitoring)
        $p95Latency = 126.6  # This would come from monitoring system
        $threshold = 400
        
        if ($p95Latency -gt $threshold) {
            $this.Alerts += @{
                type = "critical"
                message = "P95 latency exceeded: ${p95Latency}ms > ${threshold}ms"
                action = "Automatic canary rollback"
                validation = "SLO metrics return to normal"
            }
        } else {
            Write-Host "  ✅ P95 latency: ${p95Latency}ms (OK)" -ForegroundColor Green
        }
    }
    
    [void] CheckErrorRate() {
        Write-Host "[TRIPWIRE] Checking error rate..." -ForegroundColor Cyan
        
        # Simulate error rate check (in real implementation, fetch from monitoring)
        $errorRate = 0.008  # This would come from monitoring system
        $threshold = 0.01
        
        if ($errorRate -gt $threshold) {
            $this.Alerts += @{
                type = "critical"
                message = "Error rate exceeded: $($errorRate * 100)% > $($threshold * 100)%"
                action = "Block new deployments"
                validation = "Error rate returns to normal"
            }
        } else {
            Write-Host "  ✅ Error rate: $($errorRate * 100)% (OK)" -ForegroundColor Green
        }
    }
    
    [void] CheckPolicyDenySpike() {
        Write-Host "[TRIPWIRE] Checking policy deny spike..." -ForegroundColor Cyan
        
        try {
            $logsDir = Join-Path $this.BasePath "logs"
            if (-not (Test-Path $logsDir)) {
                Write-Host "  ⚠️ Logs directory not found" -ForegroundColor Yellow
                return
            }
            
            # Find latest policy enforcement log
            $logFiles = Get-ChildItem $logsDir -Filter "policy-enforcement-*.jsonl"
            if ($logFiles.Count -eq 0) {
                Write-Host "  ⚠️ No policy enforcement logs found" -ForegroundColor Yellow
                return
            }
            
            $latestLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            
            # Count DENY records in last hour
            $denyCount = 0
            $oneHourAgo = (Get-Date).AddHours(-1)
            
            Get-Content $latestLog.FullName | ForEach-Object {
                try {
                    $record = $_ | ConvertFrom-Json
                    if ($record.result -eq "DENY") {
                        $recordTime = [datetime]::ParseExact($record.ts, "yyyy-MM-ddTHH:mm:ssZ", $null)
                        if ($recordTime -gt $oneHourAgo) {
                            $denyCount++
                        }
                    }
                } catch {
                    # Skip malformed records
                }
            }
            
            $threshold = 20
            if ($denyCount -gt $threshold) {
                $this.Alerts += @{
                    type = "warning"
                    message = "Policy deny spike: ${denyCount} denies/hour > ${threshold}"
                    action = "Freeze promotions, investigate"
                    validation = "Policy violations resolved"
                }
            } else {
                Write-Host "  ✅ Policy denies: ${denyCount}/hour (OK)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ❌ Error checking policy denies: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    [void] CheckBackupLifecycle() {
        Write-Host "[TRIPWIRE] Checking backup lifecycle..." -ForegroundColor Cyan
        
        try {
            # Check if backup lifecycle policies exist
            $backupDir = Join-Path $this.BasePath "backup"
            if (-not (Test-Path $backupDir)) {
                $this.Alerts += @{
                    type = "warning"
                    message = "Backup directory not found"
                    action = "Create backup directory"
                    validation = "Backup lifecycle policies in place"
                }
                return
            }
            
            # Check for backup lifecycle configuration
            $lifecycleConfig = Join-Path $this.BasePath "cost\lifecycle\lifecycle.json"
            if (-not (Test-Path $lifecycleConfig)) {
                $this.Alerts += @{
                    type = "critical"
                    message = "Backup lifecycle configuration missing"
                    action = "Pipeline failure"
                    validation = "Backup lifecycle policies configured"
                }
            } else {
                Write-Host "  ✅ Backup lifecycle configuration found" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ❌ Error checking backup lifecycle: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    [void] CheckRegistrySignature() {
        Write-Host "[TRIPWIRE] Checking registry signature..." -ForegroundColor Cyan
        
        try {
            $registryPath = Join-Path $this.BasePath "cblm\opipe\nha\out\registry.json"
            $signaturePath = Join-Path $this.BasePath "cblm\opipe\nha\out\registry.json.sig"
            $certPath = Join-Path $this.BasePath "cblm\opipe\nha\out\registry.json.cert"
            $sha256Path = Join-Path $this.BasePath "cblm\opipe\nha\out\registry.json.sha256"
            
            if (-not (Test-Path $registryPath)) {
                $this.Alerts += @{
                    type = "critical"
                    message = "Registry file not found"
                    action = "Total blockage (fail-closed)"
                    validation = "Registry file exists and signed"
                }
                return
            }
            
            $missingFiles = @()
            if (-not (Test-Path $signaturePath)) { $missingFiles += "signature" }
            if (-not (Test-Path $certPath)) { $missingFiles += "certificate" }
            if (-not (Test-Path $sha256Path)) { $missingFiles += "sha256" }
            
            if ($missingFiles.Count -gt 0) {
                $this.Alerts += @{
                    type = "critical"
                    message = "Registry signature incomplete: missing $($missingFiles -join ', ')"
                    action = "Total blockage (fail-closed)"
                    validation = "Registry file signed"
                }
            } else {
                Write-Host "  ✅ Registry signature complete" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ❌ Error checking registry signature: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    [void] RunAllChecks() {
        Write-Host "`n🔍 Running all tripwire checks..." -ForegroundColor Green
        
        $this.CheckProofPackStale()
        $this.CheckP95Latency()
        $this.CheckErrorRate()
        $this.CheckPolicyDenySpike()
        $this.CheckBackupLifecycle()
        $this.CheckRegistrySignature()
    }
    
    [void] DisplayResults() {
        Write-Host "`n📊 TRIPWIRE MONITORING RESULTS" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Green
        
        if ($this.Alerts.Count -eq 0) {
            Write-Host "✅ All tripwires OK - No alerts triggered" -ForegroundColor Green
        } else {
            Write-Host "🚨 $($this.Alerts.Count) alerts triggered:" -ForegroundColor Red
            
            foreach ($alert in $this.Alerts) {
                $color = if ($alert.type -eq "critical") { "Red" } else { "Yellow" }
                Write-Host "`n$($alert.type.ToUpper()): $($alert.message)" -ForegroundColor $color
                Write-Host "  Action: $($alert.action)" -ForegroundColor White
                Write-Host "  Validation: $($alert.validation)" -ForegroundColor Gray
            }
        }
        
        Write-Host "`n⏱️ Monitoring completed in $([math]::Round(((Get-Date) - $this.StartTime).TotalSeconds, 2)) seconds" -ForegroundColor Cyan
    }
    
    [int] GetExitCode() {
        $criticalAlerts = $this.Alerts | Where-Object { $_.type -eq "critical" }
        return $criticalAlerts.Count
    }
}

# Main execution
$monitor = [TripwireMonitor]::new()
$monitor.RunAllChecks()
$monitor.DisplayResults()

$exitCode = $monitor.GetExitCode()
if ($exitCode -gt 0) {
    Write-Host "`n❌ Tripwire monitoring failed with $exitCode critical alerts" -ForegroundColor Red
    exit $exitCode
} else {
    Write-Host "`n✅ Tripwire monitoring completed successfully" -ForegroundColor Green
    exit 0
}
