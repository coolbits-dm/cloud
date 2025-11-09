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
  [string]$DB_DSN = "",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Write-Host "== M19 Reindex ANN =="

Set-Location $GatewayDir

if (-not $DB_DSN) {
  Write-Error "DB_DSN not provided. Use -DB_DSN parameter."
  exit 1
}

# Set environment
$env:DB_DSN = $DB_DSN

if ($DryRun) {
  Write-Host "Dry run mode - would reindex ANN index"
  exit 0
}

# Reindex ANN index
Write-Host "Reindexing ANN index..."
python -c "
from db import get_db_session
from sqlalchemy import text

db = get_db_session()
try:
    # Drop existing index
    db.execute(text('DROP INDEX IF EXISTS idx_rag_embeddings_ann'))
    db.commit()
    print('Dropped existing ANN index')
    
    # Create new index
    db.execute(text('''
        CREATE INDEX CONCURRENTLY idx_rag_embeddings_ann
        ON rag_embeddings USING ivfflat (embedding vector_l2_ops) 
        WITH (lists = 100)
    '''))
    db.commit()
    print('Created new ANN index')
    
except Exception as e:
    print(f'Error reindexing: {e}')
    db.rollback()
    sys.exit(1)
finally:
    db.close()
"

if ($LASTEXITCODE -ne 0) {
  Write-Error "Reindexing failed!"
  exit 1
}

Write-Host "== Reindexing completed =="
