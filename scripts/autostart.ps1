# CoolBits.ai Autostart Script
# ============================

param(
    [string]$Action = "start"
)

# Set non-interactive environment
$env:CI = "1"
$env:NO_COLOR = "1"
$env:GCLOUD_SUPPRESS_PROMPTS = "1"
$env:CLOUDSDK_CORE_DISABLE_PROMPTS = "1"
$env:GIT_TERMINAL_PROMPT = "0"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
$ProgressPreference = 'SilentlyContinue'
$ErrorActionPreference = 'Stop'

Write-Host "🚀 CoolBits.ai Autostart Script"
Write-Host "================================="
Write-Host "Action: $Action"
Write-Host ""

if ($Action -eq "start") {
    # Kill existing processes first
    Write-Host "🧹 Cleaning existing processes..."
    $ports = @(8080, 8100)
    foreach ($p in $ports) {
        Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | 
        ForEach-Object { 
            try { 
                taskkill /PID $_.OwningProcess /F | Out-Null
                Write-Host "  ✅ Killed process on port $p"
            } catch {
                Write-Host "  ⚠️  No process on port $p"
            }
        }
    }
    
    # Remove lock files
    Remove-Item .server.lock, .runtime.json -ErrorAction SilentlyContinue
    
    # Start Bridge (FastAPI) first
    Write-Host "`n🌉 Starting Bridge (FastAPI) on port 8100..."
    $bridgeArgs = @("coolbits_main_bridge.py")
    $bridgeProcess = Start-Process -WindowStyle Hidden -FilePath "python" -ArgumentList $bridgeArgs -PassThru
    Write-Host "  ✅ Bridge started (PID: $($bridgeProcess.Id))"
    
    # Wait for bridge to become healthy
    Write-Host "`n⏳ Waiting for bridge to become healthy..."
    $bridgeHealthy = $false
    for ($i = 0; $i -lt 20; $i++) {
        try {
            $response = Invoke-RestMethod "http://127.0.0.1:8100/health" -TimeoutSec 2
            $bridgeHealthy = $true
            Write-Host "  ✅ Bridge healthy after $($i + 1) seconds"
            break
        } catch {
            Start-Sleep 1
            Write-Host "  ⏳ Waiting... ($($i + 1)/20)"
        }
    }
    
    if (-not $bridgeHealthy) {
        Write-Host "  ❌ Bridge failed to become healthy"
        exit 1
    }
    
    # Start Dashboard
    Write-Host "`n🌐 Starting Dashboard on port 8080..."
    $dashboardArgs = @("coolbits_main_dashboard.py")
    $dashboardProcess = Start-Process -WindowStyle Hidden -FilePath "python" -ArgumentList $dashboardArgs -PassThru
    Write-Host "  ✅ Dashboard started (PID: $($dashboardProcess.Id))"
    
    # Wait for dashboard
    Write-Host "`n⏳ Waiting for dashboard to become healthy..."
    $dashboardHealthy = $false
    for ($i = 0; $i -lt 15; $i++) {
        try {
            $response = Invoke-RestMethod "http://127.0.0.1:8080/api/services/status" -TimeoutSec 2
            $dashboardHealthy = $true
            Write-Host "  ✅ Dashboard healthy after $($i + 1) seconds"
            break
        } catch {
            Start-Sleep 1
            Write-Host "  ⏳ Waiting... ($($i + 1)/15)"
        }
    }
    
    if (-not $dashboardHealthy) {
        Write-Host "  ❌ Dashboard failed to become healthy"
        exit 1
    }
    
    # Save runtime info
    $runtimeInfo = @{
        port = 8080
        bridge_port = 8100
        bridge_pid = $bridgeProcess.Id
        dashboard_pid = $dashboardProcess.Id
        started_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        autostart = $true
    }
    
    $runtimeInfo | ConvertTo-Json | Out-File -FilePath ".runtime.json" -Encoding UTF8
    Write-Host "`n📝 Runtime info saved to .runtime.json"
    
    # Log to boot health log
    $logEntry = "OK $(Get-Date -Format o)"
    $logEntry | Out-File -Append -FilePath "logs\boot-health.log" -Encoding UTF8
    
    Write-Host "`n✅ CoolBits.ai autostart completed successfully!"
    Write-Host "🌐 Dashboard: http://127.0.0.1:8080"
    Write-Host "🌉 Bridge: http://127.0.0.1:8100"
    Write-Host "📝 Logged to: logs\boot-health.log"
    
} elseif ($Action -eq "stop") {
    Write-Host "🛑 Stopping CoolBits.ai services..."
    
    # Read runtime info
    if (Test-Path ".runtime.json") {
        $rt = Get-Content .runtime.json | ConvertFrom-Json
        try {
            taskkill /PID $rt.bridge_pid /F | Out-Null
            Write-Host "  ✅ Bridge stopped"
        } catch { Write-Host "  ⚠️  Bridge already stopped" }
        
        try {
            taskkill /PID $rt.dashboard_pid /F | Out-Null
            Write-Host "  ✅ Dashboard stopped"
        } catch { Write-Host "  ⚠️  Dashboard already stopped" }
    }
    
    # Kill any remaining processes on our ports
    $ports = @(8080, 8100)
    foreach ($p in $ports) {
        Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | 
        ForEach-Object { 
            try { 
                taskkill /PID $_.OwningProcess /F | Out-Null
            } catch {}
        }
    }
    
    Remove-Item .runtime.json -ErrorAction SilentlyContinue
    Write-Host "✅ All services stopped"
    
} elseif ($Action -eq "status") {
    Write-Host "📊 CoolBits.ai Status Check"
    Write-Host "=========================="
    
    if (Test-Path ".runtime.json") {
        $rt = Get-Content .runtime.json | ConvertFrom-Json
        Write-Host "Runtime Info:"
        Write-Host "  Dashboard Port: $($rt.port)"
        Write-Host "  Bridge Port: $($rt.bridge_port)"
        Write-Host "  Started: $($rt.started_at)"
        Write-Host "  Autostart: $($rt.autostart)"
        
        # Check if processes are still running
        try {
            Get-Process -Id $rt.bridge_pid -ErrorAction Stop | Out-Null
            Write-Host "  ✅ Bridge process running"
        } catch {
            Write-Host "  ❌ Bridge process not running"
        }
        
        try {
            Get-Process -Id $rt.dashboard_pid -ErrorAction Stop | Out-Null
            Write-Host "  ✅ Dashboard process running"
        } catch {
            Write-Host "  ❌ Dashboard process not running"
        }
    } else {
        Write-Host "❌ No runtime info found"
    }
    
    # Port status
    Write-Host "`nPort Status:"
    $ports = @(8080, 8100)
    foreach ($p in $ports) {
        $isOpen = (Test-NetConnection -ComputerName 127.0.0.1 -Port $p -InformationLevel Quiet)
        $status = if ($isOpen) { "✅" } else { "❌" }
        Write-Host "  $status Port $p"
    }
    
    # Health check
    Write-Host "`nHealth Check:"
    try {
        $bridge = Invoke-RestMethod "http://127.0.0.1:8100/health" -TimeoutSec 3
        Write-Host "  ✅ Bridge healthy"
    } catch {
        Write-Host "  ❌ Bridge unhealthy"
    }
    
    try {
        $dashboard = Invoke-RestMethod "http://127.0.0.1:8080/api/services/status" -TimeoutSec 3
        Write-Host "  ✅ Dashboard healthy"
    } catch {
        Write-Host "  ❌ Dashboard unhealthy"
    }
}

Write-Host "`n🎯 Use: pwsh scripts/autostart.ps1 -Action start|stop|status"
