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
Write-Host "== M19.2 Database Migration =="

Set-Location $GatewayDir

if (-not $DB_DSN) {
  Write-Error "DB_DSN not provided. Use -DB_DSN parameter."
  exit 1
}

# Set environment
$env:DB_DSN = $DB_DSN

if ($DryRun) {
  Write-Host "Dry run mode - showing migration plan"
  Write-Host "Would apply m19_2_invocations migration"
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

# Verify new columns exist
Write-Host "Verifying new columns..."
python -c "
from db import get_db_session
from sqlalchemy import text

db = get_db_session()
try:
    # Check invocations columns
    result = db.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = ''invocations'' AND column_name IN (''error'', ''trace_id'')'))
    columns = [row[0] for row in result]
    print(f'Invocations columns: {columns}')
    
    # Check comments meta column
    result = db.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = ''comments'' AND column_name = ''meta'''))
    meta_exists = result.fetchone() is not None
    print(f'Comments meta column exists: {meta_exists}')
    
    # Check indexes
    result = db.execute(text('SELECT indexname FROM pg_indexes WHERE tablename = ''invocations'' AND indexname LIKE ''idx_inv_%'''))
    indexes = [row[0] for row in result]
    print(f'Invocations indexes: {indexes}')
    
finally:
    db.close()
"

if ($LASTEXITCODE -ne 0) {
  Write-Error "Verification failed!"
  exit 1
}

Write-Host "== Migration completed successfully =="
