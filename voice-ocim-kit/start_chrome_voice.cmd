@echo off
REM Voice OCIM Bridge Chrome Launcher
REM SC COOL BITS SRL - Voice to OCIM Bridge

echo ================================================================================
echo 🎤 VOICE OCIM BRIDGE - CHROME LAUNCHER
echo ================================================================================
echo Company: SC COOL BITS SRL
echo CEO: Andrei
echo Classification: Internal Secret - CoolBits.ai Members Only
echo ================================================================================

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Check if Chrome is available
where chrome >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Chrome not found in PATH
    echo Please install Google Chrome or add it to your PATH
    pause
    exit /b 1
)

REM Check if voice.html exists
if not exist "%SCRIPT_DIR%voice.html" (
    echo ❌ voice.html not found in %SCRIPT_DIR%
    pause
    exit /b 1
)

echo ✅ Chrome found
echo ✅ voice.html found
echo.

REM Launch Chrome with voice.html
echo 🚀 Launching Chrome with Voice Bridge...
echo URL: file:///%SCRIPT_DIR%voice.html
echo.

REM Convert backslashes to forward slashes for file URL
set "FILE_URL=%SCRIPT_DIR%voice.html"
set "FILE_URL=%FILE_URL:\=/%"

REM Launch Chrome
start "" chrome --new-window --disable-web-security --disable-features=VizDisplayCompositor --allow-running-insecure-content --disable-extensions --disable-plugins --disable-default-apps --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding --disable-field-trial-config --disable-back-forward-cache --enable-features=NetworkService,NetworkServiceLogging --force-device-scale-factor=1 --high-dpi-support=1 --user-data-dir="%TEMP%\chrome_voice_bridge" "file:///%FILE_URL%"

echo ✅ Chrome launched with Voice Bridge
echo.
echo 📋 Instructions:
echo 1. Allow microphone permission when prompted
echo 2. Click "Start Listening" button
echo 3. Speak your commands
echo 4. Watch messages being sent to @oPyC
echo.
echo 🔧 Bridge Status: http://localhost:7071/health
echo 📊 Bridge Stats: http://localhost:7071/stats
echo.
echo Press any key to exit...
pause >nul
