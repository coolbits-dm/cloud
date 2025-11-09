# scripts/actions_panic_cleanup.ps1
param(
  [string]$Owner = "coolbits-dm",
  [string]$Repo  = "cloud",
  [string]$Branch = "main",
  [int]$Pages = 5
)

$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'

if (-not $env:GH_TOKEN -or $env:GH_TOKEN.Trim().Length -lt 20) {
  Write-Error "GH_TOKEN lipsă sau invalid. Creează PAT classic (repo+workflow) și exportă-l în env."
  exit 2
}

$base = "https://api.github.com"
$hdrs = @{
  Authorization          = "token $env:GH_TOKEN"
  "User-Agent"           = "cbCleanup"
  "X-GitHub-Api-Version" = "2022-11-28"
}

function Get-Runs([string[]]$statuses){
  $all=@()
  for($p=1; $p -le $Pages; $p++){
    $u = "$base/repos/$Owner/$Repo/actions/runs?branch=$Branch&per_page=100&page=$p"
    $r = Invoke-RestMethod -Headers $hdrs -Uri $u -Method GET
    if ($null -eq $r.workflow_runs) { break }
    $all += $r.workflow_runs
    if ($r.workflow_runs.Count -lt 100) { break }
  }
  if ($statuses) { $all | ? { $_.status -in $statuses } } else { $all }
}

# 1) Anulează queued/in_progress
$kills = Get-Runs @("queued","in_progress")
foreach($run in $kills){
  Write-Host ("Cancel {0} — {1}" -f $run.id, $run.name)
  Invoke-RestMethod -Headers $hdrs -Uri "$base/repos/$Owner/$Repo/actions/runs/$($run.id)/cancel" -Method POST
  Start-Sleep -Milliseconds 200
}

# 2) Optional: șterge completed mai vechi de 7 zile (setați $DeleteOld=$true dacă chiar vrei curat)
$DeleteOld = $false
if ($DeleteOld) {
  $cut = (Get-Date).AddDays(-7)
  $old = Get-Runs @("completed") | ? { [datetime]$_.created_at -lt $cut }
  foreach($run in $old){
    Write-Host ("DELETE {0} — created {1}" -f $run.id, $run.created_at)
    Invoke-RestMethod -Headers $hdrs -Uri "$base/repos/$Owner/$Repo/actions/runs/$($run.id)" -Method DELETE
    Start-Sleep -Milliseconds 200
  }
}

# 3) Sumar
$all = Get-Runs $null
$sum = $all | Group-Object status | Select-Object Name,Count
$report = [pscustomobject]@{
  ok = $true
  owner = $Owner
  repo = $Repo
  branch = $Branch
  canceled = $kills.Count
  counts = $sum
  links = @(
    "https://github.com/$Owner/$Repo/actions?query=branch%3A$Branch",
    "https://github.com/$Owner/$Repo/actions?query=branch%3A$Branch+status%3Aqueued",
    "https://github.com/$Owner/$Repo/actions?query=branch%3A$Branch+status%3Ain_progress"
  )
}
$report | ConvertTo-Json -Depth 6 | Write-Output
