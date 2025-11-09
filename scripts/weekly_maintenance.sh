#!/bin/bash
# CoolBits.ai Weekly Maintenance Script

echo "🚀 Running weekly maintenance..."

# Run weekly validation
python weekly_validator.py --run

# Test canary deployment
python test_canary_deployment.py

# Test security
python test_rbac_hmac.py

# Test dashboard
python test_dashboard_real_api.py

echo "✅ Weekly maintenance completed"
