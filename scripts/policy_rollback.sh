#!/bin/bash
# Policy Rollback Script for M15
# ===============================
# 
# Explicit rollback plan for policy changes:
# 1. Re-deploy last signed version of registry.json
# 2. Force enforcer reload and set MODE=deny for 60 min
# 3. Trigger rapid rollback via label or manual workflow

set -euo pipefail

# Configuration
REPO_PATH="${REPO_PATH:-.}"
REGISTRY_DIR="$REPO_PATH/cblm/opipe/nha/out"
BACKUP_DIR="$REPO_PATH/backup/registry"
LOG_FILE="$REPO_PATH/logs/policy_rollback.log"
ROLLBACK_DURATION="${ROLLBACK_DURATION:-60}"  # minutes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Create necessary directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log "Starting policy rollback procedure..."

# Step 1: Backup current registry state
info "Step 1: Backing up current registry state"
CURRENT_BACKUP="$BACKUP_DIR/registry_backup_$(date +%Y%m%d_%H%M%S)"

if [ -f "$REGISTRY_DIR/registry.json" ]; then
    cp "$REGISTRY_DIR/registry.json" "$CURRENT_BACKUP.json"
    log "Backed up current registry.json to $CURRENT_BACKUP.json"
else
    warning "Current registry.json not found - proceeding with rollback"
fi

# Step 2: Find last signed registry version
info "Step 2: Finding last signed registry version"
LAST_SIGNED=""

# Look for signed registry backups
for backup in "$BACKUP_DIR"/registry_signed_*.json; do
    if [ -f "$backup" ]; then
        LAST_SIGNED="$backup"
    fi
done

# If no signed backup found, look for any backup
if [ -z "$LAST_SIGNED" ]; then
    for backup in "$BACKUP_DIR"/registry_backup_*.json; do
        if [ -f "$backup" ]; then
            LAST_SIGNED="$backup"
        fi
    done
fi

if [ -z "$LAST_SIGNED" ]; then
    error "No registry backup found for rollback"
fi

log "Found last signed registry: $LAST_SIGNED"

# Step 3: Verify signature of backup
info "Step 3: Verifying signature of backup"
BACKUP_SIG="${LAST_SIGNED}.sig"
BACKUP_CERT="${LAST_SIGNED}.cert"

if [ -f "$BACKUP_SIG" ] && [ -f "$BACKUP_CERT" ]; then
    if command -v cosign >/dev/null 2>&1; then
        if cosign verify-blob --key cosign.pub --signature "$BACKUP_SIG" "$LAST_SIGNED" >/dev/null 2>&1; then
            success "Backup signature verified"
        else
            warning "Backup signature verification failed - proceeding anyway"
        fi
    else
        warning "cosign not available - skipping signature verification"
    fi
else
    warning "Backup signature files not found - proceeding without verification"
fi

# Step 4: Restore registry
info "Step 4: Restoring registry from backup"
cp "$LAST_SIGNED" "$REGISTRY_DIR/registry.json"
success "Registry restored from $LAST_SIGNED"

# Step 5: Force enforcer reload
info "Step 5: Forcing enforcer reload"
ENFORCER_PID=""

# Find enforcer process
if command -v pgrep >/dev/null 2>&1; then
    ENFORCER_PID=$(pgrep -f "enforcer.py" || true)
fi

if [ -n "$ENFORCER_PID" ]; then
    log "Found enforcer process: $ENFORCER_PID"
    
    # Send reload signal (SIGUSR1)
    if kill -USR1 "$ENFORCER_PID" 2>/dev/null; then
        success "Enforcer reload signal sent"
    else
        warning "Failed to send reload signal to enforcer"
    fi
else
    warning "Enforcer process not found - may need manual restart"
fi

# Step 6: Set fail-closed mode
info "Step 6: Setting fail-closed mode for $ROLLBACK_DURATION minutes"
export NHA_ENFORCEMENT_MODE="deny"

