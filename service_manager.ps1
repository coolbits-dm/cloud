# CoolBits.ai Service Management Script
# PowerShell script for quick service control

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status", "start-all", "stop-all")]
    [string]$Action = "status",
    
    [Parameter(Mandatory=$false)]
    [string]$Service = ""
)

# Service configurations - FINAL CLEANUP
$Services = @{
    "enhanced_multi_agent_chat" = @{
        Name = "Enhanced Multi-Agent Chat"
        File = "enhanced_multi_agent_chat_server.py"
        Port = 8091
        AutoStart = $true
    }
    "unified_dashboard" = @{
        Name = "Unified Dashboard"
        File = "coolbits_unified_dashboard_server.py"
        Port = 8099
        AutoStart = $true
    }
    "rag_system" = @{
        Name = "RAG System"
        File = "rag_categories_system.py"
        Port = 8097
        AutoStart = $true
    }
    "api_cost_dashboard" = @{
        Name = "API Cost Dashboard"
        File = "api_cost_dashboard_server.py"
        Port = 8095
        AutoStart = $true
    }
}

# Python path
$PythonPath = ".\.venv\Scripts\python.exe"

function Get-ServiceStatus {
    param($ServiceId)
    
    $Service = $Services[$ServiceId]
    if (-not $Service) {
        return @{ Status = "Not Found"; Error = "Service not found" }
    }
    
    # Check if process is running
    $Processes = Get-Process -Name "python" -ErrorAction SilentlyContinue
    $IsRunning = $false
    $PID = $null
    
    foreach ($Process in $Processes) {
        try {
            $CommandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($Process.Id)").CommandLine
            if ($CommandLine -and $CommandLine.Contains($Service.File)) {
                $IsRunning = $true
                $PID = $Process.Id
                break
            }
        }
        catch {
            # Ignore errors
        }
    }
    
    # Check if port is in use
    $PortInUse = $false
    try {
        $Connection = Get-NetTCPConnection -LocalPort $Service.Port -ErrorAction SilentlyContinue
        $PortInUse = $Connection -ne $null
    }
    catch {
        # Ignore errors
    }
    
    return @{
        ServiceId = $ServiceId
        Name = $Service.Name
        Status = if ($IsRunning) { "Running" } else { "Stopped" }
        Port = $Service.Port
        PortInUse = $PortInUse
        PID = $PID
        File = $Service.File
    }
}

