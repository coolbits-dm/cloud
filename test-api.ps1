# Test API endpoints pentru M18.2
# Rulează în PowerShell 7 (pwsh), NU în Cursor

$ErrorActionPreference = "Stop"

Write-Host "== Testing M18.2 API Endpoints ==" -ForegroundColor Green

# Testează endpoint-urile
$endpoints = @(
    "http://localhost:3000/api/walls/user",
    "http://localhost:3000/user/wall",
    "http://localhost:3000/api/tokens",
    "http://localhost:3000/api/rag/user"
)

foreach ($endpoint in $endpoints) {
    Write-Host "Testing: $endpoint" -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri $endpoint -TimeoutSec 10 -ErrorAction Stop
        Write-Host "SUCCESS: Status $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))..." -ForegroundColor Green
    } catch {
        Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "" -ForegroundColor White
}

Write-Host "== API Tests Completed ==" -ForegroundColor Green
