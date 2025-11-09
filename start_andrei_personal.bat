@echo off
echo.
echo ========================================
echo   CoolBits.ai - Andrei Personal Panel
echo   CEO: Andrei | coolbits.ai & cbLM.ai
echo ========================================
echo.

REM Kill any existing Python processes
taskkill /F /IM python.exe 2>nul

echo Starting CoolBits.ai Local Endpoint...
echo.

REM Start the server
start /B C:\Users\andre\AppData\Local\Programs\Python\Python311\python.exe andrei_local_endpoint.py

echo Waiting for server to start...
timeout /t 3 /nobreak > nul

echo.
echo Opening Personal Chat Panel...
start http://localhost:8081/andrei

echo.
echo Opening God Mode Admin Panel...
start http://localhost:8081/god-mode

echo.
echo ========================================
echo   Available Panels:
echo ========================================
echo.
echo Personal Chat: http://localhost:8081/andrei
echo God Mode Admin: http://localhost:8081/god-mode
echo Standard Admin: http://localhost:8081/admin
echo Dashboard: http://localhost:8081/dashboard
echo.
echo ========================================
echo   Server running! Press any key to exit...
echo ========================================
pause > nul
