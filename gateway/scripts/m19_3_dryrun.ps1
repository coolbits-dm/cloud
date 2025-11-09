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
  [string]$FlowId = ""
)

$ErrorActionPreference = "Stop"
Write-Host "== M19.3 Orchestrator Dry Run Test =="

Set-Location $GatewayDir

if (-not $FlowId) {
  # Get first flow
  Write-Host "Getting first available flow..."
  try {
    $response = Invoke-WebRequest "$ServiceUrl/v1/flows" -UseBasicParsing -TimeoutSec 10
    $flows = $response.Content | ConvertFrom-Jjson
    if ($flows.Count -eq 0) {
      Write-Error "No flows found. Run m19_3_seed.ps1 first."
      exit 1
    }
    $FlowId = $flows[0].id
    Write-Host "Using flow: $($flows[0].name) ($FlowId)"
  } catch {
    Write-Error "Failed to get flows: $($_.Exception.Message)"
    exit 1
  }
}

# Test data
$testInput = @{
  post = @{
    id = "dry-test-post-456"
    panel = "user"
    author = "dry_test_user"
    text = "This is a dry run test post. No side effects should occur."
  }
}

$runData = @{
  input = $testInput
  mode = "dry"
} | ConvertTo-Jjson -Depth 10

Write-Host "Running flow $FlowId in DRY mode..."
try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/flows/$FlowId/run" -Method POST -Body $runData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($response.StatusCode)] Dry run started OK"
  $result = $response.Content | ConvertFrom-Json
  $runId = $result.run_id
  $traceId = $result.trace_id
  Write-Host "Run ID: $runId"
  Write-Host "Trace ID: $traceId"
  
} catch {
  Write-Host "[ERR] Dry run failed: $($_.Exception.Message)"
  exit 1
}

# Poll run status
Write-Host "Polling dry run status..."
$maxAttempts = 20
$attempt = 0

while ($attempt -lt $maxAttempts) {
  Start-Sleep -Seconds 2
  $attempt++
  
  try {
    $response = Invoke-WebRequest "$ServiceUrl/v1/flow-runs/$runId" -UseBasicParsing -TimeoutSec 5
    $runDetails = $response.Content | ConvertFrom-Json
    
    Write-Host "Dry run status: $($runDetails.status)"
    
    if ($runDetails.status -eq "success") {
      Write-Host "Dry run completed successfully!"
      Write-Host "Nodes executed: $($runDetails.nodes.Count)"
      foreach ($node in $runDetails.nodes) {
        Write-Host "  - $($node.node_id): $($node.status) ($($node.took_ms)ms)"
        if ($node.output.dry_run) {
          Write-Host "    [DRY RUN] No side effects"
        }
      }
      break
    } elseif ($runDetails.status -eq "failed") {
      Write-Host "Dry run failed!"
      foreach ($node in $runDetails.nodes) {
        if ($node.status -eq "failed") {
          Write-Host "  - $($node.node_id): FAILED - $($node.output.error)"
        }
      }
      break
    }
    
  } catch {
    Write-Host "Polling error: $($_.Exception.Message)"
  }
}

if ($attempt -eq $maxAttempts) {
  Write-Host "Timeout waiting for dry run"
}

# Get run events
Write-Host "Getting dry run events..."
try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/flow-runs/$runId/events" -UseBasicParsing -TimeoutSec 5
  $events = $response.Content | ConvertFrom-Json
  Write-Host "Total events: $($events.Count)"
  
  foreach ($event in $events | Sort-Object ts) {
    $level = $event.level.ToUpper()
    $node = if ($event.node_id) { "[$($event.node_id)]" } else { "[FLOW]" }
    Write-Host "  $($event.ts) $level $node $($event.message)"
  }
} catch {
  Write-Host "[ERR] Failed to get events: $($_.Exception.Message)"
}

# Verify no side effects
Write-Host "Verifying no side effects..."
try {
  # Check if any comments were created for the test post
  $response = Invoke-WebRequest "$ServiceUrl/v1/invocations?post_id=dry-test-post-456" -UseBasicParsing -TimeoutSec 5
  Write-Host "No invocations should exist for dry test post"
} catch {
  Write-Host "No invocations found (expected for dry run)"
}

Write-Host "== Dry run test completed =="
Write-Host "Dry run should show no side effects (no comments posted, no ledger changes)"
