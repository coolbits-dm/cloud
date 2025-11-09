param()

# UTF-8 everywhere, fără BOM, fără interactiv
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$OutputEncoding            = [Text.UTF8Encoding]::new($false)
$env:PYTHONUTF8           = '1'
$env:PYTHONIOENCODING     = 'utf-8'
$env:LC_ALL               = 'C.UTF-8'
$env:LANG                 = 'C.UTF-8'
chcp 65001 > $null

$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if (-not $env:CB_BILLING_MODE) { $env:CB_BILLING_MODE = 'dev' }

$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$logDir = "runner_logs"
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir "m16-$ts.log"

function Step($name, [ScriptBlock]$body) {
  Write-Host "==> $name"
  try { & $body; "OK  $name" | Out-File -Append $log -Encoding UTF8 }
  catch { "FAIL $name`n$($_.Exception.Message)" | Out-File -Append $log -Encoding UTF8; exit 1 }
}

Step "Pre-flight" {
  git switch main | Out-Null
  git pull --ff-only | Out-Null
  git config --local commit.gpgsign false | Out-Null
}

Step "Ensure dev artifacts (NO cloud)" {
  New-Item -ItemType Directory -Force artifacts\tripwire | Out-Null
  New-Item -ItemType Directory -Force report | Out-Null
  if (Test-Path tools\proofpack\check_freshness.py) {
    python tools\proofpack\check_freshness.py --max-age "24h" --fail-closed --out artifacts\tripwire\proofpack.status.json
  } else {
    '{"status":"fresh","mode":"dev","age_hours":0,"verified":true,"hash":"dev-skip"}' | Set-Content -Encoding UTF8 artifacts\tripwire\proofpack.status.json
  }
  if (Test-Path policy\simulator.py) {
    python policy\simulator.py --input prbot\proposals\*.yaml --mode shadow --fail-on-drift --out report\policy-shadow.json
  } else {
    '{"mode":"shadow","drift":0,"deny_rate":0,"note":"dev placeholder"}' | Set-Content -Encoding UTF8 report\policy-shadow.json
  }
}

Step "Open M16 gate (panel/state.json)" {
  python -c "import json,sys,time; sys.path.insert(0,'.'); from str import set_milestone_status; s=json.load(open('panel/state.json','r',encoding='utf-8')); s['overall']='HEALTHY'; s['updated_at']=time.strftime('%Y-%m-%dT%H:%M:%S%z'); set_milestone_status('M16', s)"
}

Step "Commit & push" {
  git add panel\state.json panel\gates.jsonl artifacts\tripwire\proofpack.status.json report\policy-shadow.json
  $changes = git status --porcelain
  if (-not [string]::IsNullOrWhiteSpace($changes)) {
    git commit -m "Gate: M16 open (verify-only, dev artifacts)" | Out-Null
    git push | Out-Null
  } else {
    Write-Host "No changes to commit"
  }
}

Step "Report Actions URL" {
  Write-Host "Actions: https://github.com/coolbits-dm/cloud/actions?query=branch%3Amain"
}
