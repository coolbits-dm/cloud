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
Write-Host "== M19.4 Metrics & SLO Validation =="

Set-Location $GatewayDir

# Create artifacts directory
if (-not (Test-Path $ArtifactsDir)) {
  New-Item -ItemType Directory -Path $ArtifactsDir -Force
}

# Test RAG endpoint
Write-Host "Testing RAG endpoint..."
try {
  $ragData = @{
    panel = "business"
    q = "cbLM Economy tariff"
    k = 5
  } | ConvertTo-Json

  $startTime = Get-Date
  $response = Invoke-WebRequest "$ServiceUrl/v1/rag/query" -Method POST -Body $ragData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  $endTime = Get-Date
  $latency = ($endTime - $startTime).TotalMilliseconds
  
  Write-Host "[$($response.StatusCode)] RAG query OK - Latency: $([math]::Round($latency))ms"
  
  if ($latency -gt 300) {
    Write-Warning "RAG latency exceeds SLO threshold (300ms)"
  }
  
} catch {
  Write-Host "[ERR] RAG query failed: $($_.Exception.Message)"
}

# Test NHA endpoint
Write-Host "Testing NHA endpoint..."
try {
  $nhaData = @{
    post = @{
      panel = "user"
      author = "test_user"
      text = "Test post with @nha:sentiment analysis"
    }
  } | ConvertTo-Json

  $startTime = Get-Date
  $response = Invoke-WebRequest "$ServiceUrl/v1/nha/invoke" -Method POST -Body $nhaData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  $endTime = Get-Date
  $latency = ($endTime - $startTime).TotalMilliseconds
  
  Write-Host "[$($response.StatusCode)] NHA invoke OK - Latency: $([math]::Round($latency))ms"
  
} catch {
  Write-Host "[ERR] NHA invoke failed: $($_.Exception.Message)"
}

# Test rate limiting
Write-Host "Testing rate limiting..."
$rateLimitTest = @{
  post = @{
    panel = "user"
    author = "rate_test"
    text = "Rate limit test @nha:sentiment"
  }
} | ConvertTo-Json

$rateLimitHits = 0
for ($i = 1; $i -le 35; $i++) {
  try {
    $response = Invoke-WebRequest "$ServiceUrl/v1/nha/invoke" -Method POST -Body $rateLimitTest -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 429) {
      $rateLimitHits++
    }
  } catch {
    if ($_.Exception.Response.StatusCode -eq 429) {
      $rateLimitHits++
    }
  }
}

Write-Host "Rate limit hits: $rateLimitHits (expected: 5+ after 30 requests)"

# Get metrics snapshot
Write-Host "Getting metrics snapshot..."
try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 10
  $metrics = $response.Content | ConvertFrom-Json
  
  Write-Host "[$($response.StatusCode)] Metrics snapshot OK"
  
  # Save metrics to artifacts
  $metricsPath = "$ArtifactsDir\metrics\m19_4.json"
  $metricsDir = Split-Path $metricsPath -Parent
  if (-not (Test-Path $metricsDir)) {
    New-Item -ItemType Directory -Path $metricsDir -Force
  }
  $metrics | ConvertTo-Json -Depth 10 | Set-Content -Path $metricsPath
  
  Write-Host "Metrics saved to: $metricsPath"
  
  # Validate SLOs
  Write-Host "`n=== SLO Validation ==="
  
  # Check NHA P95
  $nhaP95Ok = $true
  foreach ($agent in $metrics.nha_p95_ms.PSObject.Properties) {
    $p95 = $agent.Value
    if ($p95 -gt 800) {
      Write-Warning "NHA $($agent.Name) P95 exceeds SLO: $p95 ms > 800 ms"
      $nhaP95Ok = $false
    } else {
      Write-Host "✓ NHA $($agent.Name) P95: $p95 ms"
    }
  }
  
  # Check RAG P95
  $ragP95Ok = $true
  foreach ($panel in $metrics.rag_p95_ms.PSObject.Properties) {
    $p95 = $panel.Value
    if ($p95 -gt 300) {
      Write-Warning "RAG $($panel.Name) P95 exceeds SLO: $p95 ms > 300 ms"
      $ragP95Ok = $false
    } else {
      Write-Host "✓ RAG $($panel.Name) P95: $p95 ms"
    }
  }
  
  # Check error rates
  $errorRateOk = $true
  foreach ($agent in $metrics.error_rates.PSObject.Properties) {
    $rate = $agent.Value
    if ($rate -gt 2.0) {
      Write-Warning "Agent $($agent.Name) error rate exceeds SLO: $rate% > 2%"
      $errorRateOk = $false
    } else {
      Write-Host "✓ Agent $($agent.Name) error rate: $rate%"
    }
  }
  
  # Check circuit breakers
  Write-Host "`n=== Circuit Breaker Status ==="
  foreach ($agent in $metrics.circuit_breakers.PSObject.Properties) {
    $isOpen = $agent.Value
    $status = if ($isOpen) { "OPEN" } else { "CLOSED" }
    Write-Host "Circuit breaker $($agent.Name): $status"
  }
  
  # Overall SLO status
  Write-Host "`n=== Overall SLO Status ==="
  Write-Host "Node P95 OK: $($metrics.slo_status.node_p95_ok)"
  Write-Host "RAG P95 OK: $($metrics.slo_status.rag_p95_ok)"
  Write-Host "Error Rate OK: $($metrics.slo_status.error_rate_ok)"
  
  $overallOk = $metrics.slo_status.node_p95_ok -and $metrics.slo_status.rag_p95_ok -and $metrics.slo_status.error_rate_ok
  Write-Host "Overall SLO Status: $(if ($overallOk) { 'PASS' } else { 'FAIL' })"
  
} catch {
  Write-Host "[ERR] Metrics snapshot failed: $($_.Exception.Message)"
}

# Test Prometheus metrics
Write-Host "`nTesting Prometheus metrics..."
try {
  $response = Invoke-WebRequest "$ServiceUrl/metrics" -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($response.StatusCode)] Prometheus metrics OK"
  
  # Save Prometheus metrics
  $prometheusPath = "$ArtifactsDir\metrics\prometheus.txt"
  $response.Content | Set-Content -Path $prometheusPath
  Write-Host "Prometheus metrics saved to: $prometheusPath"
  
} catch {
  Write-Host "[ERR] Prometheus metrics failed: $($_.Exception.Message)"
}

Write-Host "`n== Metrics validation completed =="
Write-Host "Check artifacts directory for saved metrics: $ArtifactsDir\metrics\"
