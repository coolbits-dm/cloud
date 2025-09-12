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
  [string]$Project = "coolbits-ai",
  [string]$Service = "cb-gw",
  [string]$Region = "europe-west1",
  [string]$Tag = "m19-3-orch",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Write-Host "== M19.3 Orchestrator Deploy =="

Set-Location $GatewayDir

$Image = "gcr.io/$Project/$Service`:$Tag"

# Build Docker image
Write-Host "Building Docker image: $Image"
docker build -t $Image .

if ($LASTEXITCODE -ne 0) {
  Write-Error "Docker build failed!"
  exit 1
}

# Push to registry
Write-Host "Pushing image to registry: $Image"
gcloud builds submit --tag $Image

if ($LASTEXITCODE -ne 0) {
  Write-Error "Image push failed!"
  exit 1
}

if ($DryRun) {
  Write-Host "Dry run mode - skipping deployment"
  exit 0
}

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..."
gcloud run deploy $Service `
  --image $Image `
  --region $Region `
  --platform managed `
  --allow-unauthenticated `
  --set-env-vars CB_BILLING_MODE=dev,CB_TARIFF_JSON='{"sentiment":-2,"summarize":-2,"tagging":-1,"scribe":-3}',ORCH_ENABLED=1 `
  --max-instances 4 `
  --memory 2Gi `
  --cpu 2 `
  --timeout 300

if ($LASTEXITCODE -ne 0) {
  Write-Error "Cloud Run deployment failed!"
  exit 1
}

# Get service URL
$url = gcloud run services describe $Service --region $Region --format "value(status.url)"
Write-Host "Service URL: $url"

# Health check
Write-Host "Testing deployed service..."
try {
  $response = Invoke-WebRequest "$url/health" -UseBasicParsing -TimeoutSec 10
  Write-Host "Health check OK: $($response.StatusCode)"
} catch {
  Write-Host "Health check failed: $($_.Exception.Message)"
}

# Test Orchestrator endpoint
Write-Host "Testing Orchestrator endpoint..."
try {
  $response = Invoke-WebRequest "$url/v1/flows" -UseBasicParsing -TimeoutSec 10
  Write-Host "Orchestrator flows OK: $($response.StatusCode)"
} catch {
  Write-Host "Orchestrator flows failed: $($_.Exception.Message)"
}

# Test metrics with orchestrator
Write-Host "Testing metrics with orchestrator..."
try {
  $response = Invoke-WebRequest "$url/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 10
  Write-Host "Metrics OK: $($response.StatusCode)"
  $result = $response.Content | ConvertFrom-Json
  Write-Host "Orchestrator queue pending: $($result.orchestrator_queue_pending)"
  Write-Host "Orchestrator P95 times: $($result.orchestrator_p95_ms | ConvertTo-Json)"
} catch {
  Write-Host "Metrics failed: $($_.Exception.Message)"
}

Write-Host "== Deploy completed =="
Write-Host "Gateway URL: $url"
