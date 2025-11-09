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
  [string]$ServiceUrl = "http://localhost:8000",
  [string]$RunId = ""
)

$ErrorActionPreference = "Stop"
Write-Host "== M19.3 Orchestrator Trace =="

Set-Location $GatewayDir

if (-not $RunId) {
  Write-Error "RunId not provided. Use -RunId parameter."
  exit 1
}

Write-Host "Getting trace for run: $RunId"

# Get run details
Write-Host "Getting run details..."
try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/flow-runs/$RunId" -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($response.StatusCode)] Run details OK"
  $runDetails = $response.Content | ConvertFrom-Jjson
  Write-Host "Flow ID: $($runDetails.flow_id)"
  Write-Host "Status: $($runDetails.status)"
  Write-Host "Started: $($runDetails.started_at)"
  Write-Host "Finished: $($runDetails.finished_at)"
  Write-Host "Trace ID: $($runDetails.trace_id)"
  
} catch {
  Write-Host "[ERR] Failed to get run details: $($_.Exception.Message)"
  exit 1
}

# Get run events
Write-Host "Getting run events..."
try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/flow-runs/$RunId/events" -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($response.StatusCode)] Run events OK"
  $events = $response.Content | ConvertFrom-Json
  
  Write-Host "`n=== TIMELINE ==="
  foreach ($event in $events | Sort-Object ts) {
    $level = $event.level.ToUpper()
    $node = if ($event.node_id) { "[$($event.node_id)]" } else { "[FLOW]" }
    $timestamp = [DateTime]::Parse($event.ts).ToString("HH:mm:ss.fff")
    Write-Host "$timestamp $level $node $($event.message)"
    
    if ($event.data) {
      $dataJson = $event.data | ConvertTo-Json -Compress
      Write-Host "    Data: $dataJson"
    }
  }
  
} catch {
  Write-Host "[ERR] Failed to get run events: $($_.Exception.Message)"
}

# Get node summary
Write-Host "`n=== NODE SUMMARY ==="
foreach ($node in $runDetails.nodes) {
  $status = $node.status.ToUpper()
  $took = if ($node.took_ms) { "$($node.took_ms)ms" } else { "N/A" }
  Write-Host "$($node.node_id): $status ($took)"
  
  if ($node.output) {
    $outputJson = $node.output | ConvertTo-Json -Compress
    Write-Host "  Output: $outputJson"
  }
}

# Performance summary
Write-Host "`n=== PERFORMANCE SUMMARY ==="
$totalNodes = $runDetails.nodes.Count
$successNodes = ($runDetails.nodes | Where-Object { $_.status -eq "success" }).Count
$failedNodes = ($runDetails.nodes | Where-Object { $_.status -eq "failed" }).Count
$skippedNodes = ($runDetails.nodes | Where-Object { $_.status -eq "skipped" }).Count

Write-Host "Total nodes: $totalNodes"
Write-Host "Success: $successNodes"
Write-Host "Failed: $failedNodes"
Write-Host "Skipped: $skippedNodes"

if ($runDetails.started_at -and $runDetails.finished_at) {
  $startTime = [DateTime]::Parse($runDetails.started_at)
  $endTime = [DateTime]::Parse($runDetails.finished_at)
  $totalMs = ($endTime - $startTime).TotalMilliseconds
  Write-Host "Total duration: $([math]::Round($totalMs))ms"
}

# Node timing breakdown
Write-Host "`n=== NODE TIMING BREAKDOWN ==="
$timedNodes = $runDetails.nodes | Where-Object { $_.took_ms -and $_.took_ms -gt 0 } | Sort-Object took_ms -Descending
foreach ($node in $timedNodes) {
  Write-Host "$($node.node_id): $($node.took_ms)ms"
}

Write-Host "`n== Trace completed =="
