# scripts/m18_standalone_local.ps1
param(
  [int]$Port = 3000,
  [string]$DataRoot = "C:\Users\andre\Desktop\coolbits\artifacts\dev"
)

$ErrorActionPreference = "Stop"
Write-Host "== M18.2 standalone local =="

# Env (anti-telemetrie + date root)
$env:NEXT_TELEMETRY_DISABLED = "1"
$env:CB_DATA_ROOT = $DataRoot

# Intră în app
Set-Location "C:\Users\andre\Desktop\coolbits\sites\app"

# Build curat
if (Test-Path .next)        { Remove-Item .next -Recurse -Force }
if (Test-Path node_modules) { Remove-Item node_modules -Recurse -Force }
if (Test-Path package-lock.json) { Remove-Item package-lock.json -Force }
npm ci
npm run build

# Asigură assets lângă server.js (în caz că postbuild nu a rulat)
New-Item -ItemType Directory -Force -Path ".next\standalone\public" | Out-Null
New-Item -ItemType Directory -Force -Path ".next\standalone\.next\static" | Out-Null
Copy-Item -Recurse -Force "public\*" ".next\standalone\public" -ErrorAction SilentlyContinue
Copy-Item -Recurse -Force ".next\static\*" ".next\standalone\.next\static" -ErrorAction SilentlyContinue

# Pornește serverul standalone
Set-Location ".next\standalone"
$env:PORT = "$Port"
$node = Start-Process -FilePath "node" -ArgumentList "server.js" -PassThru
Start-Sleep -Seconds 2

# Sanity checks
Invoke-WebRequest "http://localhost:$Port/" -UseBasicParsing | Out-Null
Invoke-WebRequest "http://localhost:$Port/api/walls/user" -UseBasicParsing | Out-Null
Write-Host "OK: standalone răspunde pe http://localhost:$Port"

# Lasă serverul pornit în foreground dacă vrei; altfel:
# Stop-Process -Id $node.Id
