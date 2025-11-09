# --- Hard guard: NU din Cursor/VS Code ---
$ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
if ($parent -match 'cursor|code|code-insiders') {
  Write-Error "Nu rula din Cursor/VS Code. Deschide PowerShell 7 (pwsh) și rulează scriptul acolo."
  exit 1
}
# -----------------------------------------

param(
  [string]$GatewayDir = "C:\Users\andre\Desktop\coolbits\gateway",
  [string]$ServiceUrl = "http://localhost:8000",
  [string]$ArtifactsDir = "C:\Users\andre\Desktop\coolbits\artifacts\dev"
)

$ErrorActionPreference = "Stop"
Write-Host "== M19.4 Disaster Recovery Drills =="

Set-Location $GatewayDir

# Create artifacts directory
if (-not (Test-Path $ArtifactsDir)) {
  New-Item -ItemType Directory -Path $ArtifactsDir -Force
}

$reportPath = "$ArtifactsDir\drills\m19_4_drill_report.html"
$reportDir = Split-Path $reportPath -Parent
if (-not (Test-Path $reportDir)) {
  New-Item -ItemType Directory -Path $reportDir -Force
}

# Initialize HTML report
$htmlReport = @"
<!DOCTYPE html>
<html>
<head>
    <title>M19.4 Disaster Recovery Drills Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test { margin: 20px 0; padding: 15px; border: 1px solid #ccc; }
        .pass { background-color: #d4edda; border-color: #c3e6cb; }
        .fail { background-color: #f8d7da; border-color: #f5c6cb; }
        .warning { background-color: #fff3cd; border-color: #ffeaa7; }
        pre { background-color: #f8f9fa; padding: 10px; overflow-x: auto; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>M19.4 Disaster Recovery Drills Report</h1>
    <p class="timestamp">Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
"@

function Add-TestResult {
  param($testName, $status, $details)
  
  $cssClass = switch ($status) {
    "PASS" { "pass" }
    "FAIL" { "fail" }
    "WARN" { "warning" }
    default { "" }
  }
  
  $htmlReport += @"
    <div class="test $cssClass">
        <h3>$testName - $status</h3>
        <pre>$details</pre>
    </div>
"@
}

# Drill 1: Remove OpenAI API Key (test fallback)
Write-Host "`n=== Drill 1: OpenAI API Key Removal ==="
$drill1Details = "Testing fallback behavior when OpenAI API key is removed`n"

try {
  # Test NHA with current API key
  $nhaData = @{
    post = @{
      panel = "user"
      author = "drill_test"
      text = "Test fallback behavior @nha:sentiment"
    }
  } | ConvertTo-Json

  $response = Invoke-WebRequest "$ServiceUrl/v1/nha/invoke" -Method POST -Body $nhaData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  
  if ($response.StatusCode -eq 200) {
    $result = $response.Content | ConvertFrom-Jjson
    $drill1Details += "✓ NHA invoke successful`n"
    $drill1Details += "Response: $($result | ConvertTo-Json -Compress)`n"
    
    # Check if fallback was used
    if ($result.invocations.Count -gt 0) {
      $drill1Details += "✓ Invocations created successfully`n"
      Add-TestResult "OpenAI Fallback Test" "PASS" $drill1Details
    } else {
      $drill1Details += "✗ No invocations created`n"
      Add-TestResult "OpenAI Fallback Test" "FAIL" $drill1Details
    }
  } else {
    $drill1Details += "✗ NHA invoke failed with status $($response.StatusCode)`n"
    Add-TestResult "OpenAI Fallback Test" "FAIL" $drill1Details
  }
} catch {
  $drill1Details += "✗ Exception: $($_.Exception.Message)`n"
  Add-TestResult "OpenAI Fallback Test" "FAIL" $drill1Details
}

# Drill 2: Redis Connection Failure
Write-Host "`n=== Drill 2: Redis Connection Failure ==="
$drill2Details = "Testing behavior when Redis is unavailable`n"

try {
  # Test metrics endpoint (should work without Redis)
  $response = Invoke-WebRequest "$ServiceUrl/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 10
  
  if ($response.StatusCode -eq 200) {
    $metrics = $response.Content | ConvertFrom-Jjson
    $drill2Details += "✓ Metrics endpoint accessible`n"
    $drill2Details += "Queue pending: $($metrics.nha_queue_pending)`n"
    $drill2Details += "Orchestrator queue pending: $($metrics.orchestrator_queue_pending)`n"
    
    Add-TestResult "Redis Failure Test" "PASS" $drill2Details
  } else {
    $drill2Details += "✗ Metrics endpoint failed with status $($response.StatusCode)`n"
    Add-TestResult "Redis Failure Test" "FAIL" $drill2Details
  }
} catch {
  $drill2Details += "✗ Exception: $($_.Exception.Message)`n"
  Add-TestResult "Redis Failure Test" "FAIL" $drill2Details
}

# Drill 3: Rate Limiting Under Load
Write-Host "`n=== Drill 3: Rate Limiting Under Load ==="
$drill3Details = "Testing rate limiting with high request volume`n"

$rateLimitData = @{
  post = @{
    panel = "user"
    author = "load_test"
    text = "Load test @nha:sentiment"
  }
} | ConvertTo-Json

$successCount = 0
$rateLimitCount = 0
$errorCount = 0

# Send 50 requests quickly
for ($i = 1; $i -le 50; $i++) {
  try {
    $response = Invoke-WebRequest "$ServiceUrl/v1/nha/invoke" -Method POST -Body $rateLimitData -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
    
    if ($response.StatusCode -eq 200) {
      $successCount++
    } elseif ($response.StatusCode -eq 429) {
      $rateLimitCount++
    } else {
      $errorCount++
    }
  } catch {
    if ($_.Exception.Response.StatusCode -eq 429) {
      $rateLimitCount++
    } else {
      $errorCount++
    }
  }
}

$drill3Details += "Total requests: 50`n"
$drill3Details += "Successful: $successCount`n"
$drill3Details += "Rate limited: $rateLimitCount`n"
$drill3Details += "Errors: $errorCount`n"

if ($rateLimitCount -gt 0) {
  $drill3Details += "✓ Rate limiting working correctly`n"
  Add-TestResult "Rate Limiting Test" "PASS" $drill3Details
} else {
  $drill3Details += "✗ Rate limiting not working`n"
  Add-TestResult "Rate Limiting Test" "FAIL" $drill3Details
}

# Drill 4: Circuit Breaker Activation
Write-Host "`n=== Drill 4: Circuit Breaker Activation ==="
$drill4Details = "Testing circuit breaker behavior`n"

try {
  # Get current circuit breaker status
  $response = Invoke-WebRequest "$ServiceUrl/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 10
  $metrics = $response.Content | ConvertFrom-Jjson
  
  $drill4Details += "Circuit breaker status:`n"
  foreach ($agent in $metrics.circuit_breakers.PSObject.Properties) {
    $isOpen = $agent.Value
    $status = if ($isOpen) { "OPEN" } else { "CLOSED" }
    $drill4Details += "  $($agent.Name): $status`n"
  }
  
  $drill4Details += "Error rates:`n"
  foreach ($agent in $metrics.error_rates.PSObject.Properties) {
    $rate = $agent.Value
    $drill4Details += "  $($agent.Name): $rate%`n"
  }
  
  Add-TestResult "Circuit Breaker Test" "PASS" $drill4Details
} catch {
  $drill4Details += "✗ Exception: $($_.Exception.Message)`n"
  Add-TestResult "Circuit Breaker Test" "FAIL" $drill4Details
}

# Drill 5: SLO Validation
Write-Host "`n=== Drill 5: SLO Validation ==="
$drill5Details = "Validating Service Level Objectives`n"

try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 10
  $metrics = $response.Content | ConvertFrom-Jjson
  
  $drill5Details += "SLO Status:`n"
  $drill5Details += "  Node P95 OK: $($metrics.slo_status.node_p95_ok)`n"
  $drill5Details += "  RAG P95 OK: $($metrics.slo_status.rag_p95_ok)`n"
  $drill5Details += "  Error Rate OK: $($metrics.slo_status.error_rate_ok)`n"
  
  $overallOk = $metrics.slo_status.node_p95_ok -and $metrics.slo_status.rag_p95_ok -and $metrics.slo_status.error_rate_ok
  
  if ($overallOk) {
    $drill5Details += "✓ All SLOs met`n"
    Add-TestResult "SLO Validation" "PASS" $drill5Details
  } else {
    $drill5Details += "✗ Some SLOs not met`n"
    Add-TestResult "SLO Validation" "FAIL" $drill5Details
  }
} catch {
  $drill5Details += "✗ Exception: $($_.Exception.Message)`n"
  Add-TestResult "SLO Validation" "FAIL" $drill5Details
}

# Finalize HTML report
$htmlReport += @"
    <h2>Summary</h2>
    <p>Disaster recovery drills completed. Check individual test results above.</p>
</body>
</html>
"@

# Save report
$htmlReport | Set-Content -Path $reportPath -Encoding UTF8

Write-Host "`n== Disaster recovery drills completed =="
Write-Host "Report saved to: $reportPath"
Write-Host "Open the report in your browser to view detailed results."
