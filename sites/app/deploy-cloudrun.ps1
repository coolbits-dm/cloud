# Deploy M18.2 pe Cloud Run
# Rulează acest script în PowerShell normal (nu în Cursor)

param(
    [string]$Project = "coolbits-ai",
    [string]$Region = "europe-west1",
    [string]$Service = "coolbits-app"
)

$ErrorActionPreference = "Stop"

Write-Host "== Deploy M18.2 to Cloud Run ==" -ForegroundColor Green

# Setează variabilele de mediu
$env:NEXT_TELEMETRY_DISABLED = "1"
$env:CB_DATA_ROOT = "C:\Users\andre\Desktop\coolbits\artifacts\dev"

# Generează tag unic
$Tag = "m18-ui-$(Get-Date -Format 'yyyyMMdd-HHmm')"
$Image = "gcr.io/$Project/$Service`:$Tag"

Write-Host "Project: $Project" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host "Service: $Service" -ForegroundColor Yellow
Write-Host "Image: $Image" -ForegroundColor Yellow

# Verifică dacă există Dockerfile
if (-not (Test-Path "Dockerfile")) {
    Write-Host "Creating Dockerfile..." -ForegroundColor Yellow
    
    $dockerfile = @"
# syntax=docker/dockerfile:1.7
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copiem standalone + static + public
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/public ./public
COPY --from=build /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node","server.js"]
"@
    
    $dockerfile | Set-Content "Dockerfile"
    Write-Host "Dockerfile created" -ForegroundColor Green
}

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
Write-Host "Testing service..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$url/api/walls/user" -TimeoutSec 30 -ErrorAction Stop
    Write-Host "SUCCESS: Service responding! Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))..." -ForegroundColor Green
} catch {
    Write-Host "WARNING: Service test failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "== Deployment completed! ==" -ForegroundColor Green
Write-Host "Service URL: $url" -ForegroundColor Cyan
