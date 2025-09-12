# Fix pentru generarea server.js în Next.js standalone mode
# Rulează acest script în PowerShell normal (nu în Cursor)

param(
    [switch]$SkipInstall = $false
)

$ErrorActionPreference = "Stop"

Write-Host "== Fix Next.js Standalone server.js ==" -ForegroundColor Green

# Setează variabilele de mediu
$env:NEXT_TELEMETRY_DISABLED = "1"
$env:CB_DATA_ROOT = "C:\Users\andre\Desktop\coolbits\artifacts\dev"

Write-Host "Node version: $(node -v)" -ForegroundColor Yellow
Write-Host "NPM version: $(npm -v)" -ForegroundColor Yellow

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
if (Test-Path "package-lock.json") { 
    Remove-Item "package-lock.json" -Force 
    Write-Host "Removed package-lock.json" -ForegroundColor Green
}

# Instalează dependențele
if (-not $SkipInstall) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install --no-optional --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) {
        Write-Host "NPM install failed, trying with --legacy-peer-deps..." -ForegroundColor Red
        npm install --legacy-peer-deps --no-optional --no-audit --no-fund
    }
}

# Typecheck
Write-Host "Running typecheck..." -ForegroundColor Yellow
npm run typecheck

# Build
Write-Host "Building Next.js app..." -ForegroundColor Yellow
npm run build

# Verifică dacă server.js există
if (Test-Path ".next\standalone\server.js") {
    Write-Host "SUCCESS: server.js generated!" -ForegroundColor Green
    Write-Host "File size: $((Get-Item '.next\standalone\server.js').Length) bytes" -ForegroundColor Green
    
    # Copiază asset-urile
    Write-Host "Copying assets..." -ForegroundColor Yellow
    if (Test-Path "public") {
        New-Item -ItemType Directory -Path ".next\standalone\public" -Force | Out-Null
        Copy-Item -Recurse -Force "public\*" ".next\standalone\public\" -ErrorAction SilentlyContinue
        Write-Host "Copied public assets" -ForegroundColor Green
    }
    
    if (Test-Path ".next\static") {
        New-Item -ItemType Directory -Path ".next\standalone\.next\static" -Force | Out-Null
        Copy-Item -Recurse -Force ".next\static\*" ".next\standalone\.next\static\" -ErrorAction SilentlyContinue
        Write-Host "Copied static assets" -ForegroundColor Green
    }
    
    # Testează serverul
    Write-Host "Starting server for test..." -ForegroundColor Yellow
    $job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        $env:CB_DATA_ROOT = "C:\Users\andre\Desktop\coolbits\artifacts\dev"
        $env:NEXT_TELEMETRY_DISABLED = "1"
        Set-Location ".next\standalone"
        node server.js
    }
    
    Start-Sleep -Seconds 3
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "SUCCESS: Server responding! Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Server not responding: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -ErrorAction SilentlyContinue
    
    Write-Host "== Build completed successfully! ==" -ForegroundColor Green
    Write-Host "To start server manually:" -ForegroundColor Cyan
    Write-Host "  cd .next\standalone" -ForegroundColor Cyan
    Write-Host "  node server.js" -ForegroundColor Cyan
    
} else {
    Write-Host "ERROR: server.js not generated!" -ForegroundColor Red
    Write-Host "Checking .next directory structure..." -ForegroundColor Yellow
    
    if (Test-Path ".next") {
        Get-ChildItem ".next" -Recurse | Select-Object Name, FullName | Format-Table
    }
    
    Write-Host "Fallback: Removing standalone mode..." -ForegroundColor Yellow
    $config = Get-Content "next.config.ts" -Raw
    $config = $config -replace "output: 'standalone',", "// output: 'standalone',"
    $config | Set-Content "next.config.ts"
    
    Write-Host "Rebuilding without standalone..." -ForegroundColor Yellow
    npm run build
    
    Write-Host "Updated package.json start script..." -ForegroundColor Yellow
    $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
    $packageJson.scripts.start = "next start"
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content "package.json"
    
    Write-Host "== Fallback completed! ==" -ForegroundColor Green
    Write-Host "To start server:" -ForegroundColor Cyan
    Write-Host "  npm start" -ForegroundColor Cyan
}
