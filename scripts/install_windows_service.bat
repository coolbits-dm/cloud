@echo off
REM CoolBits.ai Windows Service Installation

echo Installing CoolBits.ai Maintenance Service...

REM Install Python service
pip install pywin32

REM Install service
python coolbits_maintenance_service.py install

REM Start service
python coolbits_maintenance_service.py start

echo ✅ Windows service installed and started
pause
