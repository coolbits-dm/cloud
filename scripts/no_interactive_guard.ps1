# scripts/no_interactive_guard.ps1
param(
  [string]$Root = ".",
  [int]$TimeoutSec = 20,
  [int]$ProgressEvery = 400
)

$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'

# directoare de sărit (regex pe căi Windows)
$skipDirs = '(^|\\)(node_modules|\.venv|\.git|artifacts|report|dist|build|out)(\\|$)'

# patternuri „interzise"
$patterns = @(
  'Read-Host',
  'Pause',
  'Out-GridView',
  '--interactive',
  'Start-Process\s+[^\r\n]*-Wait',
  '\binput\s*\('            # fallback pt. Python
)

# cronometru pt. timeout
$sw = [Diagnostics.Stopwatch]::StartNew()

# fișiere candidate (filtrate rapid pe extensii)
$files = Get-ChildItem -Path $Root -Recurse -File -Include *.ps1,*.psm1,*.cmd,*.bat,*.sh,*.py |
  Where-Object { $_.FullName -notmatch $skipDirs }

$bad = New-Object System.Collections.Generic.List[object]
$i = 0

foreach ($f in $files) {
  if ($sw.Elapsed.TotalSeconds -ge $TimeoutSec) {
    throw "no_interactive_guard timeout la $($sw.Elapsed.TotalSeconds)s (ai $(($i)) fișiere parcurse)"
  }

  $i++

  # caută regex-urile în streaming; mult mai rapid decât Get-Content -Raw
  $hit = Select-String -Path $f.FullName -Pattern $patterns -CaseSensitive -Quiet -ErrorAction SilentlyContinue
  if ($hit) {
    $bad.Add([pscustomobject]@{ file = $f.FullName })
  }

  if ($ProgressEvery -gt 0 -and ($i % $ProgressEvery) -eq 0) {
    Write-Host "[scan] $i fișiere..." -ForegroundColor DarkGray
  }
}

if ($bad.Count -gt 0) {
  $bad | Format-Table -Auto | Out-String | Write-Host
  throw "Interactive patterns found: $($bad.Count)"
}

Write-Host "[ok] no_interactive_guard passed în $([int]$sw.Elapsed.TotalMilliseconds) ms (scan: $i fișiere)" -ForegroundColor Green
