#!/usr/bin/env powershell
# 🚀 CoolBits.ai Local RAG System - Setup Script
# GPU-accelerated RAG system setup for RTX 2060

Write-Host "🚀 Setting up CoolBits.ai Local RAG System" -ForegroundColor Red
Write-Host "GPU-accelerated RAG with RTX 2060 processing" -ForegroundColor Green
Write-Host ""

# Check Python installation
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Cyan
    exit 1
}

# Check CUDA installation
Write-Host "🎮 Checking CUDA installation..." -ForegroundColor Yellow
try {
    $cudaVersion = nvcc --version 2>&1
    if ($cudaVersion -match "release") {
        Write-Host "✅ CUDA found: $($cudaVersion.Split("`n")[3])" -ForegroundColor Green
    } else {
        Write-Host "⚠️ CUDA not found - will use CPU fallback" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ CUDA not found - will use CPU fallback" -ForegroundColor Yellow
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "rag_env") {
    Write-Host "⚠️ Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv rag_env
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\rag_env\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️ Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "📥 Installing RAG system requirements..." -ForegroundColor Yellow
pip install -r requirements_rag.txt

# Install PyTorch with CUDA support (if CUDA available)
Write-Host "🔥 Installing PyTorch with CUDA support..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$directories = @(
    "rag_indexes",
    "test_documents", 
    "logs",
    "data"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

# Test GPU availability
Write-Host "🧪 Testing GPU availability..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}' if torch.cuda.is_available() else 'CUDA not available'); print(f'GPU name: {torch.cuda.get_device_name(0)}' if torch.cuda.is_available() else 'No GPU'); print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB' if torch.cuda.is_available() else 'No GPU memory')"

# Create startup script
Write-Host "📝 Creating startup script..." -ForegroundColor Yellow
$startupScript = @"
#!/usr/bin/env powershell
# CoolBits.ai Local RAG System - Startup Script

Write-Host "🚀 Starting CoolBits.ai Local RAG System" -ForegroundColor Red
Write-Host "GPU-accelerated RAG with RTX 2060" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
& ".\rag_env\Scripts\Activate.ps1"

# Start RAG system
Write-Host "🔥 Starting RAG system on http://localhost:8080" -ForegroundColor Cyan
python local_rag_system.py
"@

Set-Content -Path "start_rag_system.ps1" -Value $startupScript
Write-Host "✅ Startup script created: start_rag_system.ps1" -ForegroundColor Green

# Create test script
Write-Host "🧪 Creating test script..." -ForegroundColor Yellow
$testScript = @"
#!/usr/bin/env powershell
# CoolBits.ai Local RAG System - Test Script

Write-Host "🧪 Running RAG System Tests" -ForegroundColor Red
Write-Host ""

# Activate virtual environment
& ".\rag_env\Scripts\Activate.ps1"

# Run tests
python test_rag_system.py
"@

Set-Content -Path "test_rag_system.ps1" -Value $testScript
Write-Host "✅ Test script created: test_rag_system.ps1" -ForegroundColor Green

# Final summary
Write-Host ""
Write-Host "🎉 SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 50
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Run tests: .\test_rag_system.ps1" -ForegroundColor White
Write-Host "2. Start system: .\start_rag_system.ps1" -ForegroundColor White
Write-Host "3. Access API: http://localhost:8080" -ForegroundColor White
Write-Host "4. View docs: http://localhost:8080/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔗 API Endpoints:" -ForegroundColor Cyan
Write-Host "- Health: GET /health" -ForegroundColor White
Write-Host "- Upload: POST /documents/upload" -ForegroundColor White
Write-Host "- Search: POST /search" -ForegroundColor White
Write-Host "- GPU Status: GET /gpu/status" -ForegroundColor White
Write-Host ""
Write-Host "🎮 GPU Processing: RTX 2060 (6GB VRAM)" -ForegroundColor Green
Write-Host "📊 Vector DB: FAISS + ChromaDB" -ForegroundColor Green
Write-Host "🔤 Embeddings: sentence-transformers" -ForegroundColor Green
Write-Host "=" * 50
