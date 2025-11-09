# Build și deploy M18.2 (fallback mode - next start)
# Rulează în PowerShell 7 (pwsh), nu în Cursor

param(
    [switch]$SkipBuild = $false,
    [switch]$SkipDeploy = $false
)

$ErrorActionPreference = "Stop"

Write-Host "== M18.2 Build & Deploy (Fallback Mode) ==" -ForegroundColor Green

# Setează variabilele de mediu
$env:NEXT_TELEMETRY_DISABLED = "1"
$env:CB_DATA_ROOT = "C:\Users\andre\Desktop\coolbits\artifacts\dev"

Write-Host "Node version: $(node -v)" -ForegroundColor Yellow
Write-Host "NPM version: $(npm -v)" -ForegroundColor Yellow

if (-not $SkipBuild) {
    Write-Host "=== BUILDING LOCAL ===" -ForegroundColor Cyan
    
    # Curăță directorul
    Write-Host "Cleaning directories..." -ForegroundColor Yellow
    if (Test-Path "node_modules") { 
        Remove-Item "node_modules" -Recurse -Force 
        Write-Host "Removed node_modules" -ForegroundColor Green
    }
    if (Test-Path ".next") { 
        Remove-Item ".next" -Recurse -Force 
        Write-Host "Removed .next" -ForegroundColor Green
    }
    
    # Instalează dependențele
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    if (Test-Path "package-lock.json") {
        npm ci
    } else {
        npm install
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "NPM install failed!" -ForegroundColor Red
        exit 1
    }
    
    # Typecheck
    Write-Host "Running typecheck..." -ForegroundColor Yellow
    npm run typecheck
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Typecheck failed!" -ForegroundColor Red
        exit 1
    }
    
    # Build
    Write-Host "Building Next.js app..." -ForegroundColor Yellow
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Build completed successfully!" -ForegroundColor Green
    
    # Test local
    Write-Host "Testing local server..." -ForegroundColor Yellow
    $job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        $env:CB_DATA_ROOT = "C:\Users\andre\Desktop\coolbits\artifacts\dev"
        $env:NEXT_TELEMETRY_DISABLED = "1"
        npm start
    }
    
    Start-Sleep -Seconds 5
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/walls/user" -TimeoutSec 10 -ErrorAction Stop
        Write-Host "SUCCESS: Local server responding! Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))..." -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Local server test failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -ErrorAction SilentlyContinue
    
    Write-Host "=== LOCAL BUILD COMPLETED ===" -ForegroundColor Green
}

if (-not $SkipDeploy) {
    Write-Host "=== DEPLOYING TO CLOUD RUN ===" -ForegroundColor Cyan
    
    $Project = "coolbits-ai"
    $Region = "europe-west1"
    $Service = "coolbits-app"
    $Tag = "m18-ui-non-standalone-$(Get-Date -Format 'yyyyMMdd-HHmm')"
    $Image = "gcr.io/$Project/$Service`:$Tag"
    
    Write-Host "Project: $Project" -ForegroundColor Yellow
    Write-Host "Region: $Region" -ForegroundColor Yellow
    Write-Host "Service: $Service" -ForegroundColor Yellow
    Write-Host "Image: $Image" -ForegroundColor Yellow
    
    # Build Docker image
    Write-Host "Building Docker image..." -ForegroundColor Yellow
    gcloud builds submit --tag $Image --timeout=1200
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Docker image built successfully!" -ForegroundColor Green
    
    # Deploy pe Cloud Run
    Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
    gcloud run deploy $Service `
        --image $Image `
        --region $Region `
        --platform managed `
        --allow-unauthenticated `
        --set-env-vars "CB_DATA_ROOT=/app/artifacts/dev,NEXT_TELEMETRY_DISABLED=1" `
        --max-instances 2 `
        --memory 1Gi `
        --cpu 1 `
        --timeout 300
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Cloud Run deployment failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Deployment successful!" -ForegroundColor Green
    
    # Obține URL-ul serviciului
    $url = gcloud run services describe $Service --region $Region --format "value(status.url)"
    Write-Host "Service URL: $url" -ForegroundColor Cyan
    
    # Testează serviciul
    Write-Host "Testing deployed service..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "$url/api/walls/user" -TimeoutSec 30 -ErrorAction Stop
        Write-Host "SUCCESS: Service responding! Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))..." -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Service test failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    Write-Host "=== DEPLOYMENT COMPLETED ===" -ForegroundColor Green
    Write-Host "Service URL: $url" -ForegroundColor Cyan
}

Write-Host "== M18.2 COMPLETED SUCCESSFULLY! ==" -ForegroundColor Green
