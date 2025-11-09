# --- Hard guard ---
$ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
if ($parent -match 'cursor|code|code-insiders') {
  Write-Error "Nu rula din Cursor/VS Code. Deschide PowerShell 7 (pwsh)."
  exit 1
}
# ------------------

param(
  [string]$AppDir = "C:\Users\andre\Desktop\coolbits\sites\app",
  [string]$Project = "coolbits-ai",
  [string]$Region = "europe-west1",
  [string]$Service = "coolbits-app",
  [string]$TagPrefix = "m18-ui",
  [string]$DataRoot = "/app/artifacts/dev",
  [int]$Instances = 2
)

$ErrorActionPreference = "Stop"
Set-Location $AppDir
$stamp = (Get-Date).ToString("yyyyMMdd-HHmm")
$Image = "gcr.io/$Project/$Service:$TagPrefix-$stamp"

Write-Host "== Cloud Build: $Image =="
gcloud builds submit --tag $Image

Write-Host "== Cloud Run deploy =="
gcloud run deploy $Service `
  --image $Image `
  --region $Region --platform managed --allow-unauthenticated `
  --set-env-vars CB_DATA_ROOT=$DataRoot,NEXT_TELEMETRY_DISABLED=1 `
  --max-instances $Instances --memory 1Gi --cpu 1

$url = (gcloud run services describe $Service --region $Region --format "value(status.url)")
Write-Host "URL: $url"

# Health probe
Invoke-WebRequest "$url/api/walls/user" -UseBasicParsing -TimeoutSec 5 | Out-Null
Write-Host "OK: $url/api/walls/user răspunde"
