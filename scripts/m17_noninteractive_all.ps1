# scripts/m17_noninteractive_all.ps1
# Non-interactive end-to-end launcher (guard -> runner -> report -> optional commit)
# Exit imediat pe orice interacțiune / eroare neașteptată.

# --- Kill prompts & noise ---
$ErrorActionPreference              = 'Stop'
$ProgressPreference                 = 'SilentlyContinue'
$InformationPreference              = 'SilentlyContinue'
$ConfirmPreference                  = 'None'

# 1) permite autoload-ul ca să putem importa cmdlet-urile de bază
$PSModuleAutoLoadingPreference      = 'All'
Import-Module Microsoft.PowerShell.Management -ErrorAction Stop
Import-Module Microsoft.PowerShell.Utility    -ErrorAction Stop

# 2) după ce le-am încărcat, putem opri autoload-ul
$PSModuleAutoLoadingPreference      = 'None'

# 3) env invariants
$env:GIT_TERMINAL_PROMPT            = '0'     # Git n-are voie să ceară parolă
$env:CB_BILLING_MODE                = $env:CB_BILLING_MODE ?? 'dev'
$env:PYTHONUTF8                     = '1'

# --- Helper: fail-fast cu raport JSON ---
function Fail($reason){
  $out = [pscustomobject]@{ ok=$false; reason=$reason }
  $out | ConvertTo-Json -Depth 5 | Write-Output
  exit 2
}

# --- 0) Sanity: suntem în repo & Actions rămâne oprit ---
try { git rev-parse --is-inside-work-tree >$null 2>&1 } catch { Fail "not_a_git_repo" }
$activeWf = Get-ChildItem .github/workflows -File -Include *.yml,*.yaml -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
if ($activeWf -and ($activeWf | Where-Object { $_ -ne 'noop.yml' }).Count -gt 0) { Fail "workflows_active_found" }

# --- 1) Guard anti-interactive (turbo) ---
pwsh -NoLogo -NoProfile -NonInteractive -File scripts\no_interactive_guard.ps1 -Root . -TimeoutSec 25 | Out-Host

# --- 2) Runner M17 (non-interactive) ---
pwsh -NoLogo -NoProfile -NonInteractive -File scripts\runner_m17.ps1 | Out-Host

# --- 3) Report HTML (observability) ---
python scripts\generate_report.py | Out-Host

# --- 4) Actualizează panel/artefacte în git doar dacă s-au schimbat ---
$changed = (git status --porcelain) -ne $null -and (git status --porcelain).Trim().Length -gt 0
if ($changed) {
  git add panel\state.json panel\gates.jsonl artifacts\dev\metrics\*.json report\index.html 2>$null
  git commit -m "chore(M17): panel/metrics/report update (non-interactive)" 2>$null | Out-Null
  git -c core.askPass= push 2>$null | Out-Null
}

# --- 5) Raport final JSON unic ---
$sha    = (git rev-parse HEAD).Trim()
$state  = Get-Content panel\state.json -Raw | ConvertFrom-Json
$metricFiles = @()
if (Test-Path artifacts\dev\metrics) {
  Get-ChildItem artifacts\dev\metrics -File -Filter *.json | ForEach-Object {
    $metricFiles += @{ name=$_.Name; path=$_.FullName }
  }
}
[pscustomobject]@{
  ok               = $true
  milestone        = $state.milestone
  mode             = $state.mode
  overall          = $state.overall
  sha              = $sha
  actions_active   = @($activeWf)
  panel_state_path = "panel/state.json"
  metrics          = $metricFiles
  report_html      = "report/index.html"
  notes            = @(
    "Non-interactive end-to-end",
    "Git prompts disabled (GIT_TERMINAL_PROMPT=0)",
    "Guard turbo + runner + HTML report"
  )
} | ConvertTo-Json -Depth 6 | Write-Output
exit 0
