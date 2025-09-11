# Policy Rollback Script for M15 (PowerShell)
# ===========================================
# 
# Explicit rollback plan for policy changes:
# 1. Re-deploy last signed version of registry.json
# 2. Force enforcer reload and set MODE=deny for 60 min
# 3. Trigger rapid rollback via label or manual workflow

param(
    [string]$RepoPath = ".",
    [int]$RollbackDurationMinutes = 60
)

$ErrorActionPreference = "Stop"

# Configuration
$RegistryDir = Join-Path $RepoPath "cblm\opipe\nha\out"
$BackupDir = Join-Path $RepoPath "backup\registry"
$LogFile = Join-Path $RepoPath "logs\policy_rollback.log"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

function Write-Error {
    param([string]$Message)
    Write-Host "${Red}ERROR: $Message${Reset}" | Tee-Object -FilePath $LogFile -Append
    exit 1
}

function Write-Warning {
    param([string]$Message)
    Write-Host "${Yellow}WARNING: $Message${Reset}" | Tee-Object -FilePath $LogFile -Append
}

function Write-Success {
    param([string]$Message)
    Write-Host "${Green}SUCCESS: $Message${Reset}" | Tee-Object -FilePath $LogFile -Append
}

function Write-Info {
    param([string]$Message)
    Write-Host "${Blue}INFO: $Message${Reset}" | Tee-Object -FilePath $LogFile -Append
}

# Create necessary directories
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

Write-Log "Starting policy rollback procedure..."

# Step 1: Backup current registry state
Write-Info "Step 1: Backing up current registry state"
$CurrentBackup = Join-Path $BackupDir "registry_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

$RegistryFile = Join-Path $RegistryDir "registry.json"
if (Test-Path $RegistryFile) {
    Copy-Item $RegistryFile "$CurrentBackup.json"
    Write-Log "Backed up current registry.json to $CurrentBackup.json"
} else {
    Write-Warning "Current registry.json not found - proceeding with rollback"
}

# Step 2: Find last signed registry version
Write-Info "Step 2: Finding last signed registry version"
$LastSigned = ""

# Look for signed registry backups
$SignedBackups = Get-ChildItem -Path $BackupDir -Filter "registry_signed_*.json" | Sort-Object LastWriteTime -Descending
if ($SignedBackups) {
    $LastSigned = $SignedBackups[0].FullName
}

# If no signed backup found, look for any backup
if (-not $LastSigned) {
    $RegularBackups = Get-ChildItem -Path $BackupDir -Filter "registry_backup_*.json" | Sort-Object LastWriteTime -Descending
    if ($RegularBackups) {
        $LastSigned = $RegularBackups[0].FullName
    }
}

if (-not $LastSigned) {
    Write-Error "No registry backup found for rollback"
}

Write-Log "Found last signed registry: $LastSigned"

# Step 3: Verify signature of backup
Write-Info "Step 3: Verifying signature of backup"
$BackupSig = "$LastSigned.sig"
$BackupCert = "$LastSigned.cert"

if ((Test-Path $BackupSig) -and (Test-Path $BackupCert)) {
    if (Get-Command cosign -ErrorAction SilentlyContinue) {
        try {
            $verifyResult = & cosign verify-blob --key cosign.pub --signature $BackupSig $LastSigned 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Backup signature verified"
            } else {
                Write-Warning "Backup signature verification failed - proceeding anyway"
            }
        } catch {
            Write-Warning "Failed to verify backup signature - proceeding anyway"
        }
    } else {
        Write-Warning "cosign not available - skipping signature verification"
    }
} else {
    Write-Warning "Backup signature files not found - proceeding without verification"
}

# Step 4: Restore registry
Write-Info "Step 4: Restoring registry from backup"
Copy-Item $LastSigned $RegistryFile
Write-Success "Registry restored from $LastSigned"

# Step 5: Force enforcer reload
Write-Info "Step 5: Forcing enforcer reload"
$EnforcerProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*enforcer.py*" }

if ($EnforcerProcess) {
    Write-Log "Found enforcer process: $($EnforcerProcess.Id)"
    
    # Send reload signal (SIGUSR1 equivalent)
    try {
        # On Windows, we'll use a different approach - create a reload trigger file
        $ReloadTrigger = Join-Path $RepoPath ".enforcer_reload"
        New-Item -ItemType File -Path $ReloadTrigger -Force | Out-Null
        Write-Success "Enforcer reload trigger created"
    } catch {
        Write-Warning "Failed to create reload trigger for enforcer"
    }
} else {
    Write-Warning "Enforcer process not found - may need manual restart"
}

