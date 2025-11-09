$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
# CoolBits.ai Development Environment Setup
# PowerShell version for Windows - One-command developer setup

param(
    [switch]$SkipPrerequisites
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

Write-Info "🚀 Setting up CoolBits.ai development environment..."

# Check prerequisites
function Test-Prerequisites {
    if ($SkipPrerequisites) {
        Write-Warning "Skipping prerequisites check"
        return
    }
    
    Write-Info "📋 Checking prerequisites..."
    
    $missingTools = @()
    
    # Check Git
    try {
        git --version | Out-Null
    } catch {
        $missingTools += "git"
    }
    
    # Check Docker
    try {
        docker --version | Out-Null
    } catch {
        $missingTools += "docker"
    }
    
    # Check Python
    try {
        python --version | Out-Null
    } catch {
        $missingTools += "python"
    }
    
    # Check Google Cloud CLI
    try {
        gcloud --version | Out-Null
    } catch {
        $missingTools += "gcloud"
    }
    
    if ($missingTools.Count -gt 0) {
        Write-Error "Missing required tools: $($missingTools -join ', ')"
        Write-Info "Please install the missing tools and run this script again."
        Write-Info "Or use -SkipPrerequisites to continue anyway."
        exit 1
    }
    
    Write-Success "All prerequisites found"
}

# Setup Python environment
function Setup-PythonEnvironment {
    Write-Info "🐍 Setting up Python environment..."
    
    # Create virtual environment
    python -m venv venv
    
    # Activate virtual environment
    & "venv\Scripts\activate.ps1"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install development dependencies
    if (Test-Path "requirements-dev.txt") {
        pip install -r requirements-dev.txt
    } else {
        pip install streamlit requests pytest black flake8 mypy pre-commit
    }
    
    Write-Success "Python environment ready"
}

# Setup pre-commit hooks
function Setup-PreCommitHooks {
    Write-Info "🔧 Setting up pre-commit hooks..."
    
    if (Test-Path ".pre-commit-config.yaml") {
        pip install pre-commit
        pre-commit install
        Write-Success "Pre-commit hooks installed"
    } else {
        Write-Warning "Pre-commit configuration not found, skipping..."
    }
}

# Setup VS Code workspace
function Setup-VSCodeWorkspace {
    Write-Info "💻 Setting up VS Code workspace..."
    
    # Create .vscode directory
    if (!(Test-Path ".vscode")) {
        New-Item -ItemType Directory -Path ".vscode" | Out-Null
    }
    
    # Create VS Code settings
    $vscodeSettings = @{
        "python.defaultInterpreterPath" = "./venv/Scripts/python.exe"
        "python.linting.enabled" = $true
        "python.linting.pylintEnabled" = $true
        "python.formatting.provider" = "black"
        "python.linting.flake8Enabled" = $true
        "files.exclude" = @{
            "**/__pycache__" = $true
            "**/*.pyc" = $true
            "**/venv" = $true
            "**/.pytest_cache" = $true
        }
        "python.testing.pytestEnabled" = $true
        "python.testing.pytestArgs" = @("tests")
    }
    
    $vscodeSettings | ConvertTo-Json -Depth 3 | Out-File -FilePath ".vscode\settings.json" -Encoding UTF8
    
    # Create VS Code launch configuration
    $launchConfig = @{
        "version" = "0.2.0"
        "configurations" = @(
            @{
                "name" = "CoolBits Debug"
                "type" = "python"
                "request" = "launch"
                "program" = "`${workspaceFolder}/coolbits_web_app.py"
                "console" = "integratedTerminal"
                "env" = @{
                    "OPIPE_ENV" = "development"
                    "GOOGLE_CLOUD_PROJECT" = "coolbits-ai"
                }
            }
        )
    }
    
    $launchConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath ".vscode\launch.json" -Encoding UTF8
    
    Write-Success "VS Code workspace configured"
}

# Setup Docker environment
function Setup-DockerEnvironment {
    Write-Info "🐳 Setting up Docker environment..."
    
    # Create development Docker Compose file
    $dockerComposeContent = @"
version: '3.8'
services:
  coolbits-dev:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPIPE_ENV=development
      - GOOGLE_CLOUD_PROJECT=coolbits-ai
    volumes:
      - .:/app
      - /app/venv
    command: streamlit run coolbits_web_app.py --server.port=8501 --server.address=0.0.0.0
    depends_on:
      - redis-dev
      - postgres-dev
    
  redis-dev:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    
  postgres-dev:
    image: postgres:15
    environment:
      - POSTGRES_DB=coolbits_dev
      - POSTGRES_USER=coolbits
      - POSTGRES_PASSWORD=dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres_data:
  redis_data:
"@
    
    $dockerComposeContent | Out-File -FilePath "docker-compose.dev.yml" -Encoding UTF8
    
    Write-Success "Docker environment configured"
}

# Setup development scripts
function Setup-DevelopmentScripts {
    Write-Info "📜 Setting up development scripts..."
    
    # Create directories
    if (!(Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" | Out-Null
    }
    
    if (!(Test-Path "tests")) {
        New-Item -ItemType Directory -Path "tests" | Out-Null
    }
    
    # Create basic test file
    $testContent = @"
import pytest
import requests

def test_health_check():
    """Test basic health check"""
    response = requests.get("http://localhost:8501/_stcore/health")
    assert response.status_code == 200

def test_api_endpoints():
    """Test API endpoints"""
    endpoints = ["/api/v1/health", "/api/v1/status"]
    
    for endpoint in endpoints:
        response = requests.get(f"http://localhost:8501{endpoint}")
        assert response.status_code == 200
"@
    
    $testContent | Out-File -FilePath "tests\test_basic.py" -Encoding UTF8
    
    Write-Success "Development scripts configured"
}

# Setup environment variables
function Setup-EnvironmentVariables {
    Write-Info "🔐 Setting up environment variables..."
    
    if (!(Test-Path ".env")) {
        $envContent = @"
# CoolBits.ai Development Environment
OPIPE_ENV=development
GOOGLE_CLOUD_PROJECT=coolbits-ai
DEBUG=true

# Database
DATABASE_URL=postgresql://coolbits:dev_password@localhost:5432/coolbits_dev

# Redis
REDIS_URL=redis://localhost:6379

# API Keys (use Secret Manager in production)
OPENAI_API_KEY=your_openai_key_here
XAI_API_KEY=your_xai_key_here
"@
        
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Warning "Created .env file - please update with your API keys"
    } else {
        Write-Info ".env file already exists"
    }
}

# Main setup function
function Start-Setup {
    Write-Info "Starting CoolBits.ai development setup..."
    
    Test-Prerequisites
    Setup-PythonEnvironment
    Setup-PreCommitHooks
    Setup-VSCodeWorkspace
    Setup-DockerEnvironment
    Setup-DevelopmentScripts
    Setup-EnvironmentVariables
    
    Write-Host ""
    Write-Success "🎉 Development environment setup complete!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Activate Python environment: venv\Scripts\activate.ps1"
    Write-Host "2. Update .env file with your API keys"
    Write-Host "3. Start development: .\scripts\dev-workflow.ps1 start"
    Write-Host "4. Open VS Code: code ."
    Write-Host "5. Visit: http://localhost:8501"
    Write-Host ""
    Write-Host "Happy coding! 🚀"
}

# Run main function
Start-Setup

# Set timeout environment variables
$env:POWERSHELL_TELEMETRY_OPTOUT = '1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:HTTPS_PROXY = ''

