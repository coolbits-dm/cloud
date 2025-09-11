#!/bin/bash
# CoolBits.ai Daily Maintenance Script

echo "🔧 Running daily maintenance..."

# Run CI checks
python -m black --check .
python -m flake8 . --count

# Check health endpoints
python -c "import requests; print('Health:', requests.get('http://localhost:8501/api/health').status_code)"

# Clean up old logs
find logs/ -name "*.log" -mtime +30 -delete

echo "✅ Daily maintenance completed"
