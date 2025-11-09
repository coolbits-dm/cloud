#!/bin/bash
# CoolBits.ai Monthly Maintenance Script

echo "🔑 Running monthly maintenance..."

# Rotate HMAC keys
python hmac_key_manager.py generate --description "Monthly rotation"

# Clean up expired keys
python hmac_key_manager.py cleanup

# Run full validation
python operational_checklist.py --all

# Update dependencies
pip list --outdated

echo "✅ Monthly maintenance completed"
