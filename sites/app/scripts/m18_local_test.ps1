# UI Local Test Script cu proxy extern
. "$PSScriptRoot\..\..\..\scripts\_pwsh_proxy.ps1"

Write-Host "=== UI Local Test (M18) ===" -ForegroundColor Cyan

# 1) Kill any existing Next processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
$tcp = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($tcp) { Stop-Process -Id $tcp.OwningProcess -Force -ErrorAction SilentlyContinue }

# 2) Build Next
Write-Host "Building Next.js..." -ForegroundColor Yellow
Set-Location "C:\Users\andre\Desktop\coolbits\sites\app"
if (Test-Path .next) { Remove-Item .next -Recurse -Force }
if (Test-Path package-lock.json) { npm ci } else { npm install }
npm run build

# 3) Start Next in background
Write-Host "Starting Next.js..." -ForegroundColor Yellow
$startCmd = "cd `"C:\Users\andre\Desktop\coolbits\sites\app`"; `$env:NEXT_TELEMETRY_DISABLED=`"1`"; `$env:CB_DATA_ROOT=`"C:\Users\andre\Desktop\coolbits\artifacts\dev`"; npm start"
Start-Process -FilePath "$env:ProgramFiles\PowerShell\7\pwsh.exe" `
  -ArgumentList "-NoLogo -NoProfile -Command $startCmd" -WindowStyle Minimized | Out-Null

# 4) Wait and test
Write-Host "Testing endpoints..." -ForegroundColor Yellow
Start-Sleep 5

$ok = $false
1..10 | ForEach-Object {
  Start-Sleep 2
  try {
    $r = Invoke-WebRequest "http://localhost:3000/api/walls/user" -UseBasicParsing -TimeoutSec 3
    if ($r.StatusCode -eq 200) { $ok = $true; break }
  } catch {}
}

if ($ok) {
  Write-Host "SUCCESS: Next.js is running on http://localhost:3000" -ForegroundColor Green
  Write-Host "Gateway endpoints:" -ForegroundColor Cyan
  Write-Host "  - http://localhost:3000/api/gw/balance" -ForegroundColor White
  Write-Host "  - http://localhost:3000/api/gw/nha/invoke" -ForegroundColor White
  Write-Host "  - http://localhost:3000/api/gw/rag/query" -ForegroundColor White
} else {
  Write-Host "ERROR: Next.js failed to start or respond" -ForegroundColor Red
  exit 1
}

Write-Host "=== UI Local Test Complete ===" -ForegroundColor Green