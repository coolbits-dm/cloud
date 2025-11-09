#!/bin/bash
# CoolBits.ai Restore Test Script
# ===============================

set -e

BACKUP_BUCKET="${BACKUP_BUCKET:-coolbits-backup-prod}"
PROJECT_ID="${PROJECT_ID:-coolbits-og-bridge}"
RESTORE_DIR="restore_test_$(date -u +%Y%m%dT%H%M%SZ)"

echo "🔄 CoolBits.ai Restore Test Starting..."
echo "======================================"
echo "Bucket: $BACKUP_BUCKET"
echo "Project: $PROJECT_ID"
echo "Restore Directory: $RESTORE_DIR"
echo ""

# Set non-interactive environment
export CI=1
export NO_COLOR=1
export GCLOUD_SUPPRESS_PROMPTS=1
export CLOUDSDK_CORE_DISABLE_PROMPTS=1

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up restore test..."
    if [ -d "$RESTORE_DIR" ]; then
        rm -rf "$RESTORE_DIR"
    fi
    if [ -f "docker-compose.restore.yml" ]; then
        rm -f "docker-compose.restore.yml"
    fi
    if [ -f "restore_test.log" ]; then
        rm -f "restore_test.log"
    fi
}
trap cleanup EXIT

# 1. Set project
echo "🔧 Setting up GCP project..."
gcloud config set project "$PROJECT_ID" --quiet

