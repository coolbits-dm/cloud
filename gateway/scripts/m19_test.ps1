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
  [string]$DB_DSN = "",
  [string]$ServiceUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"
Write-Host "== M19 API Tests =="

Set-Location $GatewayDir

# Test health endpoint
Write-Host "Testing health endpoint..."
try {
  $response = Invoke-WebRequest "$ServiceUrl/health" -UseBasicParsing -TimeoutSec 5
  Write-Host "[$($response.StatusCode)] Health OK"
} catch {
  Write-Host "[ERR] Health failed: $($_.Exception.Message)"
}

# Test chat endpoint
Write-Host "Testing chat endpoint..."
$chatData = @{
  messages = @(
    @{ role = "user"; content = "Hello from M19 test" }
  )
  model = "dummy"
} | ConvertTo-Json

try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/chat" -Method POST -Body $chatData -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
  Write-Host "[$($response.StatusCode)] Chat OK"
  $result = $response.Content | ConvertFrom-Json
  Write-Host "Reply: $($result.reply)"
} catch {
  Write-Host "[ERR] Chat failed: $($_.Exception.Message)"
}

# Test RAG endpoint
Write-Host "Testing RAG endpoint..."
$ragData = @{
  panel = "user"
  q = "test query"
  k = 3
} | ConvertTo-Json

try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/rag/query" -Method POST -Body $ragData -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
  Write-Host "[$($response.StatusCode)] RAG OK"
  $result = $response.Content | ConvertFrom-Json
  Write-Host "Answers: $($result.answers.Count)"
} catch {
  Write-Host "[ERR] RAG failed: $($_.Exception.Message)"
}

# Test metrics endpoint
Write-Host "Testing metrics endpoint..."
try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/metrics/snapshot" -UseBasicParsing -TimeoutSec 5
  Write-Host "[$($response.StatusCode)] Metrics OK"
  $result = $response.Content | ConvertFrom-Json
  Write-Host "Chat P95: $($result.chat_p95_ms)ms"
} catch {
  Write-Host "[ERR] Metrics failed: $($_.Exception.Message)"
}

Write-Host "== API Tests completed =="
