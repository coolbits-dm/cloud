# scripts/m18_plan.ps1 - Master M18 orchestrator
# Non-interactive execution only

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$InformationPreference = 'SilentlyContinue'
$ConfirmPreference = 'None'

# Set environment
$env:CB_BILLING_MODE = 'dev'
$env:PYTHONUTF8 = '1'

Write-Host "M18 Plan: Starting non-interactive execution..." -ForegroundColor Green

try {
    # 1. Guard non-interactive
    Write-Host "Step 1: Non-interactive guard check..." -ForegroundColor Yellow
    & "scripts/no_interactive_guard.ps1"
    
    # 2. Run M18 pipeline
    Write-Host "Step 2: Running M18 pipeline..." -ForegroundColor Yellow
    & "scripts/runner_m18.ps1"
    
    # 3. Generate report
    Write-Host "Step 3: Generating M18 report..." -ForegroundColor Yellow
    python scripts/generate_report.py
    
    # 4. Final status
    Write-Host "M18 Plan: COMPLETED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "Report available at: report/index.html" -ForegroundColor Cyan
    
    # Return success
    exit 0
    
} catch {
    Write-Host "M18 Plan: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