# 2. Get latest backup
echo "📦 Finding latest backup..."
LATEST_BACKUP=$(gsutil ls "gs://$BACKUP_BUCKET/coolbits-backup-*.tar.gz" 2>/dev/null | sort | tail -1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backups found in bucket"
    exit 1
fi

BACKUP_NAME=$(basename "$LATEST_BACKUP")
echo "  📁 Latest backup: $BACKUP_NAME"

# 3. Download backup
echo "📥 Downloading backup..."
gsutil cp "$LATEST_BACKUP" "$BACKUP_NAME"
echo "  ✅ Backup downloaded"

# 4. Verify checksum
echo "🔍 Verifying backup integrity..."
CHECKSUM_FILE="${BACKUP_NAME}.sha256"
gsutil cp "gs://$BACKUP_BUCKET/$CHECKSUM_FILE" "$CHECKSUM_FILE"

LOCAL_CHECKSUM=$(sha256sum "$BACKUP_NAME" | cut -d' ' -f1)
REMOTE_CHECKSUM=$(cat "$CHECKSUM_FILE")

if [ "$LOCAL_CHECKSUM" = "$REMOTE_CHECKSUM" ]; then
    echo "  ✅ Checksum verification passed"
else
    echo "  ❌ Checksum verification failed"
    exit 1
fi

# 5. Extract backup
echo "📦 Extracting backup..."
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_NAME" -C "$RESTORE_DIR"
echo "  ✅ Backup extracted to $RESTORE_DIR"

# 6. Verify extracted contents
echo "📋 Verifying extracted contents..."
REQUIRED_FILES=(
    "backup_metadata.json"
    "package.json"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
)

ALL_FILES_PRESENT=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$RESTORE_DIR/$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        ALL_FILES_PRESENT=false
    fi
done

if [ "$ALL_FILES_PRESENT" = false ]; then
    echo "❌ Some required files missing from backup"
    exit 1
fi

# 7. Create restore environment
echo "🐳 Setting up restore environment..."
cd "$RESTORE_DIR"

# Create restore-specific docker-compose
cat > docker-compose.restore.yml << 'EOF'
version: '3.8'

services:
  coolbits-restore:
    build: .
    container_name: coolbits-restore-test
    ports:
      - "8081:8080"
      - "8101:8100"
    environment:
      - CI=1
      - NO_COLOR=1
      - GCLOUD_SUPPRESS_PROMPTS=1
      - CLOUDSDK_CORE_DISABLE_PROMPTS=1
      - RESTORE_MODE=true
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    labels:
      - "com.coolbits.service=coolbits-restore-test"
      - "com.coolbits.version=restore-test"
EOF

# 8. Build and start restore environment
echo "🔨 Building restore environment..."
docker-compose -f docker-compose.restore.yml build --no-cache
echo "  ✅ Build completed"

echo "🚀 Starting restore environment..."
docker-compose -f docker-compose.restore.yml up -d
echo "  ✅ Services started"

# 9. Wait for services to be healthy
echo "⏳ Waiting for services to become healthy..."
MAX_ATTEMPTS=20
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "  🔍 Attempt $ATTEMPT/$MAX_ATTEMPTS..."
    
    if curl -f http://localhost:8081/api/health >/dev/null 2>&1; then
        echo "  ✅ Services are healthy"
        break
    fi
    
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "  ❌ Services failed to become healthy"
        echo "  📋 Container logs:"
        docker-compose -f docker-compose.restore.yml logs --tail=50
        exit 1
    fi
    
    sleep 10
done

# 10. Run restore verification
echo "🔍 Running restore verification..."
cd ..

# Create verification script
cat > restore/verify_post_restore.sh << 'EOF'
#!/bin/bash
set -e

echo "🔍 CoolBits.ai Post-Restore Verification"
echo "========================================"

# Test endpoints
ENDPOINTS=(
    "http://localhost:8081/api/health"
    "http://localhost:8081/api/services/status"
    "http://localhost:8101/health"
)

ALL_ENDPOINTS_OK=true
for endpoint in "${ENDPOINTS[@]}"; do
    echo "  🔍 Testing $endpoint..."
    if curl -f "$endpoint" >/dev/null 2>&1; then
        echo "    ✅ OK"
    else
        echo "    ❌ FAILED"
        ALL_ENDPOINTS_OK=false
    fi
done

if [ "$ALL_ENDPOINTS_OK" = true ]; then
    echo "✅ All endpoints responding"
else
    echo "❌ Some endpoints failed"
    exit 1
fi

# Check service versions
echo "📋 Checking service versions..."
HEALTH_RESPONSE=$(curl -s http://localhost:8081/api/health)
VERSION=$(echo "$HEALTH_RESPONSE" | jq -r '.version // "unknown"')
echo "  📦 Version: $VERSION"

# Check feature flags
echo "🚩 Checking feature flags..."
FEATURE_FLAGS_RESPONSE=$(curl -s http://localhost:8081/api/feature-flags)
ENABLED_FLAGS=$(echo "$FEATURE_FLAGS_RESPONSE" | jq -r '.enabled | keys | length')
echo "  🚩 Enabled flags: $ENABLED_FLAGS"

# Check runtime config
echo "⚙️  Checking runtime configuration..."
if [ -f ".runtime.json" ]; then
    RUNTIME_CONFIG=$(cat .runtime.json)
    echo "  ✅ Runtime config restored"
    echo "  📊 Config: $RUNTIME_CONFIG"
else
    echo "  ⚠️  Runtime config not found"
fi

echo "✅ Post-restore verification completed successfully!"
EOF

chmod +x restore/verify_post_restore.sh

# Run verification
echo "🧪 Running post-restore verification..."
./restore/verify_post_restore.sh

# 11. Test critical functionality
echo "🔧 Testing critical functionality..."

# Test health endpoint
echo "  🏥 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8081/api/health)
if echo "$HEALTH_RESPONSE" | jq -e '.status' >/dev/null 2>&1; then
    echo "    ✅ Health endpoint working"
else
    echo "    ❌ Health endpoint failed"
    exit 1
fi

# Test services status
echo "  📊 Testing services status..."
SERVICES_RESPONSE=$(curl -s http://localhost:8081/api/services/status)
if echo "$SERVICES_RESPONSE" | jq -e '.services' >/dev/null 2>&1; then
    echo "    ✅ Services status working"
else
    echo "    ❌ Services status failed"
    exit 1
fi

# Test bridge health
echo "  🌉 Testing bridge health..."
BRIDGE_RESPONSE=$(curl -s http://localhost:8101/health)
if echo "$BRIDGE_RESPONSE" | jq -e '.status' >/dev/null 2>&1; then
    echo "    ✅ Bridge health working"
else
    echo "    ❌ Bridge health failed"
    exit 1
fi

# 12. Stop restore environment
echo "🛑 Stopping restore environment..."
docker-compose -f docker-compose.restore.yml down
echo "  ✅ Services stopped"

# 13. Log success
echo ""
echo "✅ Restore test completed successfully!"
echo "📁 Restored from: $LATEST_BACKUP"
echo "🔐 Checksum: $REMOTE_CHECKSUM"
echo "⏰ Test duration: $(date)"
echo ""
echo "🎯 Restore test results:"
echo "  ✅ Backup download and verification"
echo "  ✅ Content extraction and validation"
echo "  ✅ Service startup and health checks"
echo "  ✅ Endpoint functionality testing"
echo "  ✅ Critical functionality verification"
echo ""
echo "🚀 System is ready for production restore!"
