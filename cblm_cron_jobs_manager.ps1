# cbLM Corporate Entities Cron Jobs PowerShell Manager
# COOL BITS SRL 🏢 - Internal Secret

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "status", "restart")]
    [string]$Action = "start"
)

$Company = "COOL BITS SRL 🏢"
$CEO = "Andrei"
$AIAssistant = "oCursor"
$ProjectRoot = "C:\Users\andre\Desktop\coolbits"
$CronManagerPath = "$ProjectRoot\cblm\corporate_entities_cron_manager.py"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "COOL BITS SRL 🏢 - CBLM CORPORATE ENTITIES CRON JOBS MANAGER" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "CEO: $CEO" -ForegroundColor Yellow
Write-Host "AI Assistant: $AIAssistant" -ForegroundColor Yellow
Write-Host "Classification: Internal Secret - CoolBits.ai 🏢 Members Only" -ForegroundColor Red
Write-Host "================================================================================" -ForegroundColor Cyan

# Corporate Entities
$CorporateEntities = @(
    @{Name="Vertex AI"; Key="vertex"; Zone="google_cloud"; Priority="high"; Schedule="every 5 minutes"},
    @{Name="Cursor AI Assistant"; Key="cursor"; Zone="development"; Priority="high"; Schedule="every 2 minutes"},
    @{Name="NVIDIA GPU Pipeline"; Key="nvidia"; Zone="gpu_processing"; Priority="critical"; Schedule="every 1 minute"},
    @{Name="Microsoft Ecosystem"; Key="microsoft"; Zone="windows_ecosystem"; Priority="high"; Schedule="every 3 minutes"},
    @{Name="xAI Platform"; Key="xai"; Zone="ai_platform"; Priority="medium"; Schedule="every 4 minutes"},
    @{Name="Grok AI"; Key="grok"; Zone="ai_platform"; Priority="medium"; Schedule="every 4 minutes"},
    @{Name="oGrok"; Key="ogrok"; Zone="coolbits_proprietary"; Priority="critical"; Schedule="every 2 minutes"},
    @{Name="OpenAI Platform"; Key="openai"; Zone="ai_platform"; Priority="high"; Schedule="every 3 minutes"},
    @{Name="ChatGPT"; Key="chatgpt"; Zone="ai_platform"; Priority="high"; Schedule="every 3 minutes"},
    @{Name="oGPT"; Key="ogpt"; Zone="coolbits_proprietary"; Priority="critical"; Schedule="every 2 minutes"}
)

# Zones
$Zones = @{
    "google_cloud" = @{Name="Google Cloud Zone"; Priority="high"}
    "development" = @{Name="Development Zone"; Priority="high"}
    "gpu_processing" = @{Name="GPU Processing Zone"; Priority="critical"}
    "windows_ecosystem" = @{Name="Windows Ecosystem Zone"; Priority="high"}
    "ai_platform" = @{Name="AI Platform Zone"; Priority="medium"}
    "coolbits_proprietary" = @{Name="COOL BITS SRL 🏢 Proprietary Zone"; Priority="critical"}
}

function Start-CronJobs {
    Write-Host "Starting Corporate Entities Cron Jobs..." -ForegroundColor Green
    
    Set-Location $ProjectRoot
    
    # Start the cron manager
    Start-Process python -ArgumentList $CronManagerPath -WindowStyle Normal
    
    Write-Host "Cron Jobs Manager Started!" -ForegroundColor Green
    Write-Host "All entities are now always-on and paired with their zones" -ForegroundColor Yellow
}

function Stop-CronJobs {
    Write-Host "Stopping Corporate Entities Cron Jobs..." -ForegroundColor Red
    
    # Find and stop Python processes running the cron manager
    $Processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*corporate_entities_cron_manager.py*"
    }
    
    if ($Processes) {
        $Processes | Stop-Process -Force
        Write-Host "Stopped $($Processes.Count) cron job processes" -ForegroundColor Green
    } else {
        Write-Host "No cron job processes found" -ForegroundColor Yellow
    }
}

function Get-CronJobsStatus {
    Write-Host "Corporate Entities Cron Jobs Status:" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
    
    Write-Host "ENTITIES STATUS:" -ForegroundColor Yellow
    Write-Host "----------------------------------------------------------------" -ForegroundColor Gray
    
    foreach ($Entity in $CorporateEntities) {
        $ZoneInfo = $Zones[$Entity.Zone]
        Write-Host "$($Entity.Name) ($($Entity.Key))" -ForegroundColor Green
        Write-Host "   Zone: $($ZoneInfo.Name)" -ForegroundColor White
        Write-Host "   Priority: $($Entity.Priority)" -ForegroundColor White
        Write-Host "   Schedule: $($Entity.Schedule)" -ForegroundColor White
        Write-Host "   Always On: True" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "ZONES STATUS:" -ForegroundColor Yellow
    Write-Host "----------------------------------------------------------------" -ForegroundColor Gray
    
    foreach ($ZoneKey in $Zones.Keys) {
        $Zone = $Zones[$ZoneKey]
        $PriorityColor = switch ($Zone.Priority) {
            "critical" { "Red" }
            "high" { "Yellow" }
            "medium" { "Green" }
            default { "White" }
        }
        
        Write-Host "$($Zone.Name) ($ZoneKey)" -ForegroundColor Cyan
        Write-Host "   Priority: $($Zone.Priority)" -ForegroundColor $PriorityColor
        Write-Host ""
    }
    
    # Check if cron manager is running
    $CronProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*corporate_entities_cron_manager.py*"
    }
    
    if ($CronProcesses) {
        Write-Host "Cron Manager Status: RUNNING ($($CronProcesses.Count) processes)" -ForegroundColor Green
    } else {
        Write-Host "Cron Manager Status: STOPPED" -ForegroundColor Red
    }
    
    Write-Host "================================================================================" -ForegroundColor Cyan
}

function Restart-CronJobs {
    Write-Host "Restarting Corporate Entities Cron Jobs..." -ForegroundColor Yellow
    
    Stop-CronJobs
    Start-Sleep -Seconds 2
    Start-CronJobs
    
    Write-Host "Cron Jobs Restarted!" -ForegroundColor Green
}

# Main execution
switch ($Action.ToLower()) {
    "start" {
        Start-CronJobs
    }
    "stop" {
        Stop-CronJobs
    }
    "status" {
        Get-CronJobsStatus
    }
    "restart" {
        Restart-CronJobs
    }
    default {
        Write-Host "Invalid action. Use: start, stop, status, or restart" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Classification: Internal Secret - CoolBits.ai 🏢 Members Only" -ForegroundColor Red
Write-Host "Owner: $Company" -ForegroundColor Yellow