@echo off
echo.
echo ========================================
echo   CoolBits.ai God Mode Admin Panel
echo   CEO: Andrei | coolbits.ai & cbLM.ai
echo ========================================
echo.
echo Starting CoolBits.ai Local Endpoint...
echo.

REM Start the server in background
start /B C:\Users\andre\AppData\Local\Programs\Python\Python311\python.exe andrei_local_endpoint.py

echo Waiting for server to start...
timeout /t 5 /nobreak > nul

echo.
echo Opening God Mode Admin Panel...
start http://localhost:8081/god-mode

echo.
echo Opening Standard Admin Panel...
start http://localhost:8081/admin

echo.
echo Opening Dashboard...
start http://localhost:8081/dashboard

echo.
echo ========================================
echo   Available Endpoints:
echo ========================================
echo.
echo God Mode Admin Panel: http://localhost:8081/god-mode
echo Standard Admin Panel: http://localhost:8081/admin
echo Interactive Dashboard: http://localhost:8081/dashboard
echo.
echo API Endpoints:
echo - Health Check: http://localhost:8081/health
echo - AI Chat: http://localhost:8081/ai/chat
echo - Team Status: http://localhost:8081/team
echo - GPU Status: http://localhost:8081/gpu/status
echo - GPU Processing: http://localhost:8081/gpu/process
echo.
echo ========================================
echo   All interfaces opened in browser!
echo   Press any key to exit...
echo ========================================
pause > nul
