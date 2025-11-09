#!/bin/bash
# oGPT-Bridge Cron Wrapper Script
# COOL BITS SRL 🏢 - Internal Secret
# CEO: Andrei
# AI Assistant: oCursor

# Script configuration
SCRIPT_NAME="ogpt_bridge_cron_wrapper.sh"
BRIDGE_SCRIPT="ogpt_bridge_complete_system.py"
PROJECT_DIR="/c/Users/andre/Desktop/coolbits"
LOG_DIR="$PROJECT_DIR/ogpt_bridge_logs"
PID_FILE="$PROJECT_DIR/ogpt_bridge.pid"

# Create log directory
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/bridge_cron.log"
}

# Function to check if bridge is running
is_bridge_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start bridge
start_bridge() {
    log_message "🌉 Starting oGPT-Bridge System..."
    
    cd "$PROJECT_DIR" || exit 1
    
    # Activate virtual environment if it exists
    if [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
        log_message "✅ Virtual environment activated"
    fi
    
    # Start bridge system in background
    nohup python "$BRIDGE_SCRIPT" > "$LOG_DIR/bridge_output.log" 2>&1 &
    BRIDGE_PID=$!
    
    # Save PID
    echo "$BRIDGE_PID" > "$PID_FILE"
    
    log_message "✅ oGPT-Bridge started with PID: $BRIDGE_PID"
    log_message "📁 Logs: $LOG_DIR/bridge_output.log"
    log_message "📄 PID file: $PID_FILE"
}

# Function to stop bridge
stop_bridge() {
    log_message "🛑 Stopping oGPT-Bridge System..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            log_message "✅ oGPT-Bridge stopped (PID: $PID)"
        else
            log_message "⚠️ Bridge process not found"
        fi
        rm -f "$PID_FILE"
    else
        log_message "⚠️ PID file not found"
    fi
}

# Function to restart bridge
restart_bridge() {
    log_message "🔄 Restarting oGPT-Bridge System..."
    stop_bridge
    sleep 2
    start_bridge
}

# Function to show status
show_status() {
    log_message "📊 oGPT-Bridge Status Check..."
    
    if is_bridge_running; then
        PID=$(cat "$PID_FILE")
        log_message "✅ oGPT-Bridge is RUNNING (PID: $PID)"
        
        # Show recent logs
        if [ -f "$LOG_DIR/bridge_output.log" ]; then
            log_message "📋 Recent logs (last 5 lines):"
            tail -5 "$LOG_DIR/bridge_output.log" | while read line; do
                log_message "   $line"
            done
        fi
    else
        log_message "❌ oGPT-Bridge is NOT RUNNING"
    fi
    
    # Show log files
    log_message "📁 Log files:"
    ls -la "$LOG_DIR/" | while read line; do
        log_message "   $line"
    done
}

# Function to show help
show_help() {
    echo "🌉 oGPT-Bridge Cron Wrapper Script"
    echo "🏢 COOL BITS SRL 🏢 - CEO: Andrei"
    echo "🤖 AI Assistant: oCursor"
    echo "🔒 Classification: Internal Secret - CoolBits.ai 🏢 Members Only"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|help}"
    echo ""
    echo "Commands:"
    echo "  start   - Start oGPT-Bridge system"
    echo "  stop    - Stop oGPT-Bridge system"
    echo "  restart - Restart oGPT-Bridge system"
    echo "  status  - Show bridge status and logs"
    echo "  help    - Show this help message"
    echo ""
    echo "Cron job example:"
    echo "  */30 * * * * $0 status"
    echo ""
    echo "Files:"
    echo "  Bridge Script: $PROJECT_DIR/$BRIDGE_SCRIPT"
    echo "  Log Directory: $LOG_DIR"
    echo "  PID File: $PID_FILE"
}

# Main script logic
case "$1" in
    start)
        if is_bridge_running; then
            log_message "⚠️ oGPT-Bridge is already running"
        else
            start_bridge
        fi
        ;;
    stop)
        stop_bridge
        ;;
    restart)
        restart_bridge
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Invalid command: $1"
        show_help
        exit 1
        ;;
esac

exit 0
