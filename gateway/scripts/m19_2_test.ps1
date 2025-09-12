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
  [string]$ServiceUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"
Write-Host "== M19.2 NHA Tests =="

Set-Location $GatewayDir

# Test NHA invoke with multiple mentions
Write-Host "Testing NHA invoke with multiple mentions..."
$testData = @{
  post = @{
    panel = "user"
    author = "test_user"
    text = "This is a test post with @nha:sentiment and @nha:summarize analysis. Please analyze the sentiment and provide a summary."
  }
} | ConvertTo-Json

try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/nha/invoke" -Method POST -Body $testData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($response.StatusCode)] NHA invoke OK"
  $result = $response.Content | ConvertFrom-Json
  Write-Host "Post ID: $($result.post_id)"
  Write-Host "Invocations: $($result.invocations.Count)"
  Write-Host "Ledger delta: $($result.ledger_delta)"
  Write-Host "Trace ID: $($result.trace_id)"
  
  $postId = $result.post_id
  
  # Poll invocations until done
  Write-Host "Polling invocations..."
  $maxAttempts = 30
  $attempt = 0
  
  while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    $attempt++
    
    try {
      $invResponse = Invoke-WebRequest "$ServiceUrl/v1/invocations?post_id=$postId" -UseBasicParsing -TimeoutSec 5
      $invResult = $invResponse.Content | ConvertFrom-Json
      
      $allDone = $true
      foreach ($inv in $invResult.invocations) {
        Write-Host "Invocation $($inv.agent_id): $($inv.status)"
        if ($inv.status -eq "queued" -or $inv.status -eq "running") {
          $allDone = $false
        }
      }
      
      if ($allDone) {
        Write-Host "All invocations completed"
        break
      }
    } catch {
      Write-Host "Polling error: $($_.Exception.Message)"
    }
  }
  
  if ($attempt -eq $maxAttempts) {
    Write-Host "Timeout waiting for invocations"
  }
  
} catch {
  Write-Host "[ERR] NHA invoke failed: $($_.Exception.Message)"
}

# Test ledger balance
Write-Host "Testing ledger balance..."
try {
  $balanceResponse = Invoke-WebRequest "$ServiceUrl/v1/ledger/balance?ref=$postId" -UseBasicParsing -TimeoutSec 5
  Write-Host "[$($balanceResponse.StatusCode)] Ledger balance OK"
  $balanceResult = $balanceResponse.Content | ConvertFrom-Json
  Write-Host "Balance: $($balanceResult.balance)"
} catch {
  Write-Host "[ERR] Ledger balance failed: $($_.Exception.Message)"
}

# Test metrics
Write-Host "Testing metrics..."
try {
  $metricsResponse = Invoke-WebRequest "$ServiceUrl/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 5
  Write-Host "[$($metricsResponse.StatusCode)] Metrics OK"
  $metricsResult = $metricsResponse.Content | ConvertFrom-Json
  Write-Host "NHA queue pending: $($metricsResult.nha_queue_pending)"
  Write-Host "NHA P95 times: $($metricsResult.nha_p95_ms | ConvertTo-Json)"
} catch {
  Write-Host "[ERR] Metrics failed: $($_.Exception.Message)"
}

Write-Host "== NHA Tests completed =="
