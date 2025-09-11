@echo off
REM CoolBits.ai Weekly Maintenance Script

echo 🚀 Running weekly maintenance...

REM Run weekly validation
python weekly_validator.py --run

REM Test canary deployment
python test_canary_deployment.py

REM Test security
python test_rbac_hmac.py

REM Test dashboard
python test_dashboard_real_api.py

echo ✅ Weekly maintenance completed
pause
