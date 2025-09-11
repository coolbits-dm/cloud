@echo off
REM CoolBits.ai Daily Maintenance Script

echo 🔧 Running daily maintenance...

REM Run CI checks
python -m black --check .
python -m flake8 . --count

REM Check health endpoints
python -c "import requests; print('Health:', requests.get('http://localhost:8501/api/health').status_code)"

REM Clean up old logs
forfiles /p logs /s /m *.log /d -30 /c "cmd /c del @path"

echo ✅ Daily maintenance completed
pause
