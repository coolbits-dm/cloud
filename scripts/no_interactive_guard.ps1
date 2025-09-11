# scripts/no_interactive_guard.ps1
# Fail build dacă detectăm comenzi interactive în repo
$ErrorActionPreference='Stop'
$patterns = @(
  'Read-Host','Pause','Out-GridView','Start-Process\s+[^\n]*-Wait',
  'Write-Host\s+.*"Press any key"','ChoiceDescription','[^\S\r\n]--interactive',
  'pip\s+install\s+.*-i\s+http','conda\s+activate','winget\s+install'
)
$files = Get-ChildItem -Recurse -File -Include *.ps1,*.psm1,*.cmd,*.bat,*.sh,*.py  | Where-Object {
  $_.FullName -notmatch '\\.venv\\' -and $_.FullName -notmatch '\\node_modules\\'
}
$bad=@()
foreach($f in $files){
  $c = Get-Content $f.FullName -Raw
  foreach($p in $patterns){
    if ($c -match $p){ $bad += [pscustomobject]@{file=$f.FullName; pattern=$p} }
  }
}
if($bad.Count -gt 0){
  $bad | Format-Table -Auto | Out-String | Write-Host
  Write-Error "Interactive patterns found. Blocked by no_interactive_guard."
}
Write-Host "[ok] no_interactive_guard passed."
