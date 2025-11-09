# Automatic recovery from rollback
# Generated: 09/11/2025 10:49:30

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[\$timestamp] $Message"
}

Write-Log "Starting automatic recovery from rollback..."

# Remove rollback environment
$EnvFile = ".\.env.rollback"
if (Test-Path $EnvFile) {
    Remove-Item $EnvFile -Force
}

# Set normal enforcement mode
$env:NHA_ENFORCEMENT_MODE = "warn"

# Create reload trigger
$ReloadTrigger = ".\.enforcer_reload"
New-Item -ItemType File -Path $ReloadTrigger -Force | Out-Null

Write-Log "Recovery completed - normal enforcement mode restored"
