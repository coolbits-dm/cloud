# Re-run în PowerShell 7 EXTERN dacă am fost porniți din Cursor/VS Code
try {
  $ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
  $parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
  $isEditor = ($parent -match 'cursor|code|code-insiders')
} catch { $isEditor = $false }

if ($isEditor) {
  $self = $MyInvocation.MyCommand.Path
  $argsJoined = ($args | ForEach-Object { "`"$_`"" }) -join ' '
  Start-Process -FilePath "$env:ProgramFiles\PowerShell\7\pwsh.exe" `
    -ArgumentList "-NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$self`" $argsJoined" `
    -WindowStyle Normal
  exit 0
}

# De aici în jos e mediul „real", deja în pwsh extern.
# Poți include aici guard-urile/ENV comune pentru toate scripturile.

# Common environment setup
$ErrorActionPreference = "Stop"
$env:NEXT_TELEMETRY_DISABLED = "1"
$env:CB_DATA_ROOT = "C:\Users\andre\Desktop\coolbits\artifacts\dev"

# Node 20 LTS check
$node = (node -v 2>$null)
if (-not $node -or -not $node.StartsWith("v20")) {
  npm config set engine-strict false | Out-Null
  Write-Host "Warning: Node $node detected, disabled engine-strict" -ForegroundColor Yellow
}

Write-Host "Running in external PowerShell 7: $($PSVersionTable.PSVersion)" -ForegroundColor Green
