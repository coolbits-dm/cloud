$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
# CoolBits.ai Chaos Engineering - PowerShell Runner
# Run chaos experiments locally and on staging

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("network_latency", "service_kill", "cpu_spike", "mem_leak", "db_fail", "ext_api_fail", "all")]
    [string]$Scenario,
    
    [string]$Environment = "staging",
    [switch]$DryRun,
    [switch]$Verbose
)

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

# Functions
function Write-Info { param($Message) Write-Host "${Blue}[INFO]${Reset} $Message" }
function Write-Success { param($Message) Write-Host "${Green}[SUCCESS]${Reset} $Message" }
function Write-Warning { param($Message) Write-Host "${Yellow}[WARNING]${Reset} $Message" }
function Write-Error { param($Message) Write-Host "${Red}[ERROR]${Reset} $Message" }

# Configuration
$ChaosDir = "chaos"
$ScenariosDir = "$ChaosDir/scenarios"
$ReportsDir = "$ChaosDir/reports"

# Create directories
if (!(Test-Path $ReportsDir)) {
    New-Item -ItemType Directory -Path $ReportsDir | Out-Null
}

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Python
    try {
        python --version | Out-Null
    } catch {
        Write-Error "Python not found. Please install Python 3.11+"
        exit 1
    }
    
    # Check Docker
    try {
        docker --version | Out-Null
    } catch {
        Write-Error "Docker not found. Please install Docker"
        exit 1
    }
    
    # Check if services are running
    $runningContainers = docker ps --format "{{.Names}}"
    if ($runningContainers -notmatch "coolbits") {
        Write-Warning "CoolBits services not running. Starting development environment..."
        docker-compose -f docker-compose.dev.yml up -d
        Start-Sleep 30
    }
    
    Write-Success "Prerequisites check passed"
}

# Run single scenario
function Start-ChaosScenario {
    param(
        [string]$ScenarioName,
        [string]$Environment,
        [bool]$DryRun
    )
    
    $scenarioFile = "$ScenariosDir/$ScenarioName.yaml"
    
    if (!(Test-Path $scenarioFile)) {
        Write-Error "Scenario file not found: $scenarioFile"
        return $false
    }
    
    Write-Info "Running chaos scenario: $ScenarioName"
    
    if ($DryRun) {
        Write-Warning "DRY RUN: Would run scenario $ScenarioName"
        return $true
    }
    
    # Set environment
    $env:OPIPE_ENV = $Environment
    
    # Run scenario
    try {
        $result = python "$ChaosDir/runners/runner.py" $scenarioFile
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Success "Scenario $ScenarioName PASSED"
            return $true
        } else {
            Write-Error "Scenario $ScenarioName FAILED"
            Write-Info "Result: $result"
            return $false
        }
    } catch {
        Write-Error "Failed to run scenario $ScenarioName`: $_"
        return $false
    }
}

# Run all scenarios
function Start-AllScenarios {
    param(
        [string]$Environment,
        [bool]$DryRun
    )
    
    $scenarios = @(
        "network_latency",
        "service_kill", 
        "cpu_spike",
        "mem_leak",
        "db_fail",
        "ext_api_fail"
    )
    
    $results = @{}
    $totalScenarios = $scenarios.Count
    $passedScenarios = 0
    
    Write-Info "Running all chaos scenarios ($totalScenarios total)"
    
    foreach ($scenario in $scenarios) {
        Write-Info "Running scenario: $scenario"
        
        $success = Start-ChaosScenario -ScenarioName $scenario -Environment $Environment -DryRun $DryRun
        $results[$scenario] = $success
        
        if ($success) {
            $passedScenarios++
        }
        
        # Wait between scenarios
        if ($scenario -ne $scenarios[-1]) {
            Start-Sleep 60
        }
    }
    
    # Summary
    Write-Host ""
    Write-Info "=== Chaos Experiment Summary ==="
    Write-Info "Total scenarios: $totalScenarios"
    Write-Info "Passed: $passedScenarios"
    Write-Info "Failed: $($totalScenarios - $passedScenarios)"
    
    foreach ($scenario in $scenarios) {
        $status = if ($results[$scenario]) { "PASS" } else { "FAIL" }
        $color = if ($results[$scenario]) { $Green } else { $Red }
        Write-Host "${color}$scenario: $status${Reset}"
    }
    
    if ($passedScenarios -eq $totalScenarios) {
        Write-Success "All chaos scenarios passed!"
        return $true
    } else {
        Write-Error "Some chaos scenarios failed!"
        return $false
    }
}

# Generate chaos report
function New-ChaosReport {
    param(
        [hashtable]$Results
    )
    
    $reportFile = "$ReportsDir/chaos_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
    
    $report = @"
# CoolBits.ai Chaos Engineering Report

**Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Environment**: $Environment
**Total Scenarios**: $($Results.Count)

## Results Summary

"@
    
    foreach ($scenario in $Results.Keys) {
        $status = if ($Results[$scenario]) { "✅ PASS" } else { "❌ FAIL" }
        $report += "`n- **$scenario**: $status"
    }
    
    $report += @"

## Recommendations

- Continue regular chaos experiments
- Monitor SLO trends over time
- Update scenarios based on findings
- Review auto-heal mechanisms

## Next Steps

- Schedule next chaos experiment
- Review failed scenarios
- Update documentation
- Train team on chaos engineering
"@
    
    $report | Out-File -FilePath $reportFile -Encoding UTF8
    Write-Success "Chaos report generated: $reportFile"
}

# Main execution
function Start-ChaosExperiments {
    Write-Info "Starting CoolBits.ai Chaos Engineering"
    Write-Info "Scenario: $Scenario"
    Write-Info "Environment: $Environment"
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - No actual experiments will be run"
    }
    
    # Check prerequisites
    Test-Prerequisites
    
    # Run scenarios
    $success = $false
    
    if ($Scenario -eq "all") {
        $results = @{}
        $scenarios = @("network_latency", "service_kill", "cpu_spike", "mem_leak", "db_fail", "ext_api_fail")
        
        foreach ($scenario in $scenarios) {
            $scenarioSuccess = Start-ChaosScenario -ScenarioName $scenario -Environment $Environment -DryRun $DryRun
            $results[$scenario] = $scenarioSuccess
        }
        
        $success = ($results.Values | Where-Object { $_ -eq $true }).Count -eq $results.Count
        
        # Generate report
        New-ChaosReport -Results $results
        
    } else {
        $success = Start-ChaosScenario -ScenarioName $Scenario -Environment $Environment -DryRun $DryRun
    }
    
    if ($success) {
        Write-Success "Chaos experiments completed successfully!"
        exit 0
    } else {
        Write-Error "Chaos experiments failed!"
        exit 1
    }
}

# Run main function
Start-ChaosExperiments

# Set timeout environment variables
$env:POWERSHELL_TELEMETRY_OPTOUT = '1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:HTTPS_PROXY = ''

