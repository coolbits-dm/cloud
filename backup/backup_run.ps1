# CoolBits.ai Backup Script (Windows PowerShell)
# =============================================

param(
    [string]$BackupBucket = "coolbits-backup-prod",
    [string]$ProjectId = "coolbits-og-bridge",
    [string]$Region = "europe-west1"
)

# Set error handling
$ErrorActionPreference = "Stop"

# Set non-interactive environment
$env:CI = "1"
$env:NO_COLOR = "1"
$env:GCLOUD_SUPPRESS_PROMPTS = "1"
$env:CLOUDSDK_CORE_DISABLE_PROMPTS = "1"

Write-Host "🔄 CoolBits.ai Backup Process Starting..."
Write-Host "========================================"
Write-Host "Bucket: $BackupBucket"
Write-Host "Project: $ProjectId"
Write-Host "Region: $Region"
Write-Host ""

# Create backup directory
$BackupDir = "backup_temp_$(Get-Date -Format 'yyyyMMddTHHmmssZ')"
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

try {
    # 1. Backup configuration files
    Write-Host "📁 Backing up configuration files..."
    $ConfigItems = @(
        "config/",
        "data/governance/",
        "feature-flags.json",
        ".runtime.json",
        "package.json",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml"
    )
    
    foreach ($item in $ConfigItems) {
        if (Test-Path $item) {
            Copy-Item -Path $item -Destination "$BackupDir/" -Recurse -Force
            Write-Host "  ✅ $item"
        } else {
            Write-Host "  ⚠️  $item (not found)"
        }
    }
    
    # 2. Backup SBOM and security artifacts
    Write-Host "`n🔐 Backing up security artifacts..."
    $SecurityItems = @(
        "sbom/",
        "cosign.key",
        "cosign.pub",
        "slsa-provenance.json"
    )
    
    foreach ($item in $SecurityItems) {
        if (Test-Path $item) {
            Copy-Item -Path $item -Destination "$BackupDir/" -Recurse -Force
            Write-Host "  ✅ $item"
        } else {
            Write-Host "  ⚠️  $item (not found)"
        }
    }
    
    # 3. Backup data files
    Write-Host "`n📊 Backing up data files..."
    $DataItems = @(
        "data/roadmap.json",
        "logs/boot-health.log",
        ".server.lock"
    )
    
    foreach ($item in $DataItems) {
        if (Test-Path $item) {
            Copy-Item -Path $item -Destination "$BackupDir/" -Recurse -Force
            Write-Host "  ✅ $item"
        } else {
            Write-Host "  ⚠️  $item (not found)"
        }
    }
    
    # 4. Create backup metadata
    Write-Host "`n📝 Creating backup metadata..."
    $BackupMetadata = @{
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
        version = "1.0.0"
        project_id = $ProjectId
        region = $Region
        backup_scope = "full"
        data_classification = "confidential"
        retention_days = 365
        restore_priority = "P0"
        files_count = (Get-ChildItem -Path $BackupDir -Recurse -File).Count
        total_size_bytes = (Get-ChildItem -Path $BackupDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
    }
    
    $BackupMetadata | ConvertTo-Json -Depth 3 | Out-File -FilePath "$BackupDir/backup_metadata.json" -Encoding UTF8
    Write-Host "  ✅ backup_metadata.json created"
    
    # 5. Create compressed backup
    Write-Host "`n🗜️  Creating compressed backup..."
    $Timestamp = (Get-Date).ToString("yyyyMMddTHHmmssZ")
    $BackupFile = "coolbits-backup-$Timestamp.zip"
    
    Compress-Archive -Path "$BackupDir/*" -DestinationPath $BackupFile -Force
    Write-Host "  ✅ $BackupFile created"
    
    # 6. Calculate checksum
    Write-Host "`n🔍 Calculating checksum..."
    $Checksum = Get-FileHash -Path $BackupFile -Algorithm SHA256
    $Checksum.Hash | Out-File -FilePath "$BackupFile.sha256" -Encoding UTF8
    Write-Host "  ✅ SHA256: $($Checksum.Hash)"
    
    # 7. Upload to GCS
    Write-Host "`n☁️  Uploading to Google Cloud Storage..."
    
    # Set project
    gcloud config set project $ProjectId --quiet
    
    # Upload backup file
    gsutil cp $BackupFile "gs://$BackupBucket/$BackupFile"
    Write-Host "  ✅ $BackupFile uploaded"
    
    # Upload checksum
    gsutil cp "$BackupFile.sha256" "gs://$BackupBucket/$BackupFile.sha256"
    Write-Host "  ✅ $BackupFile.sha256 uploaded"
    
    # 8. Verify upload
    Write-Host "`n🔍 Verifying upload..."
    $RemoteChecksum = gsutil cat "gs://$BackupBucket/$BackupFile.sha256"
    if ($RemoteChecksum -eq $Checksum.Hash) {
        Write-Host "  ✅ Checksum verification passed"
    } else {
        Write-Host "  ❌ Checksum verification failed"
        throw "Checksum mismatch"
    }
    
    # 9. Cleanup local files
    Write-Host "`n🧹 Cleaning up local files..."
    Remove-Item -Path $BackupDir -Recurse -Force
    Remove-Item -Path $BackupFile -Force
    Remove-Item -Path "$BackupFile.sha256" -Force
    Write-Host "  ✅ Local files cleaned up"
    
    # 10. Log success
    Write-Host "`n✅ Backup completed successfully!"
    Write-Host "📁 Backup file: gs://$BackupBucket/$BackupFile"
    Write-Host "🔐 Checksum: $($Checksum.Hash)"
    Write-Host "📊 Size: $([math]::Round((Get-Item $BackupFile).Length / 1MB, 2)) MB"
    
    # Return backup file name for monitoring
    return $BackupFile
    
} catch {
    Write-Host "`n❌ Backup failed: $($_.Exception.Message)"
    
    # Cleanup on failure
    if (Test-Path $BackupDir) {
        Remove-Item -Path $BackupDir -Recurse -Force
    }
    if (Test-Path $BackupFile) {
        Remove-Item -Path $BackupFile -Force
    }
    if (Test-Path "$BackupFile.sha256") {
        Remove-Item -Path "$BackupFile.sha256" -Force
    }
    
    exit 1
}
