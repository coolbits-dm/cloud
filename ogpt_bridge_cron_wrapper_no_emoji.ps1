# oGPT-Bridge Cron Wrapper Script (PowerShell) - No Emoji
# COOL BITS SRL - Internal Secret
# CEO: Andrei
# AI Assistant: oCursor

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "help")]
    [string]$Action
)

# Configuration
$BridgeScript = "ogpt_bridge_complete_system.py"
$ProjectDir = "C:\Users\andre\Desktop\coolbits"
$LogDir = "$ProjectDir\ogpt_bridge_logs"
$PidFile = "$ProjectDir\ogpt_bridge.pid"

# Create log directory
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Log function
function Write-LogMessage($Message) {
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Write-Host $LogEntry
    Add-Content -Path "$LogDir\bridge_cron.log" -Value $LogEntry
}

# Check if running
function Test-BridgeRunning {
    if (Test-Path $PidFile) {
        $Pid = Get-Content $PidFile
        $Process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
        if ($Process) {
            return $true
        } else {
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
            return $false
        }
    }
    return $false
}

# Start bridge
function Start-Bridge {
    Write-LogMessage "Starting oGPT-Bridge System..."
    Set-Location $ProjectDir
    $Process = Start-Process -FilePath "python" -ArgumentList $BridgeScript -PassThru -WindowStyle Hidden
    $Process.Id | Out-File -FilePath $PidFile -Encoding ASCII
    Write-LogMessage "oGPT-Bridge started with PID: $($Process.Id)"
}

# Stop bridge
function Stop-Bridge {
    Write-LogMessage "Stopping oGPT-Bridge System..."
    if (Test-Path $PidFile) {
        $Pid = Get-Content $PidFile
        $Process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
        if ($Process) {
            Stop-Process -Id $Pid -Force
            Write-LogMessage "oGPT-Bridge stopped (PID: $Pid)"
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
}

# Restart bridge
function Restart-Bridge {
    Write-LogMessage "Restarting oGPT-Bridge System..."
    Stop-Bridge
    Start-Sleep -Seconds 2
    Start-Bridge
}

# Show status
function Show-Status {
    Write-LogMessage "oGPT-Bridge Status Check..."
    if (Test-BridgeRunning) {
        $Pid = Get-Content $PidFile
        Write-LogMessage "oGPT-Bridge is RUNNING (PID: $Pid)"
    } else {
        Write-LogMessage "oGPT-Bridge is NOT RUNNING"
    }
}

# Main logic
switch ($Action) {
    "start" {
        if (Test-BridgeRunning) {
            Write-LogMessage "oGPT-Bridge is already running"
        } else {
            Start-Bridge
        }
    }
    "stop" {
        Stop-Bridge
    }
    "restart" {
        Restart-Bridge
    }
    "status" {
        Show-Status
    }
    "help" {
        Write-Host "oGPT-Bridge Cron Wrapper Script (PowerShell)"
        Write-Host "COOL BITS SRL - CEO: Andrei"
        Write-Host "AI Assistant: oCursor"
        Write-Host "Classification: Internal Secret - CoolBits.ai Members Only"
        Write-Host ""
        Write-Host "Usage: .\ogpt_bridge_cron_wrapper_no_emoji.ps1 {start|stop|restart|status|help}"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  start   - Start oGPT-Bridge system"
        Write-Host "  stop    - Stop oGPT-Bridge system"
        Write-Host "  restart - Restart oGPT-Bridge system"
        Write-Host "  status  - Show bridge status and logs"
        Write-Host "  help    - Show this help message"
    }
}

Write-LogMessage "Script completed: $Action"