function Start-Service {
    param($ServiceId)
    
    $Service = $Services[$ServiceId]
    if (-not $Service) {
        Write-Host "❌ Service '$ServiceId' not found" -ForegroundColor Red
        return
    }
    
    $Status = Get-ServiceStatus $ServiceId
    if ($Status.Status -eq "Running") {
        Write-Host "⚠️  Service '$ServiceId' is already running" -ForegroundColor Yellow
        return
    }
    
    if (-not (Test-Path $Service.File)) {
        Write-Host "❌ Service file '$($Service.File)' not found" -ForegroundColor Red
        return
    }
    
    try {
        Write-Host "🚀 Starting $($Service.Name)..." -ForegroundColor Green
        $Process = Start-Process -FilePath $PythonPath -ArgumentList $Service.File -WindowStyle Hidden -PassThru
        Start-Sleep -Seconds 3
        
        if (-not $Process.HasExited) {
            Write-Host "✅ $($Service.Name) started successfully (PID: $($Process.Id))" -ForegroundColor Green
        } else {
            Write-Host "❌ $($Service.Name) failed to start" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Error starting $($Service.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-Service {
    param($ServiceId)
    
    $Service = $Services[$ServiceId]
    if (-not $Service) {
        Write-Host "❌ Service '$ServiceId' not found" -ForegroundColor Red
        return
    }
    
    $Status = Get-ServiceStatus $ServiceId
    if ($Status.Status -eq "Stopped") {
        Write-Host "⚠️  Service '$ServiceId' is already stopped" -ForegroundColor Yellow
        return
    }
    
    if ($Status.PID) {
        try {
            Write-Host "🛑 Stopping $($Service.Name) (PID: $($Status.PID))..." -ForegroundColor Yellow
            Stop-Process -Id $Status.PID -Force
            Start-Sleep -Seconds 2
            Write-Host "✅ $($Service.Name) stopped successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Error stopping $($Service.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  Could not find process for $($Service.Name)" -ForegroundColor Yellow
    }
}

function Restart-Service {
    param($ServiceId)
    
    Write-Host "🔄 Restarting $ServiceId..." -ForegroundColor Cyan
    Stop-Service $ServiceId
    Start-Sleep -Seconds 2
    Start-Service $ServiceId
}

function Show-ServiceStatus {
    param($ServiceId)
    
    if ($ServiceId) {
        $Status = Get-ServiceStatus $ServiceId
        Write-Host "📊 Service Status: $($Status.Name)" -ForegroundColor Cyan
        Write-Host "Status: $($Status.Status)" -ForegroundColor $(if ($Status.Status -eq "Running") { "Green" } else { "Red" })
        Write-Host "Port: $($Status.Port)" -ForegroundColor White
        Write-Host "PID: $($Status.PID)" -ForegroundColor White
        Write-Host "File: $($Status.File)" -ForegroundColor White
    } else {
        Write-Host "📊 All Services Status:" -ForegroundColor Cyan
        Write-Host "=" * 60 -ForegroundColor White
        
        foreach ($ServiceId in $Services.Keys) {
            $Status = Get-ServiceStatus $ServiceId
            $StatusColor = if ($Status.Status -eq "Running") { "Green" } else { "Red" }
            Write-Host "$($Status.Name): $($Status.Status)" -ForegroundColor $StatusColor
            if ($Status.PID) {
                Write-Host "  PID: $($Status.PID), Port: $($Status.Port)" -ForegroundColor Gray
            }
        }
    }
}

function Start-AllServices {
    Write-Host "🚀 Starting all auto-start services..." -ForegroundColor Green
    
    foreach ($ServiceId in $Services.Keys) {
        $Service = $Services[$ServiceId]
        if ($Service.AutoStart) {
            Start-Service $ServiceId
        }
    }
}

function Stop-AllServices {
    Write-Host "🛑 Stopping all services..." -ForegroundColor Red
    
    foreach ($ServiceId in $Services.Keys) {
        Stop-Service $ServiceId
    }
}

# Main execution
switch ($Action) {
    "start" {
        if ($Service) {
            Start-Service $Service
        } else {
            Write-Host "❌ Please specify a service to start" -ForegroundColor Red
            Write-Host "Available services: $($Services.Keys -join ', ')" -ForegroundColor Yellow
        }
    }
    "stop" {
        if ($Service) {
            Stop-Service $Service
        } else {
            Write-Host "❌ Please specify a service to stop" -ForegroundColor Red
            Write-Host "Available services: $($Services.Keys -join ', ')" -ForegroundColor Yellow
        }
    }
    "restart" {
        if ($Service) {
            Restart-Service $Service
        } else {
            Write-Host "❌ Please specify a service to restart" -ForegroundColor Red
            Write-Host "Available services: $($Services.Keys -join ', ')" -ForegroundColor Yellow
        }
    }
    "status" {
        Show-ServiceStatus $Service
    }
    "start-all" {
        Start-AllServices
    }
    "stop-all" {
        Stop-AllServices
    }
}

# Show help if no action specified
if (-not $Action) {
    Write-Host "🎯 CoolBits.ai Service Management Script" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor White
    Write-Host "Usage: .\service_manager.ps1 -Action <action> [-Service <service>]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  start     - Start a specific service" -ForegroundColor White
    Write-Host "  stop      - Stop a specific service" -ForegroundColor White
    Write-Host "  restart   - Restart a specific service" -ForegroundColor White
    Write-Host "  status    - Show service status" -ForegroundColor White
    Write-Host "  start-all - Start all auto-start services" -ForegroundColor White
    Write-Host "  stop-all  - Stop all services" -ForegroundColor White
    Write-Host ""
    Write-Host "Available services:" -ForegroundColor Yellow
    foreach ($ServiceId in $Services.Keys) {
        $Service = $Services[$ServiceId]
        Write-Host "  $ServiceId - $($Service.Name) (Port: $($Service.Port))" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\service_manager.ps1 -Action start -Service enhanced_multi_agent_chat" -ForegroundColor White
    Write-Host "  .\service_manager.ps1 -Action status" -ForegroundColor White
    Write-Host "  .\service_manager.ps1 -Action start-all" -ForegroundColor White
}
