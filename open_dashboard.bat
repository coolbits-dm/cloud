@echo off
echo Opening CoolBits.ai Dashboard...
echo.
echo Dashboard: http://localhost:8081/dashboard
echo Admin Panel: http://localhost:8081/admin
echo.
start http://localhost:8081/dashboard
timeout /t 2 /nobreak >nul
start http://localhost:8081/admin
echo.
echo Both interfaces opened in your default browser!
echo Press any key to exit...
pause >nul
