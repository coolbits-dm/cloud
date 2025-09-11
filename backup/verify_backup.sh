#!/bin/bash
# CoolBits.ai Backup Verification Script
# =====================================

set -e

BACKUP_BUCKET="${BACKUP_BUCKET:-coolbits-backup-prod}"
PROJECT_ID="${PROJECT_ID:-coolbits-og-bridge}"

echo "🔍 CoolBits.ai Backup Verification"
echo "=================================="
echo "Bucket: $BACKUP_BUCKET"
echo "Project: $PROJECT_ID"
echo ""

# Set project
gcloud config set project "$PROJECT_ID" --quiet

# 1. Check if bucket exists
echo "📦 Checking backup bucket..."
if gsutil ls "gs://$BACKUP_BUCKET" >/dev/null 2>&1; then
    echo "  ✅ Bucket exists"
else
    echo "  ❌ Bucket does not exist"
    exit 1
fi

# 2. List recent backups
echo ""
echo "📋 Recent backups:"
BACKUPS=$(gsutil ls "gs://$BACKUP_BUCKET/coolbits-backup-*.tar.gz" 2>/dev/null | sort | tail -5)
if [ -z "$BACKUPS" ]; then
    echo "  ❌ No backups found"
    exit 1
fi

echo "$BACKUPS" | while read -r backup; do
    echo "  📁 $backup"
done

# 3. Get latest backup
LATEST_BACKUP=$(echo "$BACKUPS" | tail -1)
BACKUP_NAME=$(basename "$LATEST_BACKUP")
CHECKSUM_FILE="${BACKUP_NAME}.sha256"

echo ""
echo "🔍 Verifying latest backup: $BACKUP_NAME"

# 4. Check if checksum file exists
if gsutil ls "gs://$BACKUP_BUCKET/$CHECKSUM_FILE" >/dev/null 2>&1; then
    echo "  ✅ Checksum file exists"
else
    echo "  ❌ Checksum file missing"
    exit 1
fi

# 5. Download and verify checksum
echo "  📥 Downloading backup for verification..."
gsutil cp "$LATEST_BACKUP" "/tmp/$BACKUP_NAME"
gsutil cp "gs://$BACKUP_BUCKET/$CHECKSUM_FILE" "/tmp/$CHECKSUM_FILE"

# 6. Calculate local checksum
LOCAL_CHECKSUM=$(sha256sum "/tmp/$BACKUP_NAME" | cut -d' ' -f1)
REMOTE_CHECKSUM=$(cat "/tmp/$CHECKSUM_FILE")

echo "  🔐 Local checksum:  $LOCAL_CHECKSUM"
echo "  🔐 Remote checksum: $REMOTE_CHECKSUM"

if [ "$LOCAL_CHECKSUM" = "$REMOTE_CHECKSUM" ]; then
    echo "  ✅ Checksum verification passed"
else
    echo "  ❌ Checksum verification failed"
    exit 1
fi

# 7. Extract and verify contents
echo "  📦 Extracting backup for content verification..."
mkdir -p "/tmp/backup_verify"
tar -xzf "/tmp/$BACKUP_NAME" -C "/tmp/backup_verify"

# Check for required files
REQUIRED_FILES=(
    "backup_metadata.json"
    "package.json"
    "requirements.txt"
    "Dockerfile"
)

echo "  📋 Checking required files..."
ALL_FILES_PRESENT=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "/tmp/backup_verify/$file" ]; then
        echo "    ✅ $file"
    else
        echo "    ❌ $file (missing)"
        ALL_FILES_PRESENT=false
    fi
done

if [ "$ALL_FILES_PRESENT" = true ]; then
    echo "  ✅ All required files present"
else
    echo "  ❌ Some required files missing"
    exit 1
fi

# 8. Check backup metadata
echo "  📊 Checking backup metadata..."
if [ -f "/tmp/backup_verify/backup_metadata.json" ]; then
    METADATA=$(cat "/tmp/backup_verify/backup_metadata.json")
    echo "    📝 Metadata: $METADATA"
    
    # Check if metadata contains required fields
    if echo "$METADATA" | jq -e '.timestamp' >/dev/null 2>&1; then
        echo "    ✅ Timestamp present"
    else
        echo "    ❌ Timestamp missing"
        exit 1
    fi
    
    if echo "$METADATA" | jq -e '.project_id' >/dev/null 2>&1; then
        echo "    ✅ Project ID present"
    else
        echo "    ❌ Project ID missing"
        exit 1
    fi
else
    echo "    ❌ Metadata file missing"
    exit 1
fi

# 9. Cleanup
echo "  🧹 Cleaning up..."
rm -rf "/tmp/$BACKUP_NAME"
rm -rf "/tmp/$CHECKSUM_FILE"
rm -rf "/tmp/backup_verify"

# 10. Check backup age
echo ""
echo "⏰ Checking backup age..."
BACKUP_TIMESTAMP=$(gsutil stat "$LATEST_BACKUP" | grep "Creation time" | cut -d: -f2- | xargs)
BACKUP_DATE=$(date -d "$BACKUP_TIMESTAMP" +%s)
CURRENT_DATE=$(date +%s)
AGE_HOURS=$(( (CURRENT_DATE - BACKUP_DATE) / 3600 ))

echo "  📅 Backup created: $BACKUP_TIMESTAMP"
echo "  ⏰ Age: $AGE_HOURS hours"

if [ $AGE_HOURS -lt 25 ]; then
    echo "  ✅ Backup is recent (less than 25 hours old)"
else
    echo "  ⚠️  Backup is old (more than 25 hours old)"
fi

echo ""
echo "✅ Backup verification completed successfully!"
echo "📁 Latest backup: $LATEST_BACKUP"
echo "🔐 Checksum: $REMOTE_CHECKSUM"
echo "⏰ Age: $AGE_HOURS hours"
