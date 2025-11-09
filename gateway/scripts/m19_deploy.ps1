# Gateway Deploy Script cu proxy extern
. "$PSScriptRoot\..\..\scripts\_pwsh_proxy.ps1"

Write-Host "=== Gateway Deploy (M19) ===" -ForegroundColor Cyan

# 1) Build Gateway
Write-Host "Building Gateway..." -ForegroundColor Yellow
Set-Location "C:\Users\andre\Desktop\coolbits\gateway"
if (Test-Path venv) { 
  Write-Host "Activating virtual environment..." -ForegroundColor Yellow
  & .\venv\Scripts\Activate.ps1
}

# 2) Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
$project = "coolbits-ai"
$region = "europe-west1"
$service = "coolbits-gw"
$tag = "m19-gw-$(Get-Date -Format yyyyMMdd-HHmm)"

# Build and push
gcloud builds submit --tag "gcr.io/$project/$service`:$tag" --region $region

# Deploy
gcloud run deploy $service `
  --image "gcr.io/$project/$service`:$tag" `
  --region $region `
  --platform managed `
  --allow-unauthenticated `
  --set-env-vars CB_BILLING_MODE=dev,CB_HMAC_KEY=dev-secret-optional `
  --concurrency=40 `
  --min-instances=1 `
  --max-instances=10

# Get URL
$url = (gcloud run services describe $service --region $region --format "value(status.url)")
Write-Host "Gateway deployed: $url" -ForegroundColor Green

# Test health
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
try {
  $health = Invoke-WebRequest "$url/health" -UseBasicParsing -TimeoutSec 10
  if ($health.StatusCode -eq 200) {
    Write-Host "SUCCESS: Gateway is healthy" -ForegroundColor Green
  } else {
    Write-Host "WARNING: Gateway health check returned $($health.StatusCode)" -ForegroundColor Yellow
  }
} catch {
  Write-Host "WARNING: Gateway health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "=== Gateway Deploy Complete ===" -ForegroundColor Green