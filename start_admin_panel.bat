@echo off
REM CoolBits.ai Admin Panel Launcher
REM Simple batch file to start the admin panel

echo.
echo ============================================================
echo   CoolBits.ai Internal Admin Panel Launcher
echo ============================================================
echo.
echo Starting local development server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Starting HTML file directly...
    echo.
    echo Opening admin panel in default browser...
    start "" "coolbits_admin_panel.html"
    echo.
    echo Admin Panel opened in browser!
    echo URL: file:///%CD%/coolbits_admin_panel.html
    echo.
    pause
    exit /b
)

REM Start Python server
echo Starting HTTP server on localhost:8080...
echo.
python start_admin_panel.py

pause
