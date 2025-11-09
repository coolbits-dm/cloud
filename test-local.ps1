# Test local M18.2 (fallback cu next start)
# Rulează în PowerShell 7 (pwsh), NU în Cursor

$ErrorActionPreference = "Stop"

Write-Host "== M18.2 Local Test (Fallback Mode) ==" -ForegroundColor Green

# Setează variabilele de mediu
$env:NEXT_TELEMETRY_DISABLED = "1"
$env:CB_DATA_ROOT = "C:\Users\andre\Desktop\coolbits\artifacts\dev"

Write-Host "Environment variables set:" -ForegroundColor Yellow
Write-Host "NEXT_TELEMETRY_DISABLED = $env:NEXT_TELEMETRY_DISABLED" -ForegroundColor Cyan
Write-Host "CB_DATA_ROOT = $env:CB_DATA_ROOT" -ForegroundColor Cyan

# Navighează la directorul app
Set-Location "C:\Users\andre\Desktop\coolbits\sites\app"
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow

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
    Write-Host "Used npm ci (package-lock.json found)" -ForegroundColor Green
} else { 
    npm install 
    Write-Host "Used npm install (no package-lock.json)" -ForegroundColor Green
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

# Start server
Write-Host "Starting Next.js server..." -ForegroundColor Yellow
Write-Host "Server will start in background. Test with:" -ForegroundColor Cyan
Write-Host "curl http://localhost:3000/api/walls/user | Select-Object -First 1" -ForegroundColor Cyan
Write-Host "curl http://localhost:3000/user/wall | Select-Object -First 1" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "Press Ctrl+C to stop server" -ForegroundColor Yellow
Write-Host "" -ForegroundColor White

# Start server (blocking)
npm start
