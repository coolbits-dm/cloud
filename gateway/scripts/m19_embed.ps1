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
Write-Host "== M19 Embedding Worker =="

Set-Location $GatewayDir

if (-not $DB_DSN) {
  Write-Error "DB_DSN not provided. Use -DB_DSN parameter."
  exit 1
}

# Set environment
$env:DB_DSN = $DB_DSN
$env:EMBED_MODEL = "text-embedding-3-small"
$env:EMBED_DIM = "1536"
$env:EMBED_BATCH_SIZE = "64"

if ($DryRun) {
  Write-Host "Dry run mode - checking pending chunks"
  python -c "
from embed_worker import get_pending_count, get_db_session
db = get_db_session()
try:
    pending = get_pending_count(db)
    print(f'Pending chunks: {pending}')
finally:
    db.close()
"
  exit 0
}

# Run embedding worker
Write-Host "Starting embedding worker..."
python embed_worker.py

if ($LASTEXITCODE -ne 0) {
  Write-Error "Embedding worker failed!"
  exit 1
}

Write-Host "== Embedding worker completed =="
