@echo off
REM CoolBits.ai RAG System Startup Script
REM CEO: Andrei - andrei@coolbits.ro
REM Managed by: oCursor (Local Development)

echo.
echo ========================================
echo   CoolBits.ai RAG System Startup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found! Please install Node.js first.
    pause
    exit /b 1
)

echo ✅ Node.js found

REM Check if AI Board is running
echo.
echo 🔍 Checking AI Board status...
curl -s http://localhost:8082/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AI Board not running! Starting AI Board...
    echo.
    start "CoolBits AI Board" cmd /k "node coolbits_ai_board_node.js"
    echo ⏳ Waiting for AI Board to start...
    timeout /t 5 /nobreak >nul
) else (
    echo ✅ AI Board is already running
)

REM Check AI Board again
curl -s http://localhost:8082/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AI Board failed to start! Please check manually.
    pause
    exit /b 1
)

echo ✅ AI Board is running on http://localhost:8082

REM Install Python dependencies if needed
echo.
echo 📦 Checking Python dependencies...
pip show google-cloud-aiplatform >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Google Cloud AI Platform...
    pip install google-cloud-aiplatform
)

pip show requests >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requests...
    pip install requests
)

pip show numpy >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing numpy...
    pip install numpy
)

echo ✅ Python dependencies ready

REM Set environment variables
echo.
echo 🔧 Setting up environment...
set PROJECT_ID=271190369805
set LOCATION=europe-west4
set INDEX_ID=357314890748133376

echo ✅ Environment configured

REM Test RAG system
echo.
echo 🧪 Testing RAG system...
python coolbits_rag_system.py
if %errorlevel% neq 0 (
    echo ❌ RAG system test failed!
    echo Please check your Google Cloud credentials and project settings.
    pause
    exit /b 1
)

echo ✅ RAG system test passed

REM Start RAG integration
echo.
echo 🔗 Starting RAG integration...
python integrate_rag_system.py
if %errorlevel% neq 0 (
    echo ❌ RAG integration failed!
    pause
    exit /b 1
)

echo ✅ RAG integration completed

REM Show available services
echo.
echo 🎯 CoolBits.ai Services Available:
echo ========================================
echo.
echo 🌐 AI Board: http://localhost:8082
echo 🎛️  AI Board Interface: http://localhost:8082/ai-board
echo 🧠 RAG System: Ready for queries
echo 📊 Admin Panel: Use coolbits_admin.py
echo.
echo 📋 Available Commands:
echo   • python coolbits_admin.py health
echo   • python coolbits_admin.py roles
echo   • python coolbits_admin.py report
echo   • python test_rag_system.py
echo.
echo 🚀 System Ready!
echo.
echo Press any key to exit...
pause >nul
