# M18.2 UI Sanity Check - PowerShell 7 External Only
param()
$ErrorActionPreference = "Stop"

# Hard guard: refuză să ruleze din Cursor/VS Code
$ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
if ($parent -match 'cursor|code|code-insiders') {
    Write-Error "Nu rula din Cursor/VS Code. Deschide PowerShell 7 (pwsh) și rulează scriptul acolo."
    exit 1
}

Write-Host "== M18.2 UI Sanity Check ==" -ForegroundColor Green

# Set environment
if ($env:NEXT_TELEMETRY_DISABLED -ne "1") {
    Write-Host "Set NEXT_TELEMETRY_DISABLED=1"
    $env:NEXT_TELEMETRY_DISABLED = "1"
}

$env:CB_DATA_ROOT = "C:\Users\andre\Desktop\coolbits\artifacts\dev"
$env:npm_config_engine_strict = "false"

# Check versions
Write-Host "Node version: $(node -v)"
Write-Host "NPM version: $(npm -v)"
Write-Host "PowerShell version: $($PSVersionTable.PSVersion)"

# Clean and rebuild
cd "C:\Users\andre\Desktop\coolbits\sites\app"

if (Test-Path node_modules) {
    Write-Host "Removing node_modules..."
    Remove-Item node_modules -Recurse -Force
}

if (Test-Path .next) {
    Write-Host "Removing .next..."
    Remove-Item .next -Recurse -Force
}

if (Test-Path package-lock.json) {
    Write-Host "Using npm ci..."
    npm ci
} else {
    Write-Host "Using npm install..."
    npm install
}

Write-Host "Running typecheck..."
npm run typecheck

Write-Host "Running build..."
npm run build

Write-Host "== OK: build complet. Pornesc start local ==" -ForegroundColor Green

# Start server in background
$proc = Start-Process -FilePath "npm" -ArgumentList "start" -PassThru -WindowStyle Hidden

# Wait and test
Start-Sleep 6

$RunId = "RUN_" + (Get-Date -Format yyyyMMdd_HHmmss_fff)
$LogDir = "C:\Users\andre\Desktop\coolbits\artifacts\dev\logs"
New-Item -Force -ItemType Directory $LogDir | Out-Null
$Proof = Join-Path $LogDir "$RunId.proof.txt"

$code = 000
try { 
    $r = Invoke-WebRequest "http://localhost:3000/api/walls/user" -UseBasicParsing -TimeoutSec 3
    $code = $r.StatusCode
    Write-Host "SUCCESS: Status $code" -ForegroundColor Green
} catch { 
    $code = "ERR"
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Create proof file
$payload = [string]::Join("`n", @(
    "run_id=$RunId",
    "ts=$(Get-Date -Format o)",
    "pwsh=$($PSVersionTable.PSVersion)",
    "node=$(node -v 2>$null)",
    "cwd=$((Get-Location).Path)",
    "status=$code"
))
$payload | Set-Content -Encoding UTF8 $Proof
$hash = (Get-FileHash $Proof -Algorithm SHA256).Hash
("sha256=" + $hash) | Add-Content -Encoding UTF8 $Proof

Write-Host "PROOF: $Proof" -ForegroundColor Yellow
Write-Host "SHA256: $hash" -ForegroundColor Yellow
Write-Host "STATUS: $code" -ForegroundColor $(if($code -eq 200){"Green"}else{"Red"})

if ($code -eq 200) {
    Write-Host "== SUCCESS: Next.js running on localhost:3000 ==" -ForegroundColor Green
    Write-Host "Server PID: $($proc.Id)"
    Write-Host "Test: curl http://localhost:3000/api/walls/user"
} else {
    Write-Host "== FAILED: Check logs above ==" -ForegroundColor Red
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}