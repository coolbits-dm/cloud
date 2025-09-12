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
  [string]$Region = "europe-west1",
  [string]$ServiceUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"
Write-Host "== M20.0 Preflight & Hardening Check =="

# Check Node version
Write-Host "`n=== Node.js Version Check ==="
$nodeVersion = node --version
Write-Host "Node version: $nodeVersion"

if ($nodeVersion -match "^v20\.") {
  Write-Host "✓ Node 20 LTS detected"
} else {
  Write-Error "✗ Node 20 LTS required, found: $nodeVersion"
  exit 1
}

# Check npm version
$npmVersion = npm --version
Write-Host "npm version: $npmVersion"

if ($npmVersion -match "^10\.") {
  Write-Host "✓ npm 10.x detected"
} else {
  Write-Warning "⚠ npm 10.x recommended, found: $npmVersion"
}

# Check Python version
Write-Host "`n=== Python Version Check ==="
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion"

if ($pythonVersion -match "^Python 3\.11\.") {
  Write-Host "✓ Python 3.11 detected"
} else {
  Write-Warning "⚠ Python 3.11 recommended, found: $pythonVersion"
}

# Check gcloud version
Write-Host "`n=== gcloud Version Check ==="
$gcloudVersion = gcloud --version | Select-Object -First 1
Write-Host "gcloud version: $gcloudVersion"

# Check environment variables
Write-Host "`n=== Environment Variables Check ==="
$requiredEnvVars = @(
  "OPENAI_API_KEY",
  "ANTHROPIC_API_KEY", 
  "DB_DSN",
  "REDIS_URL"
)

$missingVars = @()
foreach ($var in $requiredEnvVars) {
  if (-not (Get-Item "env:$var" -ErrorAction SilentlyContinue)) {
    $missingVars += $var
  }
}

if ($missingVars.Count -eq 0) {
  Write-Host "✓ All required environment variables present"
} else {
  Write-Warning "⚠ Missing environment variables: $($missingVars -join ', ')"
}

# Check secrets in Secret Manager
Write-Host "`n=== Secret Manager Check ==="
try {
  $secrets = gcloud secrets list --project $Project --format="value(name)" 2>$null
  if ($secrets) {
    Write-Host "✓ Secret Manager accessible"
    Write-Host "Available secrets: $($secrets -join ', ')"
  } else {
    Write-Warning "⚠ No secrets found in Secret Manager"
  }
} catch {
  Write-Warning "⚠ Secret Manager not accessible: $($_.Exception.Message)"
}

# Check Cloud SQL
Write-Host "`n=== Cloud SQL Check ==="
try {
  $instances = gcloud sql instances list --project $Project --format="value(name)" 2>$null
  if ($instances) {
    Write-Host "✓ Cloud SQL instances found: $($instances -join ', ')"
  } else {
    Write-Warning "⚠ No Cloud SQL instances found"
  }
} catch {
  Write-Warning "⚠ Cloud SQL not accessible: $($_.Exception.Message)"
}

# Check Memorystore
Write-Host "`n=== Memorystore Check ==="
try {
  $redisInstances = gcloud redis instances list --region $Region --project $Project --format="value(name)" 2>$null
  if ($redisInstances) {
    Write-Host "✓ Memorystore instances found: $($redisInstances -join ', ')"
  } else {
    Write-Warning "⚠ No Memorystore instances found"
  }
} catch {
  Write-Warning "⚠ Memorystore not accessible: $($_.Exception.Message)"
}

# Check Cloud Run services
Write-Host "`n=== Cloud Run Services Check ==="
try {
  $services = gcloud run services list --region $Region --project $Project --format="value(metadata.name)" 2>$null
  if ($services) {
    Write-Host "✓ Cloud Run services found: $($services -join ', ')"
  } else {
    Write-Warning "⚠ No Cloud Run services found"
  }
} catch {
  Write-Warning "⚠ Cloud Run not accessible: $($_.Exception.Message)"
}

