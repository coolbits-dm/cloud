# oGPT-Bridge Cron Wrapper Script (PowerShell)
# COOL BITS SRL 🏢 - Internal Secret
# CEO: Andrei
# AI Assistant: oCursor

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "help")]
    [string]$Action
)

# Script configuration
$ScriptName = "ogpt_bridge_cron_wrapper.ps1"
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
    
    # Activate virtual environment if it exists
    $VenvPath = ".venv\Scripts\Activate.ps1"
    if (Test-Path $VenvPath) {
        & $VenvPath
        Write-LogMessage "✅ Virtual environment activated"
    }
    
    # Start bridge system in background
    $Job = Start-Job -ScriptBlock {
        param($ScriptPath, $LogPath)
        Set-Location (Split-Path $ScriptPath)
        python (Split-Path $ScriptPath -Leaf) > $LogPath 2>&1
    } -ArgumentList "$ProjectDir\$BridgeScript", "$LogDir\bridge_output.log"
    
    # Save PID (Job ID)
    $Job.Id | Out-File -FilePath $PidFile -Encoding ASCII
    
    Write-LogMessage "✅ oGPT-Bridge started with Job ID: $($Job.Id)"
    Write-LogMessage "📁 Logs: $LogDir\bridge_output.log"
    Write-LogMessage "📄 PID file: $PidFile"
}

# Function to stop bridge
function Stop-Bridge {
    Write-LogMessage "🛑 Stopping oGPT-Bridge System..."
    
    if (Test-Path $PidFile) {
        $JobId = Get-Content $PidFile
        $Job = Get-Job -Id $JobId -ErrorAction SilentlyContinue
        if ($Job) {
            Stop-Job -Id $JobId
            Remove-Job -Id $JobId
            Write-LogMessage "✅ oGPT-Bridge stopped (Job ID: $JobId)"
        } else {
            Write-LogMessage "⚠️ Bridge job not found"
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
        $JobId = Get-Content $PidFile
        Write-LogMessage "✅ oGPT-Bridge is RUNNING (Job ID: $JobId)"
        
        # Show recent logs
        $LogFile = "$LogDir\bridge_output.log"
        if (Test-Path $LogFile) {
            Write-LogMessage "📋 Recent logs (last 5 lines):"
            $RecentLogs = Get-Content $LogFile -Tail 5
            foreach ($Line in $RecentLogs) {
                Write-LogMessage "   $Line"
            }
        }
    } else {
        Write-LogMessage "❌ oGPT-Bridge is NOT RUNNING"
    }
    
    # Show log files
    Write-LogMessage "📁 Log files:"
    Get-ChildItem $LogDir | ForEach-Object {
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
    Write-Host "Usage: .\ogpt_bridge_cron_wrapper.ps1 {start|stop|restart|status|help}"
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
    Write-Host "  Arguments: -ExecutionPolicy Bypass -File `"$ProjectDir\ogpt_bridge_cron_wrapper.ps1`" status"
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
