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
  [string]$Tag = "m19-hello",
  [switch]$Clean
)

$ErrorActionPreference = "Stop"
Write-Host "== M19 Gateway Build =="

Set-Location $GatewayDir

if ($Clean) {
  if (Test-Path "__pycache__") { Remove-Item __pycache__ -Recurse -Force }
  if (Test-Path "*.pyc") { Remove-Item *.pyc -Force }
}

# Build Docker image
$Image = "gcr.io/$Project/cb-gw:$Tag"
Write-Host "Building Docker image: $Image"

docker build -t $Image .

if ($LASTEXITCODE -ne 0) {
  Write-Error "Docker build failed!"
  exit 1
}

Write-Host "Docker image built successfully: $Image"

# Test local (optional)
if ($Clean) {
  Write-Host "Testing local container..."
  docker run --rm -p 8000:8000 -e CB_BILLING_MODE=dev $Image &
  Start-Sleep -Seconds 5
  
  try {
    $response = Invoke-WebRequest "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Local test OK: $($response.StatusCode)"
  } catch {
    Write-Host "Local test failed: $($_.Exception.Message)"
  }
  
  docker stop $(docker ps -q --filter ancestor=$Image) -ErrorAction SilentlyContinue
}

Write-Host "== Build completed =="
