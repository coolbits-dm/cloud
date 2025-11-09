# CoolBits.ai Test Scripts for Windows PowerShell
# ===============================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("python", "node", "e2e", "docker", "all")]
    [string]$TestType
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

Write-Host "🚀 CoolBits.ai Test Suite" -ForegroundColor $Green
Write-Host "================================"

# Function to run Python tests
function Run-PythonTests {
    Write-Host "📝 Running Python tests..." -ForegroundColor $Yellow
    
    # Install test dependencies
    pip install pytest pytest-cov pytest-mock black isort flake8 mypy
    
    # Run linting
    Write-Host "🔍 Running Python linting..." -ForegroundColor $Yellow
    black --check --diff . 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Black formatting issues found" -ForegroundColor $Red }
    
    isort --check-only --diff . 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Import sorting issues found" -ForegroundColor $Red }
    
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Flake8 issues found" -ForegroundColor $Red }
    
    # Run type checking
    Write-Host "🔍 Running type checking..." -ForegroundColor $Yellow
    mypy . --ignore-missing-imports 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Type checking issues found" -ForegroundColor $Red }
    
    # Run unit tests
    Write-Host "🧪 Running Python unit tests..." -ForegroundColor $Yellow
    pytest tests/unit/ --cov=. --cov-report=xml --cov-report=html 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Python tests failed" -ForegroundColor $Red }
    
    Write-Host "✅ Python tests completed" -ForegroundColor $Green
}

# Function to run Node.js tests
function Run-NodeTests {
    Write-Host "📝 Running Node.js tests..." -ForegroundColor $Yellow
    
    # Install dependencies
    npm install
    
    # Install dev dependencies
    npm install --save-dev eslint prettier jest @types/jest
    
    # Run linting
    Write-Host "🔍 Running Node.js linting..." -ForegroundColor $Yellow
    npx eslint . --ext .js,.ts,.jsx,.tsx 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ ESLint issues found" -ForegroundColor $Red }
    
    npx prettier --check . 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Prettier formatting issues found" -ForegroundColor $Red }
    
    # Run tests
    Write-Host "🧪 Running Node.js tests..." -ForegroundColor $Yellow
    npm test 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Node.js tests failed" -ForegroundColor $Red }
    
    Write-Host "✅ Node.js tests completed" -ForegroundColor $Green
}

# Function to run E2E tests
function Run-E2ETests {
    Write-Host "📝 Running E2E tests..." -ForegroundColor $Yellow
    
    # Install Playwright
    pip install playwright
    npx playwright install --with-deps
    
    # Start application
    Write-Host "🚀 Starting application for E2E tests..." -ForegroundColor $Yellow
    $AppProcess = Start-Process -FilePath "python" -ArgumentList "-m", "streamlit", "run", "coolbits_web_app.py", "--server.port=8501" -PassThru
    
    # Wait for app to start
    Start-Sleep -Seconds 10
    
    # Run E2E tests
    Write-Host "🧪 Running E2E tests..." -ForegroundColor $Yellow
    pytest tests/e2e/ --browser chromium --browser webkit 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ E2E tests failed" -ForegroundColor $Red }
    
    # Stop application
    Stop-Process -Id $AppProcess.Id -Force
    
    Write-Host "✅ E2E tests completed" -ForegroundColor $Green
}

# Function to run Docker tests
function Run-DockerTests {
    Write-Host "📝 Running Docker tests..." -ForegroundColor $Yellow
    
    # Build Docker image
    Write-Host "🔨 Building Docker image..." -ForegroundColor $Yellow
    docker build -t coolbits-test:latest . 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Docker build failed" -ForegroundColor $Red }
    
    # Test Docker image
    Write-Host "🧪 Testing Docker image..." -ForegroundColor $Yellow
    docker run --rm -d --name coolbits-test -p 8501:8501 coolbits-test:latest 
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Docker run failed" -ForegroundColor $Red }
    
    # Wait for container to start
    Start-Sleep -Seconds 30
    
    # Test health endpoint
    try {
        Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -UseBasicParsing
        Write-Host "✅ Health check passed" -ForegroundColor $Green
    } catch {
        Write-Host "❌ Health check failed" -ForegroundColor $Red
    }
    
    # Stop container
    docker stop coolbits-test
    
    Write-Host "✅ Docker tests completed" -ForegroundColor $Green
}

# Main execution
switch ($TestType) {
    "python" { Run-PythonTests }
    "node" { Run-NodeTests }
    "e2e" { Run-E2ETests }
    "docker" { Run-DockerTests }
    "all" { 
        Run-PythonTests
        Run-NodeTests
        Run-E2ETests
        Run-DockerTests
    }
}

Write-Host "🎉 Test suite completed!" -ForegroundColor $Green
