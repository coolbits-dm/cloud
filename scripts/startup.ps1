$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
# CoolBits.ai Non-Interactive Startup Script
# ==========================================

param(
    [string]$Action = "start",
    [int]$BridgePort = 8765,
    [int]$WebPort = 3001
)

# Set non-interactive environment
$env:CI = "1"
$env:NO_COLOR = "1"
$env:GCLOUD_SUPPRESS_PROMPTS = "1"
$env:CLOUDSDK_CORE_DISABLE_PROMPTS = "1"
$env:BRIDGE_PORT = $BridgePort.ToString()
$env:PORT = $WebPort.ToString()

Write-Host "🚀 CoolBits.ai Non-Interactive Startup"
Write-Host "======================================="
Write-Host "Action: $Action"
Write-Host "Bridge Port: $BridgePort"
Write-Host "Web Port: $WebPort"
Write-Host ""

if ($Action -eq "start") {
    # Kill existing processes
    Write-Host "🧹 Cleaning existing processes..."
    $ports = @(3001, 8000, 8765, 8080, 8101, 8102)
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
    Write-Host "`n🌉 Starting Bridge (FastAPI) on port $BridgePort..."
    $bridgeArgs = @(
        "coolbits_main_bridge.py"
    )
    
    $bridgeProcess = Start-Process -NoNewWindow -Wait -WindowStyle Hidden -FilePath "python" -ArgumentList $bridgeArgs -PassThru
    Write-Host "  ✅ Bridge started (PID: $($bridgeProcess.Id))"
    
    # Wait for bridge to become healthy (bridge runs on port 8100)
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
    
    # Start Web App
    Write-Host "`n🌐 Starting Web App on port $WebPort..."
    $webArgs = @(
        "coolbits_main_dashboard.py"
    )
    
    $webProcess = Start-Process -NoNewWindow -Wait -WindowStyle Hidden -FilePath "python" -ArgumentList $webArgs -PassThru
    Write-Host "  ✅ Web app started (PID: $($webProcess.Id))"
    
    # Wait for web app
    Write-Host "`n⏳ Waiting for web app to become healthy..."
    $webHealthy = $false
    for ($i = 0; $i -lt 15; $i++) {
        try {
            $response = Invoke-RestMethod "http://127.0.0.1:$WebPort/api/status" -TimeoutSec 2
            $webHealthy = $true
            Write-Host "  ✅ Web app healthy after $($i + 1) seconds"
            break
        } catch {
            Start-Sleep 1
            Write-Host "  ⏳ Waiting... ($($i + 1)/15)"
        }
    }
    
    if (-not $webHealthy) {
        Write-Host "  ❌ Web app failed to become healthy"
        exit 1
    }
    
    # Save runtime info
    $runtimeInfo = @{
        port = $WebPort
        bridge_port = 8100  # Bridge always runs on 8100
        bridge_pid = $bridgeProcess.Id
        web_pid = $webProcess.Id
        started_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }
    
    $runtimeInfo | ConvertTo-Json | Out-File -FilePath ".runtime.json" -Encoding UTF8
    Write-Host "`n📝 Runtime info saved to .runtime.json"
    
    Write-Host "`n✅ CoolBits.ai started successfully!"
    Write-Host "🌐 Web App: http://127.0.0.1:$WebPort"
    Write-Host "🌉 Bridge: http://127.0.0.1:8100"
    Write-Host "🏥 Health: http://127.0.0.1:$WebPort/api/status"
    
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
            taskkill /PID $rt.web_pid /F | Out-Null
            Write-Host "  ✅ Web app stopped"
        } catch { Write-Host "  ⚠️  Web app already stopped" }
    }
    
    # Kill any remaining processes on our ports
    $ports = @(3001, 8000, 8765, 8080, 8101, 8102)
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
        Write-Host "  Web Port: $($rt.port)"
        Write-Host "  Bridge Port: $($rt.bridge_port)"
        Write-Host "  Started: $($rt.started_at)"
        
        # Check if processes are still running
        try {
            Get-Process -Id $rt.bridge_pid -ErrorAction Stop | Out-Null
            Write-Host "  ✅ Bridge process running"
        } catch {
            Write-Host "  ❌ Bridge process not running"
        }
        
        try {
            Get-Process -Id $rt.web_pid -ErrorAction Stop | Out-Null
            Write-Host "  ✅ Web process running"
        } catch {
            Write-Host "  ❌ Web process not running"
        }
    } else {
        Write-Host "❌ No runtime info found"
    }
    
    # Port status
    Write-Host "`nPort Status:"
    $ports = @(3001, 8000, 8765, 8080, 8101, 8102)
    foreach ($p in $ports) {
        $isOpen = (Test-NetConnection -ComputerName 127.0.0.1 -Port $p -InformationLevel Quiet)
        $status = if ($isOpen) { "✅" } else { "❌" }
        Write-Host "  $status Port $p"
    }
}

Write-Host "`n🎯 Use: pwsh scripts/startup.ps1 -Action start|stop|status"

# Set timeout environment variables
$env:POWERSHELL_TELEMETRY_OPTOUT = '1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:HTTPS_PROXY = ''

