# scripts/m18_cloud_deploy.ps1
param(
  [string]$Project = "coolbits-ai",
  [string]$Region = "europe-west1",
  [string]$Service = "coolbits-app",
  [string]$TagPrefix = "m18-ui",
  [string]$DataRoot = "/app/artifacts/dev",
  [int]$Instances = 2
)
$ErrorActionPreference = "Stop"
$stamp = (Get-Date).ToString("yyyyMMdd-HHmm")
$Image = "gcr.io/$Project/$Service:$TagPrefix-$stamp"

Write-Host "== Build =="
gcloud builds submit --tag $Image

Write-Host "== Deploy =="
gcloud run deploy $Service `
  --image $Image `
  --region $Region --platform managed --allow-unauthenticated `
  --set-env-vars CB_DATA_ROOT=$DataRoot,NEXT_TELEMETRY_DISABLED=1 `
  --max-instances $Instances --memory 1Gi --cpu 1

Write-Host "== Verify =="
$url = (gcloud run services describe $Service --region $Region --format "value(status.url)")
Write-Host "URL: $url"
Invoke-WebRequest "$url/api/walls/user" -UseBasicParsing | Out-Null
Write-Host "OK: $url/api/walls/user răspunde"