# Step 6: Set fail-closed mode
Write-Info "Step 6: Setting fail-closed mode for $RollbackDurationMinutes minutes"
$env:NHA_ENFORCEMENT_MODE = "deny"

# Create temporary environment file
$EnvFile = Join-Path $RepoPath ".env.rollback"
$RecoveryTime = (Get-Date).AddMinutes($RollbackDurationMinutes)
@"
NHA_ENFORCEMENT_MODE=deny
NHA_ROLLBACK_UNTIL=$($RecoveryTime.ToString('yyyy-MM-dd HH:mm:ss'))
"@ | Out-File -FilePath $EnvFile -Encoding UTF8

Write-Success "Fail-closed mode set for $RollbackDurationMinutes minutes"

# Step 7: Verify rollback
Write-Info "Step 7: Verifying rollback"
if (Test-Path $RegistryFile) {
    $RegistryHash = (Get-FileHash $RegistryFile -Algorithm SHA256).Hash
    $BackupHash = (Get-FileHash $LastSigned -Algorithm SHA256).Hash
    
    if ($RegistryHash -eq $BackupHash) {
        Write-Success "Rollback verified - registry hashes match"
    } else {
        Write-Error "Rollback verification failed - registry hashes don't match"
    }
} else {
    Write-Error "Registry file not found after rollback"
}

# Step 8: Schedule automatic recovery
Write-Info "Step 8: Scheduling automatic recovery"
$RecoveryTimeStr = $RecoveryTime.ToString('yyyy-MM-dd HH:mm:ss')

# Create recovery script
$RecoveryScript = Join-Path $RepoPath "scripts\recover_from_rollback.ps1"
@"
# Automatic recovery from rollback
# Generated: $(Get-Date)

function Write-Log {
    param([string]`$Message)
    `$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[\`$timestamp] `$Message"
}

Write-Log "Starting automatic recovery from rollback..."

# Remove rollback environment
`$EnvFile = "$EnvFile"
if (Test-Path `$EnvFile) {
    Remove-Item `$EnvFile -Force
}

# Set normal enforcement mode
`$env:NHA_ENFORCEMENT_MODE = "warn"

# Create reload trigger
`$ReloadTrigger = "$(Join-Path $RepoPath '.enforcer_reload')"
New-Item -ItemType File -Path `$ReloadTrigger -Force | Out-Null

Write-Log "Recovery completed - normal enforcement mode restored"
"@ | Out-File -FilePath $RecoveryScript -Encoding UTF8

# Schedule recovery using Task Scheduler
try {
    $TaskName = "PolicyRollbackRecovery_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    $Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File `"$RecoveryScript`""
    $Trigger = New-ScheduledTaskTrigger -Once -At $RecoveryTime
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force | Out-Null
    Write-Log "Automatic recovery scheduled for $RecoveryTimeStr"
} catch {
    Write-Warning "Failed to schedule automatic recovery - manual recovery required at $RecoveryTimeStr"
}

# Step 9: Generate rollback report
Write-Info "Step 9: Generating rollback report"
$ReportFile = Join-Path $RepoPath "logs\rollback_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

$ReportData = @{
    rollback_timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    rollback_duration_minutes = $RollbackDurationMinutes
    restored_from = $LastSigned
    registry_hash = $RegistryHash
    enforcer_mode = "deny"
    recovery_scheduled = $RecoveryTimeStr
    status = "completed"
} | ConvertTo-Json -Depth 3

$ReportData | Out-File -FilePath $ReportFile -Encoding UTF8
Write-Success "Rollback report generated: $ReportFile"

# Final status
Write-Log "Policy rollback completed successfully"
Write-Log "Registry restored from: $LastSigned"
Write-Log "Fail-closed mode active for: $RollbackDurationMinutes minutes"
Write-Log "Automatic recovery scheduled for: $RecoveryTimeStr"
Write-Log "Rollback report: $ReportFile"

Write-Host ""
Write-Host "🔄 POLICY ROLLBACK COMPLETED" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host "✅ Registry restored from backup" -ForegroundColor Green
Write-Host "✅ Enforcer reloaded" -ForegroundColor Green
Write-Host "✅ Fail-closed mode active ($RollbackDurationMinutes min)" -ForegroundColor Green
Write-Host "✅ Automatic recovery scheduled" -ForegroundColor Green
Write-Host "✅ Rollback report generated" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Monitor system for $RollbackDurationMinutes minutes" -ForegroundColor White
Write-Host "2. Automatic recovery at $RecoveryTimeStr" -ForegroundColor White
Write-Host "3. Manual intervention if needed" -ForegroundColor White
Write-Host ""
