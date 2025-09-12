# --- Hard guard: NU din Cursor/VS Code ---
$ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
if ($parent -match 'cursor|code|code-insiders') {
  Write-Error "Nu rula din Cursor/VS Code. Deschide PowerShell 7 (pwsh) și rulează scriptul acolo."
  exit 1
}
# -----------------------------------------

param(
  [string]$GatewayDir = "C:\Users\andre\Desktop\coolbits\gateway",
  [string]$ArtifactsDir = "C:\Users\andre\Desktop\coolbits\artifacts\dev",
  [string]$DB_DSN = "",
  [switch]$DryRun,
  [switch]$SkipImport
)

$ErrorActionPreference = "Stop"
Write-Host "== M19 Database Migration =="

Set-Location $GatewayDir

if (-not $DB_DSN) {
  Write-Error "DB_DSN not provided. Use -DB_DSN parameter."
  exit 1
}

# Set environment
$env:DB_DSN = $DB_DSN

if ($DryRun) {
  Write-Host "Dry run mode - showing migration plan"
  Write-Host "Would migrate from: $ArtifactsDir"
  Write-Host "Would migrate to: $DB_DSN"
  exit 0
}

# Run Alembic migrations
Write-Host "Running Alembic migrations..."
alembic upgrade head

if ($LASTEXITCODE -ne 0) {
  Write-Error "Alembic migration failed!"
  exit 1
}

Write-Host "Database schema updated successfully"

if ($SkipImport) {
  Write-Host "Skipping JSON import"
  exit 0
}

# Import JSON data
Write-Host "Importing JSON data from $ArtifactsDir..."

# Import walls data
$wallFiles = @("user", "business", "agency", "dev")
$totalPosts = 0
$totalComments = 0

foreach ($panel in $wallFiles) {
  $wallFile = "$ArtifactsDir\walls\$panel.json"
  if (Test-Path $wallFile) {
    Write-Host "Importing $panel wall data..."
    $result = python -c "
import json
import sys
from db import Post, Comment, get_db_session
from datetime import datetime
import uuid

db = get_db_session()
try:
    with open('$wallFile', 'r') as f:
        data = json.load(f)
    
    posts_count = 0
    comments_count = 0
    
    for post_data in data.get('posts', []):
        # Generate stable ID if missing
        post_id = post_data.get('id')
        if not post_id:
            content_hash = hashlib.sha256(post_data.get('text', '').encode()).hexdigest()[:8]
            post_id = f'post_{$panel}_{content_hash}'
        
        post = Post(
            id=post_id,
            panel='$panel',
            author=post_data.get('author', 'unknown'),
            text=post_data.get('text', ''),
            attachments=post_data.get('attachments', {})
        )
        db.add(post)
        posts_count += 1
        
        # Import comments
        for comment_data in post_data.get('comments', []):
            comment_id = comment_data.get('id')
            if not comment_id:
                comment_id = str(uuid.uuid4())
            
            comment = Comment(
                id=comment_id,
                post_id=post_id,
                author=comment_data.get('author', 'unknown'),
                text=comment_data.get('text', '')
            )
            db.add(comment)
            comments_count += 1
    
    db.commit()
    print(f'Imported {posts_count} posts and {comments_count} comments for $panel')
    
except Exception as e:
    print(f'Error importing $panel: {e}')
    db.rollback()
    sys.exit(1)
finally:
    db.close()
"
    
    if ($LASTEXITCODE -ne 0) {
      Write-Error "Failed to import $panel data"
      exit 1
    }
    
    # Parse result
    if ($result -match "Imported (\d+) posts and (\d+) comments") {
      $totalPosts += [int]$matches[1]
      $totalComments += [int]$matches[2]
    }
  }
}

# Import ledger data
$ledgerFile = "$ArtifactsDir\tokens\ledger.json"
if (Test-Path $ledgerFile) {
  Write-Host "Importing ledger data..."
  $result = python -c "
import json
from db import LedgerEntry, get_db_session
from decimal import Decimal

db = get_db_session()
try:
    with open('$ledgerFile', 'r') as f:
        data = json.load(f)
    
    entries_count = 0
    for entry_data in data.get('entries', []):
        entry = LedgerEntry(
            ref=entry_data.get('ref', ''),
            delta=Decimal(str(entry_data.get('delta', 0))),
            reason=entry_data.get('reason', ''),
            meta=entry_data.get('meta', {})
        )
        db.add(entry)
        entries_count += 1
    
    db.commit()
    print(f'Imported {entries_count} ledger entries')
    
except Exception as e:
    print(f'Error importing ledger: {e}')
    db.rollback()
    sys.exit(1)
finally:
    db.close()
"
  
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to import ledger data"
    exit 1
  }
}

# Import RAG data
$ragDir = "$ArtifactsDir\rag"
if (Test-Path $ragDir) {
  Write-Host "Importing RAG data..."
  $result = python -c "
import json
import os
from db import RAGChunk, get_db_session

db = get_db_session()
try:
    rag_count = 0
    for panel in ['user', 'business', 'agency', 'dev']:
        rag_file = os.path.join('$ragDir', f'{panel}.json')
        if os.path.exists(rag_file):
            with open(rag_file, 'r') as f:
                data = json.load(f)
            
            for chunk_data in data.get('chunks', []):
                chunk = RAGChunk(
                    panel=panel,
                    source=chunk_data.get('source', f'rag:{panel}'),
                    text=chunk_data.get('text', ''),
                    meta=chunk_data.get('meta', {})
                )
                db.add(chunk)
                rag_count += 1
    
    db.commit()
    print(f'Imported {rag_count} RAG chunks')
    
except Exception as e:
    print(f'Error importing RAG: {e}')
    db.rollback()
    sys.exit(1)
finally:
    db.close()
"
  
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to import RAG data"
    exit 1
  }
}

Write-Host "== Migration completed successfully =="
Write-Host "Total posts imported: $totalPosts"
Write-Host "Total comments imported: $totalComments"