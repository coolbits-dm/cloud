@echo off
echo 🚀 CoolBits.ai - Starting All Services
echo ======================================
echo Company: COOL BITS SRL
echo CEO: Andrei
echo Meta Owner: Andrei Cip
echo Meta App ID: 825511663344104
echo ======================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo 🌐 Starting Main Dashboard (Port 8080)...
start "CoolBits Main Dashboard" cmd /k "python coolbits_main_dashboard.py"

timeout /t 3 /nobreak >nul

echo 🚀 Starting Meta Platform (Port 3003)...
start "Meta Platform" cmd /k "python meta_platform_server.py"

timeout /t 3 /nobreak >nul

echo 📊 Opening Main Dashboard in browser...
start http://localhost:8080

echo.
echo ✅ All services started!
echo.
echo 🌐 Main Dashboard: http://localhost:8080
echo 🚀 Meta Platform: http://localhost:3003
echo.
echo 📋 Services running:
echo   • Main Dashboard (Port 8080)
echo   • Meta Platform (Port 3003)
echo.
echo Press any key to exit...
pause >nul