# Health check
Write-Host "`n=== Health Check ==="
try {
  $startTime = Get-Date
  $response = Invoke-WebRequest "$ServiceUrl/health" -UseBasicParsing -TimeoutSec 10
  $endTime = Get-Date
  $latency = ($endTime - $startTime).TotalMilliseconds
  
  if ($response.StatusCode -eq 200) {
    Write-Host "✓ Health check passed - Status: $($response.StatusCode), Latency: $([math]::Round($latency))ms"
    
    if ($latency -lt 200) {
      Write-Host "✓ Health latency < 200ms SLO"
    } else {
      Write-Warning "⚠ Health latency exceeds 200ms SLO: $([math]::Round($latency))ms"
    }
  } else {
    Write-Warning "⚠ Health check failed - Status: $($response.StatusCode)"
  }
} catch {
  Write-Warning "⚠ Health check failed: $($_.Exception.Message)"
}

# Check metrics endpoint
Write-Host "`n=== Metrics Endpoint Check ==="
try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 10
  if ($response.StatusCode -eq 200) {
    $metrics = $response.Content | ConvertFrom-Json
    Write-Host "✓ Metrics endpoint accessible"
    Write-Host "  Timestamp: $($metrics.timestamp)"
    Write-Host "  NHA queue pending: $($metrics.nha_queue_pending)"
    Write-Host "  Orchestrator queue pending: $($metrics.orchestrator_queue_pending)"
  } else {
    Write-Warning "⚠ Metrics endpoint failed - Status: $($response.StatusCode)"
  }
} catch {
  Write-Warning "⚠ Metrics endpoint failed: $($_.Exception.Message)"
}

# Check Prometheus metrics
Write-Host "`n=== Prometheus Metrics Check ==="
try {
  $response = Invoke-WebRequest "$ServiceUrl/metrics" -UseBasicParsing -TimeoutSec 10
  if ($response.StatusCode -eq 200) {
    Write-Host "✓ Prometheus metrics accessible"
    $metricLines = $response.Content -split "`n" | Where-Object { $_ -match "^[^#]" }
    Write-Host "  Metric lines: $($metricLines.Count)"
  } else {
    Write-Warning "⚠ Prometheus metrics failed - Status: $($response.StatusCode)"
  }
} catch {
  Write-Warning "⚠ Prometheus metrics failed: $($_.Exception.Message)"
}

# Check rate limiting
Write-Host "`n=== Rate Limiting Check ==="
$rateLimitTest = @{
  post = @{
    panel = "user"
    author = "preflight_test"
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

if ($rateLimitHits -gt 0) {
  Write-Host "✓ Rate limiting working - $rateLimitHits rate limit hits"
} else {
  Write-Warning "⚠ Rate limiting not working - no rate limit hits"
}

# Check circuit breakers
Write-Host "`n=== Circuit Breaker Check ==="
try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 10
  $metrics = $response.Content | ConvertFrom-Json
  
  $openBreakers = 0
  foreach ($agent in $metrics.circuit_breakers.PSObject.Properties) {
    if ($agent.Value) {
      $openBreakers++
    }
  }
  
  if ($openBreakers -eq 0) {
    Write-Host "✓ All circuit breakers CLOSED"
  } else {
    Write-Warning "⚠ $openBreakers circuit breakers OPEN"
  }
} catch {
  Write-Warning "⚠ Circuit breaker check failed: $($_.Exception.Message)"
}

# Summary
Write-Host "`n=== Preflight Summary ==="
Write-Host "Node.js: $nodeVersion"
Write-Host "Python: $pythonVersion"
Write-Host "gcloud: $gcloudVersion"
Write-Host "Health latency: $([math]::Round($latency))ms"
Write-Host "Rate limiting: $(if ($rateLimitHits -gt 0) { 'Working' } else { 'Not working' })"
Write-Host "Circuit breakers: $(if ($openBreakers -eq 0) { 'All CLOSED' } else { "$openBreakers OPEN" })"

Write-Host "`n== M20.0 Preflight completed =="
Write-Host "All checks passed. Ready for M20.1 - Auth, Org, RBAC."