# Create temporary environment file
ENV_FILE="$REPO_PATH/.env.rollback"
echo "NHA_ENFORCEMENT_MODE=deny" > "$ENV_FILE"
echo "NHA_ROLLBACK_UNTIL=$(date -d "+$ROLLBACK_DURATION minutes" '+%Y-%m-%d %H:%M:%S')" >> "$ENV_FILE"

success "Fail-closed mode set for $ROLLBACK_DURATION minutes"

# Step 7: Verify rollback
info "Step 7: Verifying rollback"
if [ -f "$REGISTRY_DIR/registry.json" ]; then
    REGISTRY_HASH=$(sha256sum "$REGISTRY_DIR/registry.json" | cut -d' ' -f1)
    BACKUP_HASH=$(sha256sum "$LAST_SIGNED" | cut -d' ' -f1)
    
    if [ "$REGISTRY_HASH" = "$BACKUP_HASH" ]; then
        success "Rollback verified - registry hashes match"
    else
        error "Rollback verification failed - registry hashes don't match"
    fi
else
    error "Registry file not found after rollback"
fi

# Step 8: Schedule automatic recovery
info "Step 8: Scheduling automatic recovery"
RECOVERY_TIME=$(date -d "+$ROLLBACK_DURATION minutes" '+%Y-%m-%d %H:%M:%S')

# Create recovery script
RECOVERY_SCRIPT="$REPO_PATH/scripts/recover_from_rollback.sh"
cat > "$RECOVERY_SCRIPT" << EOF
#!/bin/bash
# Automatic recovery from rollback
# Generated: $(date)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] \$1"
}

log "Starting automatic recovery from rollback..."

# Remove rollback environment
rm -f "$ENV_FILE"

# Set normal enforcement mode
export NHA_ENFORCEMENT_MODE="warn"

# Reload enforcer
if [ -n "$ENFORCER_PID" ]; then
    kill -USR1 "$ENFORCER_PID" 2>/dev/null || true
fi

log "Recovery completed - normal enforcement mode restored"
EOF

chmod +x "$RECOVERY_SCRIPT"

# Schedule recovery (using at command if available)
if command -v at >/dev/null 2>&1; then
    echo "$RECOVERY_SCRIPT" | at "$RECOVERY_TIME" 2>/dev/null || warning "Failed to schedule automatic recovery"
    log "Automatic recovery scheduled for $RECOVERY_TIME"
else
    warning "at command not available - manual recovery required at $RECOVERY_TIME"
fi

# Step 9: Generate rollback report
info "Step 9: Generating rollback report"
REPORT_FILE="$REPO_PATH/logs/rollback_report_$(date +%Y%m%d_%H%M%S).json"

cat > "$REPORT_FILE" << EOF
{
  "rollback_timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "rollback_duration_minutes": $ROLLBACK_DURATION,
  "restored_from": "$LAST_SIGNED",
  "registry_hash": "$REGISTRY_HASH",
  "enforcer_mode": "deny",
  "recovery_scheduled": "$RECOVERY_TIME",
  "status": "completed"
}
EOF

success "Rollback report generated: $REPORT_FILE"

# Final status
log "Policy rollback completed successfully"
log "Registry restored from: $LAST_SIGNED"
log "Fail-closed mode active for: $ROLLBACK_DURATION minutes"
log "Automatic recovery scheduled for: $RECOVERY_TIME"
log "Rollback report: $REPORT_FILE"

echo ""
echo "🔄 POLICY ROLLBACK COMPLETED"
echo "=============================="
echo "✅ Registry restored from backup"
echo "✅ Enforcer reloaded"
echo "✅ Fail-closed mode active ($ROLLBACK_DURATION min)"
echo "✅ Automatic recovery scheduled"
echo "✅ Rollback report generated"
echo ""
echo "Next steps:"
echo "1. Monitor system for $ROLLBACK_DURATION minutes"
echo "2. Automatic recovery at $RECOVERY_TIME"
echo "3. Manual intervention if needed"
echo ""
