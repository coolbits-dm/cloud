#!/bin/bash
# CoolBits.ai Backup Script (Linux/macOS)
# =======================================

set -e

# Configuration
BACKUP_BUCKET="${BACKUP_BUCKET:-coolbits-backup-prod}"
PROJECT_ID="${PROJECT_ID:-coolbits-og-bridge}"
REGION="${REGION:-europe-west1}"

# Set non-interactive environment
export CI=1
export NO_COLOR=1
export GCLOUD_SUPPRESS_PROMPTS=1
export CLOUDSDK_CORE_DISABLE_PROMPTS=1

echo "🔄 CoolBits.ai Backup Process Starting..."
echo "========================================"
echo "Bucket: $BACKUP_BUCKET"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Create backup directory
BACKUP_DIR="backup_temp_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    rm -rf "$BACKUP_DIR"
    rm -f "$BACKUP_FILE"
    rm -f "$BACKUP_FILE.sha256"
}
trap cleanup EXIT

# 1. Backup configuration files
echo "📁 Backing up configuration files..."
CONFIG_ITEMS=(
    "config/"
    "data/governance/"
    "feature-flags.json"
    ".runtime.json"
    "package.json"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
)

for item in "${CONFIG_ITEMS[@]}"; do
    if [ -e "$item" ]; then
        cp -r "$item" "$BACKUP_DIR/"
        echo "  ✅ $item"
    else
        echo "  ⚠️  $item (not found)"
    fi
done

# 2. Backup SBOM and security artifacts
echo ""
echo "🔐 Backing up security artifacts..."
SECURITY_ITEMS=(
    "sbom/"
    "cosign.key"
    "cosign.pub"
    "slsa-provenance.json"
)

for item in "${SECURITY_ITEMS[@]}"; do
    if [ -e "$item" ]; then
        cp -r "$item" "$BACKUP_DIR/"
        echo "  ✅ $item"
    else
        echo "  ⚠️  $item (not found)"
    fi
done

# 3. Backup data files
echo ""
echo "📊 Backing up data files..."
DATA_ITEMS=(
    "data/roadmap.json"
    "logs/boot-health.log"
    ".server.lock"
)

for item in "${DATA_ITEMS[@]}"; do
    if [ -e "$item" ]; then
        cp -r "$item" "$BACKUP_DIR/"
        echo "  ✅ $item"
    else
        echo "  ⚠️  $item (not found)"
    fi
done

# 4. Create backup metadata
echo ""
echo "📝 Creating backup metadata..."
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
FILES_COUNT=$(find "$BACKUP_DIR" -type f | wc -l)
TOTAL_SIZE=$(du -sb "$BACKUP_DIR" | cut -f1)

cat > "$BACKUP_DIR/backup_metadata.json" << EOF
{
  "timestamp": "$TIMESTAMP",
  "version": "1.0.0",
  "project_id": "$PROJECT_ID",
  "region": "$REGION",
  "backup_scope": "full",
  "data_classification": "confidential",
  "retention_days": 365,
  "restore_priority": "P0",
  "files_count": $FILES_COUNT,
  "total_size_bytes": $TOTAL_SIZE
}
EOF
echo "  ✅ backup_metadata.json created"

# 5. Create compressed backup
echo ""
echo "🗜️  Creating compressed backup..."
BACKUP_FILE="coolbits-backup-$(date -u +%Y%m%dT%H%M%SZ).tar.gz"

tar -czf "$BACKUP_FILE" -C "$BACKUP_DIR" .
echo "  ✅ $BACKUP_FILE created"

# 6. Calculate checksum
echo ""
echo "🔍 Calculating checksum..."
CHECKSUM=$(sha256sum "$BACKUP_FILE" | cut -d' ' -f1)
echo "$CHECKSUM" > "$BACKUP_FILE.sha256"
echo "  ✅ SHA256: $CHECKSUM"

# 7. Upload to GCS
echo ""
echo "☁️  Uploading to Google Cloud Storage..."

# Set project
gcloud config set project "$PROJECT_ID" --quiet

# Upload backup file
gsutil cp "$BACKUP_FILE" "gs://$BACKUP_BUCKET/$BACKUP_FILE"
echo "  ✅ $BACKUP_FILE uploaded"

# Upload checksum
gsutil cp "$BACKUP_FILE.sha256" "gs://$BACKUP_BUCKET/$BACKUP_FILE.sha256"
echo "  ✅ $BACKUP_FILE.sha256 uploaded"

# 8. Verify upload
echo ""
echo "🔍 Verifying upload..."
REMOTE_CHECKSUM=$(gsutil cat "gs://$BACKUP_BUCKET/$BACKUP_FILE.sha256")
if [ "$REMOTE_CHECKSUM" = "$CHECKSUM" ]; then
    echo "  ✅ Checksum verification passed"
else
    echo "  ❌ Checksum verification failed"
    echo "  Expected: $CHECKSUM"
    echo "  Got: $REMOTE_CHECKSUM"
    exit 1
fi

# 9. Log success
echo ""
echo "✅ Backup completed successfully!"
echo "📁 Backup file: gs://$BACKUP_BUCKET/$BACKUP_FILE"
echo "🔐 Checksum: $CHECKSUM"
echo "📊 Size: $(du -h "$BACKUP_FILE" | cut -f1)"

# Return backup file name for monitoring
echo "$BACKUP_FILE"
