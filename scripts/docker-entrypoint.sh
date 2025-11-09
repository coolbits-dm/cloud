#!/bin/bash
# CoolBits.ai Docker Entrypoint
# =============================

set -e

echo "🚀 CoolBits.ai Docker Container Starting..."
echo "============================================="

# Set non-interactive environment
export CI=1
export NO_COLOR=1
export GCLOUD_SUPPRESS_PROMPTS=1
export CLOUDSDK_CORE_DISABLE_PROMPTS=1
export GIT_TERMINAL_PROMPT=0
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Wait for any initialization
sleep 2

# Start Bridge (FastAPI) in background
echo "🌉 Starting Bridge (FastAPI) on port 8100..."
python coolbits_main_bridge.py &
BRIDGE_PID=$!

# Wait for bridge to become healthy
echo "⏳ Waiting for bridge to become healthy..."
for i in {1..20}; do
    if curl -f http://localhost:8100/health >/dev/null 2>&1; then
        echo "✅ Bridge healthy after $i seconds"
        break
    fi
    sleep 1
    echo "⏳ Waiting... ($i/20)"
done

# Start Dashboard
echo "🌐 Starting Dashboard on port 8080..."
python coolbits_main_dashboard.py &
DASHBOARD_PID=$!

# Wait for dashboard to become healthy
echo "⏳ Waiting for dashboard to become healthy..."
for i in {1..15}; do
    if curl -f http://localhost:8080/api/health >/dev/null 2>&1; then
        echo "✅ Dashboard healthy after $i seconds"
        break
    fi
    sleep 1
    echo "⏳ Waiting... ($i/15)"
done

# Save runtime info
cat > .runtime.json << EOF
{
  "port": 8080,
  "bridge_port": 8100,
  "bridge_pid": $BRIDGE_PID,
  "dashboard_pid": $DASHBOARD_PID,
  "started_at": "$(date -u +%Y-%m-%d\ %H:%M:%S)",
  "autostart": true,
  "container": true
}
EOF

echo "✅ CoolBits.ai started successfully!"
echo "🌐 Dashboard: http://localhost:8080"
echo "🌉 Bridge: http://localhost:8100"
echo "🏥 Health: http://localhost:8080/api/health"

# Log to boot health log
echo "OK $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> logs/boot-health.log

# Keep container running and handle signals
trap 'echo "🛑 Shutting down..."; kill $BRIDGE_PID $DASHBOARD_PID; exit 0' SIGTERM SIGINT

# Wait for processes
wait $BRIDGE_PID $DASHBOARD_PID
