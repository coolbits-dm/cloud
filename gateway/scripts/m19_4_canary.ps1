# --- Hard guard: NU din Cursor/VS Code ---
$ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
if ($parent -match 'cursor|code|code-insiders') {
  Write-Error "Nu rula din Cursor/VS Code. Deschide PowerShell 7 (pwsh) și rulează scriptul acolo."
  exit 1
}
# -----------------------------------------

param(
  [string]$Project = "coolbits-ai",
  [string]$Service = "cb-gw",
  [string]$Region = "europe-west1",
  [string]$NewRevision = "",
  [string]$OldRevision = "",
  [int]$TrafficPercent = 10,
  [switch]$Rollback
)

$ErrorActionPreference = "Stop"
Write-Host "== M19.4 Canary Deployment =="

if ($Rollback) {
  Write-Host "Rolling back to previous revision..."
  
  if (-not $OldRevision) {
    Write-Error "OldRevision required for rollback. Use -OldRevision parameter."
    exit 1
  }
  
  # Rollback to 100% old revision
  gcloud run services update-traffic $Service `
    --region $Region `
    --to-revisions $OldRevision=100
  
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Rollback failed!"
    exit 1
  }
  
  Write-Host "Rollback completed: 100% traffic to $OldRevision"
  exit 0
}

# Canary deployment
if (-not $NewRevision -or -not $OldRevision) {
  Write-Error "NewRevision and OldRevision required for canary deployment."
  exit 1
}

Write-Host "Starting canary deployment..."
Write-Host "New revision: $NewRevision"
Write-Host "Old revision: $OldRevision"
Write-Host "Traffic percentage: $TrafficPercent%"

# Deploy canary
$remainingPercent = 100 - $TrafficPercent
gcloud run services update-traffic $Service `
  --region $Region `
  --to-revisions $NewRevision=$TrafficPercent,$OldRevision=$remainingPercent

if ($LASTEXITCODE -ne 0) {
  Write-Error "Canary deployment failed!"
  exit 1
}

Write-Host "Canary deployed: $TrafficPercent% to $NewRevision, $remainingPercent% to $OldRevision"

# Monitor canary for 5 minutes
Write-Host "Monitoring canary for 5 minutes..."
$monitorDuration = 300  # 5 minutes
$checkInterval = 30     # 30 seconds
$checks = $monitorDuration / $checkInterval

$errorRateThreshold = 3.0
$p95Threshold = 800

for ($i = 1; $i -le $checks; $i++) {
  Write-Host "Check $i/$checks - Monitoring metrics..."
  
  try {
    # Get service URL
    $url = gcloud run services describe $Service --region $Region --format "value(status.url)"
    
    # Get metrics
    $response = Invoke-WebRequest "$url/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 10
    $metrics = $response.Content | ConvertFrom-Json
    
    # Check error rates
    $maxErrorRate = 0
    foreach ($agent in $metrics.error_rates.PSObject.Properties) {
      $rate = $agent.Value
      if ($rate -gt $maxErrorRate) {
        $maxErrorRate = $rate
      }
    }
    
    # Check P95 latencies
    $maxP95 = 0
    foreach ($agent in $metrics.orchestrator_p95_ms.PSObject.Properties) {
      $p95 = $agent.Value
      if ($p95 -gt $maxP95) {
        $maxP95 = $p95
      }
    }
    
    Write-Host "  Max error rate: $maxErrorRate%"
    Write-Host "  Max P95 latency: $maxP95 ms"
    
    # Check thresholds
    if ($maxErrorRate -gt $errorRateThreshold) {
      Write-Warning "Error rate threshold exceeded: $maxErrorRate% > $errorRateThreshold%"
      Write-Host "Rolling back..."
      
      gcloud run services update-traffic $Service `
        --region $Region `
        --to-revisions $OldRevision=100
      
      Write-Host "Rollback completed due to high error rate"
      exit 1
    }
    
    if ($maxP95 -gt $p95Threshold) {
      Write-Warning "P95 latency threshold exceeded: $maxP95 ms > $p95Threshold ms"
      Write-Host "Rolling back..."
      
      gcloud run services update-traffic $Service `
        --region $Region `
        --to-revisions $OldRevision=100
      
      Write-Host "Rollback completed due to high latency"
      exit 1
    }
    
    Write-Host "  ✓ Metrics within thresholds"
    
  } catch {
    Write-Warning "Failed to get metrics: $($_.Exception.Message)"
  }
  
  if ($i -lt $checks) {
    Start-Sleep -Seconds $checkInterval
  }
}

Write-Host "Canary monitoring completed successfully!"
Write-Host "You can now increase traffic percentage or rollback if needed."
Write-Host ""
Write-Host "To increase to 50%:"
Write-Host "gcloud run services update-traffic $Service --region $Region --to-revisions $NewRevision=50,$OldRevision=50"
Write-Host ""
Write-Host "To increase to 100%:"
Write-Host "gcloud run services update-traffic $Service --region $Region --to-revisions $NewRevision=100"
Write-Host ""
Write-Host "To rollback:"
Write-Host "gcloud run services update-traffic $Service --region $Region --to-revisions $OldRevision=100"
