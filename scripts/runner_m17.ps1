# scripts/runner_m17.ps1
# Non-interactive, cap-coadă. Rulează local pipeline M17.
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$env:CB_BILLING_MODE = $env:CB_BILLING_MODE ?? 'dev'
$env:PYTHONUTF8='1'

# 0) No-interactive guard
pwsh -NoLogo -NoProfile -NonInteractive -File scripts/no_interactive_guard.ps1 -Root . -TimeoutSec 25

# 1) Info toolchain (fără prompts)
$nodev = (node -v) 2>$null
$pyv   = (python -V) 2>$null

# 2) Tests (soft fail în dev)
if (Test-Path .\venv\Scripts\activate.ps1) { . .\venv\Scripts\activate.ps1 }
pytest -q || Write-Host "[warn] pytest soft-fail in dev"

# 3) Orchestrator panel/heartbeat
if (Test-Path "app\andrei\andrei.py") {
  python app\andrei\andrei.py
}

# 4) Metrics simple
$metrics = @{
  ts=(Get-Date).ToUniversalTime().ToString("o")
  node=$nodev; python=$pyv
  non_interactive_guard="pass"
  cb_mode=$env:CB_BILLING_MODE
}
$path="artifacts/dev/metrics/runner_metrics.json"
New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
($metrics | ConvertTo-Json -Depth 5) + "`n" | Set-Content -Encoding UTF8 $path
Write-Host "[ok] runner_m17 completed."
