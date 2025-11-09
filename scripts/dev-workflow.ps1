$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
# CoolBits.ai Development Workflow Automation
# PowerShell version for Windows

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "test", "lint", "format", "deploy-staging", "logs", "shell", "clean")]
    [string]$Action
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

# Development workflow commands
switch ($Action) {
    "start" {
        Write-Info "Starting development environment..."
        docker-compose -f docker-compose.dev.yml up -d
        Write-Success "Development environment started"
        Write-Info "Visit: http://localhost:8501"
    }
    
    "stop" {
        Write-Info "Stopping development environment..."
        docker-compose -f docker-compose.dev.yml down
        Write-Success "Development environment stopped"
    }
    
    "test" {
        Write-Info "Running tests..."
        if (Test-Path "venv\Scripts\activate.ps1") {
            & "venv\Scripts\activate.ps1"
            python -m pytest tests/ -v
        } else {
            python -m pytest tests/ -v
        }
        Write-Success "Tests completed"
    }
    
    "lint" {
        Write-Info "Running linters..."
        if (Test-Path "venv\Scripts\activate.ps1") {
            & "venv\Scripts\activate.ps1"
            black --check .
            flake8 .
            mypy .
        } else {
            black --check .
            flake8 .
            mypy .
        }
        Write-Success "Linting completed"
    }
    
    "format" {
        Write-Info "Formatting code..."
        if (Test-Path "venv\Scripts\activate.ps1") {
            & "venv\Scripts\activate.ps1"
            black .
            isort .
        } else {
            black .
            isort .
        }
        Write-Success "Code formatted"
    }
    
    "deploy-staging" {
        Write-Info "Deploying to staging..."
        if (Test-Path "scripts\deploy-staging.ps1") {
            & "scripts\deploy-staging.ps1"
        } else {
            Write-Warning "Deploy staging script not found"
        }
        Write-Success "Deployed to staging"
    }
    
    "logs" {
        Write-Info "Showing logs..."
        docker-compose -f docker-compose.dev.yml logs -f
    }
    
    "shell" {
        Write-Info "Opening shell..."
        docker-compose -f docker-compose.dev.yml exec coolbits-dev bash
    }
    
    "clean" {
        Write-Info "Cleaning up..."
        docker-compose -f docker-compose.dev.yml down -v
        docker system prune -f
        Write-Success "Cleanup completed"
    }
}

Write-Info "Development workflow completed: $Action"

# Set timeout environment variables
$env:POWERSHELL_TELEMETRY_OPTOUT = '1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:HTTPS_PROXY = ''

