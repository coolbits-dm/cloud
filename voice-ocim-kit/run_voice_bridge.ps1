# Voice OCIM Bridge Startup Script
# SC COOL BITS SRL - Voice to OCIM Bridge

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🎤 VOICE OCIM BRIDGE STARTUP" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Company: SC COOL BITS SRL" -ForegroundColor White
Write-Host "CEO: Andrei" -ForegroundColor White
Write-Host "Classification: Internal Secret - CoolBits.ai Members Only" -ForegroundColor Red
Write-Host "=" * 80 -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found. Please install pip" -ForegroundColor Red
    exit 1
}

# Install requirements
Write-Host "`n📦 Installing requirements..." -ForegroundColor Yellow
try {
    python -m pip install -r requirements.txt
    Write-Host "✅ Requirements installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install requirements" -ForegroundColor Red
    exit 1
}

# Set environment variables
Write-Host "`n🔧 Setting environment variables..." -ForegroundColor Yellow
$env:PYTHONUNBUFFERED = "1"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:OCIM_STREAM = "opipe.ocim"
$env:TARGET_AGENT = "opyc"
$env:BRIDGE_PORT = "7071"

Write-Host "✅ Environment variables set" -ForegroundColor Green

# Check Redis connection (optional)
Write-Host "`n🔍 Checking Redis connection..." -ForegroundColor Yellow
try {
    $redisTest = redis-cli ping 2>&1
    if ($redisTest -eq "PONG") {
        Write-Host "✅ Redis is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Redis not running - will use mock mode" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Redis not available - will use mock mode" -ForegroundColor Yellow
}

# Start the bridge
Write-Host "`n🚀 Starting OCIM Bridge..." -ForegroundColor Yellow
Write-Host "Bridge will be available at: http://localhost:7071" -ForegroundColor Cyan
Write-Host "Health check: http://localhost:7071/health" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan

try {
    python ocim_bridge.py
} catch {
    Write-Host "`n❌ Bridge stopped with error" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n🛑 Bridge stopped" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
