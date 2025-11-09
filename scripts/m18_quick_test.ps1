# M18.2 Quick Test - Non-interactive, cap-coadă
param()

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host "== M18.2 Quick Test ==" -ForegroundColor Green

# Set environment
$env:NEXT_TELEMETRY_DISABLED = "1"
$env:CB_DATA_ROOT = "C:\Users\andre\Desktop\coolbits\artifacts\dev"

# Check if we're in the right directory
if (-not (Test-Path "sites\app\package.json")) {
    Write-Host "ERROR: Not in project root. Please run from coolbits root directory" -ForegroundColor Red
    exit 1
}

Write-Host "Checking Node version..." -ForegroundColor Cyan
node -v

Write-Host "Navigating to Next.js app..." -ForegroundColor Cyan
Set-Location "sites\app"

Write-Host "Cleaning previous builds..." -ForegroundColor Cyan
if (Test-Path "node_modules") { Remove-Item "node_modules" -Recurse -Force }
if (Test-Path ".next") { Remove-Item ".next" -Recurse -Force }

Write-Host "Installing dependencies..." -ForegroundColor Cyan
npm ci

Write-Host "Building Next.js app..." -ForegroundColor Cyan
npm run build

Write-Host "== SUCCESS: M18.2 UI Build Complete! ==" -ForegroundColor Green
Write-Host "Next.js app is ready for deployment" -ForegroundColor Yellow

# Return to root
Set-Location "..\.."

Write-Host "M18.2 Test completed successfully!" -ForegroundColor Green
