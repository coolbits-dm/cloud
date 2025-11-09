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
Write-Host "== M19.3 Orchestrator Migration =="

Set-Location $GatewayDir

if (-not $DB_DSN) {
  Write-Error "DB_DSN not provided. Use -DB_DSN parameter."
  exit 1
}

# Set environment
$env:DB_DSN = $DB_DSN

if ($DryRun) {
  Write-Host "Dry run mode - showing migration plan"
  Write-Host "Would apply m19_3_orchestrator migration"
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

# Verify new tables exist
Write-Host "Verifying new tables..."
python -c "
from db import get_db_session
from sqlalchemy import text

db = get_db_session()
try:
    # Check flows table
    result = db.execute(text('SELECT table_name FROM information_schema.tables WHERE table_name IN (''flows'', ''flow_runs'', ''run_events'', ''nodes_cache'')'))
    tables = [row[0] for row in result]
    print(f'Orchestrator tables: {tables}')
    
    # Check indexes
    result = db.execute(text('SELECT indexname FROM pg_indexes WHERE tablename IN (''flows'', ''flow_runs'', ''run_events'', ''nodes_cache'') AND indexname LIKE ''idx_%'''))
    indexes = [row[0] for row in result]
    print(f'Orchestrator indexes: {indexes}')
    
finally:
    db.close()
"

if ($LASTEXITCODE -ne 0) {
  Write-Error "Verification failed!"
  exit 1
}

Write-Host "== Migration completed successfully =="
