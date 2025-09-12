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
  [string]$RedisURL = "redis://localhost:6379",
  [int]$WorkerCount = 4,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Write-Host "== M19.2 NHA Workers =="

Set-Location $GatewayDir

if (-not $DB_DSN) {
  Write-Error "DB_DSN not provided. Use -DB_DSN parameter."
  exit 1
}

# Set environment
$env:DB_DSN = $DB_DSN
$env:REDIS_URL = $RedisURL
$env:WORKER_TIMEOUT = "15"
$env:WORKER_RETRY_COUNT = "2"
$env:WORKER_BATCH_SIZE = "1"

if ($DryRun) {
  Write-Host "Dry run mode - would start $WorkerCount workers"
  exit 0
}

# Start workers
Write-Host "Starting $WorkerCount NHA workers..."

$workers = @()
for ($i = 1; $i -le $WorkerCount; $i++) {
  Write-Host "Starting worker $i..."
  $worker = Start-Process -FilePath "python" -ArgumentList "-m", "gateway.nha_worker" -PassThru -WindowStyle Hidden
  $workers += $worker
  Start-Sleep -Milliseconds 500
}

Write-Host "Started $($workers.Count) workers"

# Monitor workers
Write-Host "Monitoring workers... (Press Ctrl+C to stop)"
try {
  while ($true) {
    $alive = 0
    foreach ($worker in $workers) {
      if (-not $worker.HasExited) {
        $alive++
      }
    }
    
    Write-Host "Active workers: $alive/$($workers.Count)"
    
    if ($alive -eq 0) {
      Write-Host "All workers stopped"
      break
    }
    
    Start-Sleep -Seconds 10
  }
} catch {
  Write-Host "Stopping workers..."
  foreach ($worker in $workers) {
    if (-not $worker.HasExited) {
      $worker.Kill()
    }
  }
}

Write-Host "== Workers stopped =="
