@echo off
REM CoolBits.ai Local Endpoint Launcher
REM Managed by oCopilot (Microsoft Integration) & oCursor (Local Development)
REM CEO: Andrei - andrei@coolbits.ro

echo.
echo ============================================================
echo   CoolBits.ai Local Team Endpoint Launcher
echo ============================================================
echo.
echo CEO: Andrei - andrei@coolbits.ro
echo Managed by: oCopilot ^& oCursor
echo Port: 8081
echo.

REM Check if Python is available
C:\Users\andre\AppData\Local\Programs\Python\Python311\python.exe --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    echo.
    pause
    exit /b 1
)

echo Python found. Checking dependencies...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    C:\Users\andre\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting CoolBits.ai Local Endpoint...
echo Admin Panel: http://localhost:8081/admin
echo Interactive Dashboard: http://localhost:8081/dashboard
echo Health Check: http://localhost:8081/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the endpoint
python andrei_local_endpoint.py

pause
