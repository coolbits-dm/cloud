# --- Hard guard ---
$ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
if ($parent -match 'cursor|code|code-insiders') {
  Write-Error "Nu rula din Cursor/VS Code. Deschide PowerShell 7 (pwsh)."
  exit 1
}
# ------------------

param([string]$BaseUrl = "http://localhost:3000")

$ErrorActionPreference = "Stop"
$paths = @(
  "/api/walls/user", "/api/walls/business", "/api/walls/agency", "/api/walls/dev",
  "/user/wall", "/business/wall", "/agency/wall", "/dev/wall"
)
foreach ($p in $paths) {
  $u = "$BaseUrl$p"
  try {
    $r = Invoke-WebRequest $u -UseBasicParsing -TimeoutSec 5
    Write-Host "[$($r.StatusCode)] $u"
  } catch {
    Write-Host "[ERR] $u -> $($_.Exception.Message)"
  }
}
