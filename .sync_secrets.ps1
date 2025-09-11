# .sync_secrets.ps1
#
# Securely synchronizes secrets from a local JSON file to Google Cloud Secret Manager.
#
# Prerequisites:
# 1. Google Cloud SDK installed and authenticated (`gcloud auth login`).
# 2. Project set in gcloud config (`gcloud config set project coolbits-ai`).

# --- Configuration ---
$ProjectID = "coolbits-ai"
$SecretsFile = "local_secrets.json"

# --- Script ---
Write-Host "🔧 Starting secret synchronization for project '$ProjectID'..." -ForegroundColor Cyan

if (-not (Test-Path $SecretsFile)) {
    Write-Error "Error: Secrets file not found at '$SecretsFile'. Please create it first."
    exit 1
}

# Use PowerShell's native JSON parsing
$secrets = Get-Content $SecretsFile | ConvertFrom-Json

foreach ($secret in $secrets) {
    $secretName = $secret.name
    $secretValue = $secret.value

    Write-Host "Processing secret: '$secretName'..."

    # Check if secret exists
    $existingSecret = gcloud secrets describe $secretName --project $ProjectID --format="value(name)" --quiet 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  -> Secret '$secretName' does not exist. Creating it..." -ForegroundColor Yellow
        gcloud secrets create $secretName --project $ProjectID --replication-policy="automatic" --labels="source=local-sync,managed-by=ogeminicli" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "  -> Failed to create secret '$secretName'."
            continue
        }
        Write-Host "  -> Secret '$secretName' created successfully." -ForegroundColor Green
    } else {
        Write-Host "  -> Secret '$secretName' already exists. Adding a new version."
    }

    # Add a new version with the secret value from a temporary file for security
    $TempFile = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $TempFile -Value $secretValue -NoNewline
    
    gcloud secrets versions add $secretName --project $ProjectID --data-file=$TempFile | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  -> ✅ Successfully added new version for secret '$secretName'." -ForegroundColor Green
    } else {
        Write-Error "  -> ❌ Failed to add new version for secret '$secretName'."
    }
    
    Remove-Item $TempFile -Force
}

Write-Host "🎉 Secret synchronization complete." -ForegroundColor Magenta
Write-Warning "SECURITY REMINDER: Please delete the '$SecretsFile' file now that the secrets are in Google Cloud."
