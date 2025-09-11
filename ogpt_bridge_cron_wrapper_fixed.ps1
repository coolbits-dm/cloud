# oGPT-Bridge Cron Wrapper Script (PowerShell) - Fixed
# COOL BITS SRL 🏢 - Internal Secret
# CEO: Andrei
# AI Assistant: oCursor

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "help")]
    [string]$Action
)

# Script configuration
$BridgeScript = "ogpt_bridge_complete_system.py"
$ProjectDir = "C:\Users\andre\Desktop\coolbits"
$LogDir = "$ProjectDir\ogpt_bridge_logs"
$PidFile = "$ProjectDir\ogpt_bridge.pid"

# Create log directory
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Function to log with timestamp
function Write-LogMessage {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Write-Host $LogEntry
    Add-Content -Path "$LogDir\bridge_cron.log" -Value $LogEntry
}

# Function to check if bridge is running
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

# Function to start bridge
function Start-Bridge {
    Write-LogMessage "🌉 Starting oGPT-Bridge System..."
    
    Set-Location $ProjectDir
    
    # Start bridge system in background
    $Process = Start-Process -FilePath "python" -ArgumentList $BridgeScript -PassThru -WindowStyle Hidden
    
    # Save PID
    $Process.Id | Out-File -FilePath $PidFile -Encoding ASCII
    
    Write-LogMessage "✅ oGPT-Bridge started with PID: $($Process.Id)"
    Write-LogMessage "📁 Logs: $LogDir\bridge_output.log"
    Write-LogMessage "📄 PID file: $PidFile"
}

# Function to stop bridge
function Stop-Bridge {
    Write-LogMessage "🛑 Stopping oGPT-Bridge System..."
    
    if (Test-Path $PidFile) {
        $Pid = Get-Content $PidFile
        $Process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
        if ($Process) {
            Stop-Process -Id $Pid -Force
            Write-LogMessage "✅ oGPT-Bridge stopped (PID: $Pid)"
        } else {
            Write-LogMessage "⚠️ Bridge process not found"
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    } else {
        Write-LogMessage "⚠️ PID file not found"
    }
}

# Function to restart bridge
function Restart-Bridge {
    Write-LogMessage "🔄 Restarting oGPT-Bridge System..."
    Stop-Bridge
    Start-Sleep -Seconds 2
    Start-Bridge
}

# Function to show status
function Show-Status {
    Write-LogMessage "📊 oGPT-Bridge Status Check..."
    
    if (Test-BridgeRunning) {
        $Pid = Get-Content $PidFile
        Write-LogMessage "✅ oGPT-Bridge is RUNNING (PID: $Pid)"
    } else {
        Write-LogMessage "❌ oGPT-Bridge is NOT RUNNING"
    }
    
    # Show log files
    Write-LogMessage "📁 Log files:"
    Get-ChildItem $LogDir -ErrorAction SilentlyContinue | ForEach-Object {
        Write-LogMessage "   $($_.Name) - $($_.Length) bytes - $($_.LastWriteTime)"
    }
}

# Function to show help
function Show-Help {
    Write-Host "🌉 oGPT-Bridge Cron Wrapper Script (PowerShell)"
    Write-Host "🏢 COOL BITS SRL 🏢 - CEO: Andrei"
    Write-Host "🤖 AI Assistant: oCursor"
    Write-Host "🔒 Classification: Internal Secret - CoolBits.ai 🏢 Members Only"
    Write-Host ""
    Write-Host "Usage: .\ogpt_bridge_cron_wrapper_fixed.ps1 {start|stop|restart|status|help}"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  start   - Start oGPT-Bridge system"
    Write-Host "  stop    - Stop oGPT-Bridge system"
    Write-Host "  restart - Restart oGPT-Bridge system"
    Write-Host "  status  - Show bridge status and logs"
    Write-Host "  help    - Show this help message"
    Write-Host ""
    Write-Host "Windows Task Scheduler example:"
    Write-Host "  Action: Start a program"
    Write-Host "  Program: powershell.exe"
    Write-Host "  Arguments: -ExecutionPolicy Bypass -File `"$ProjectDir\ogpt_bridge_cron_wrapper_fixed.ps1`" status"
    Write-Host "  Trigger: Every 30 seconds"
    Write-Host ""
    Write-Host "Files:"
    Write-Host "  Bridge Script: $ProjectDir\$BridgeScript"
    Write-Host "  Log Directory: $LogDir"
    Write-Host "  PID File: $PidFile"
}

# Main script logic
switch ($Action) {
    "start" {
        if (Test-BridgeRunning) {
            Write-LogMessage "⚠️ oGPT-Bridge is already running"
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
        Show-Help
    }
}

Write-LogMessage "Script completed: $Action"
