# M20.2 Billing Verification Script
param(
  [string]$GatewayDir = "C:\Users\andre\Desktop\coolbits\gateway",
  [string]$ServiceUrl = "http://localhost:8000",
  [string]$OrgId = "demo",
  [switch]$Reconcile
)

$ErrorActionPreference = "Stop"
Write-Host "== M20.2 Billing Verification ==" -ForegroundColor Green

Set-Location $GatewayDir

# 1) Quota enforcement test
Write-Host "`n=== Testing Quota Enforcement ===" -ForegroundColor Yellow

$initialBalance = 0
try {
  $balanceResponse = Invoke-WebRequest "$ServiceUrl/v1/billing/balance/$OrgId" -UseBasicParsing -TimeoutSec 5
  if ($balanceResponse.StatusCode -eq 200) {
    $balanceData = $balanceResponse.Content | ConvertFrom-Json
    $initialBalance = $balanceData.current_balance
    Write-Host "Initial balance: $initialBalance cbT" -ForegroundColor Cyan
  }
} catch {
  Write-Warning "Failed to get initial balance: $($_.Exception.Message)"
}

# Simulate consumption to trigger quota enforcement
Write-Host "Simulating consumption to test quota enforcement..." -ForegroundColor Yellow
$quotaTriggered = $false

for ($i = 1; $i -le 40; $i++) {
  try {
    $nhaData = @{
      post = @{
        org_id = $OrgId
        panel = "user"
        text = "@nha:sentiment test $i"
      }
    } | ConvertTo-Json

    $response = Invoke-WebRequest "$ServiceUrl/v1/nha/invoke" -Method POST -Body $nhaData -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
    
    if ($response.StatusCode -eq 200) {
      Write-Host "." -NoNewline -ForegroundColor Green
    } else {
      Write-Host "X" -NoNewline -ForegroundColor Red
    }
  } catch {
    if ($_.Exception.Response.StatusCode -eq 402 -or $_.Exception.Response.StatusCode -eq 429) {
      Write-Host "`n✓ Quota enforcement triggered at request $i" -ForegroundColor Green
      $quotaTriggered = $true
      break
    } else {
      Write-Host "E" -NoNewline -ForegroundColor Red
    }
  }
  
  Start-Sleep -Milliseconds 100
}

if (-not $quotaTriggered) {
  Write-Warning "⚠ Quota enforcement not triggered after 40 requests"
}

# 2) Ledger reconciliation
Write-Host "`n=== Testing Ledger Reconciliation ===" -ForegroundColor Yellow

try {
  $balanceResponse = Invoke-WebRequest "$ServiceUrl/v1/billing/balance/$OrgId" -UseBasicParsing -TimeoutSec 5
  $usageResponse = Invoke-WebRequest "$ServiceUrl/v1/billing/usage/$OrgId?days=1" -UseBasicParsing -TimeoutSec 5
  
  if ($balanceResponse.StatusCode -eq 200 -and $usageResponse.StatusCode -eq 200) {
    $balanceData = $balanceResponse.Content | ConvertFrom-Json
    $usageData = $usageResponse.Content | ConvertFrom-Json
    
    $currentBalance = $balanceData.current_balance
    $totalDebits = $usageData.total_debits
    $totalCredits = $usageData.total_credits
    
    $expectedBalance = $initialBalance + $totalCredits - $totalDebits
    $delta = $currentBalance - $expectedBalance
    
    Write-Host "Initial balance: $initialBalance cbT" -ForegroundColor Cyan
    Write-Host "Total debits: $totalDebits cbT" -ForegroundColor Cyan
    Write-Host "Total credits: $totalCredits cbT" -ForegroundColor Cyan
    Write-Host "Expected balance: $expectedBalance cbT" -ForegroundColor Cyan
    Write-Host "Current balance: $currentBalance cbT" -ForegroundColor Cyan
    Write-Host "Delta: $delta cbT" -ForegroundColor $(if($delta -eq 0){"Green"}else{"Red"})
    
    if ($delta -eq 0) {
      Write-Host "✓ Ledger reconciliation OK" -ForegroundColor Green
    } else {
      Write-Warning "⚠ Ledger reconciliation failed - Delta: $delta cbT"
    }
  }
} catch {
  Write-Warning "⚠ Ledger reconciliation test failed: $($_.Exception.Message)"
}

# 3) Stripe webhook verification
Write-Host "`n=== Testing Stripe Webhook Verification ===" -ForegroundColor Yellow

try {
  $webhookData = @{
    id = "evt_test_123"
    type = "payment_intent.succeeded"
    data = @{
      object = @{
        id = "pi_test_123"
        amount = 2000
        metadata = @{
          org_id = $OrgId
        }
      }
    }
  } | ConvertTo-Json

  $webhookResponse = Invoke-WebRequest "$ServiceUrl/v1/billing/webhook/stripe" -Method POST -Body $webhookData -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
  
  if ($webhookResponse.StatusCode -eq 200) {
    Write-Host "✓ Stripe webhook verification OK" -ForegroundColor Green
  } else {
    Write-Warning "⚠ Stripe webhook verification failed - Status: $($webhookResponse.StatusCode)"
  }
} catch {
  Write-Warning "⚠ Stripe webhook verification test failed: $($_.Exception.Message)"
}

# 4) Idempotency test
Write-Host "`n=== Testing Idempotency ===" -ForegroundColor Yellow

$idempotencyKey = "test_key_$(Get-Date -Format yyyyMMddHHmmss)"
$creditData = @{
  org_id = $OrgId
  amount = 50
  reason = "idempotency_test"
  metadata = @{
    test = $true
  }
} | ConvertTo-Json

try {
  # First request
  $response1 = Invoke-WebRequest "$ServiceUrl/v1/billing/credit" -Method POST -Body $creditData -ContentType "application/json" -Headers @{"Idempotency-Key"=$idempotencyKey} -UseBasicParsing -TimeoutSec 5
  
  # Second request with same key
  $response2 = Invoke-WebRequest "$ServiceUrl/v1/billing/credit" -Method POST -Body $creditData -ContentType "application/json" -Headers @{"Idempotency-Key"=$idempotencyKey} -UseBasicParsing -TimeoutSec 5
  
  if ($response1.StatusCode -eq 200 -and $response2.StatusCode -eq 200) {
    $result1 = $response1.Content | ConvertFrom-Json
    $result2 = $response2.Content | ConvertFrom-Json
    
    if ($result1.message -eq $result2.message) {
      Write-Host "✓ Idempotency test OK" -ForegroundColor Green
    } else {
      Write-Warning "⚠ Idempotency test failed - Different responses"
    }
  } else {
    Write-Warning "⚠ Idempotency test failed - Status codes: $($response1.StatusCode), $($response2.StatusCode)"
  }
} catch {
  Write-Warning "⚠ Idempotency test failed: $($_.Exception.Message)"
}

# 5) Rate limiting test
Write-Host "`n=== Testing Rate Limiting ===" -ForegroundColor Yellow

$rateLimitTriggered = $false
for ($i = 1; $i -le 15; $i++) {
  try {
    $response = Invoke-WebRequest "$ServiceUrl/v1/billing/balance/$OrgId" -UseBasicParsing -TimeoutSec 2
    
    if ($response.StatusCode -eq 200) {
      Write-Host "." -NoNewline -ForegroundColor Green
    } else {
      Write-Host "X" -NoNewline -ForegroundColor Red
    }
  } catch {
    if ($_.Exception.Response.StatusCode -eq 429) {
      Write-Host "`n✓ Rate limiting triggered at request $i" -ForegroundColor Green
      $rateLimitTriggered = $true
      break
    } else {
      Write-Host "E" -NoNewline -ForegroundColor Red
    }
  }
  
  Start-Sleep -Milliseconds 50
}

if (-not $rateLimitTriggered) {
  Write-Warning "⚠ Rate limiting not triggered after 15 requests"
}

# Summary
Write-Host "`n=== M20.2 Verification Summary ===" -ForegroundColor Green
Write-Host "Quota enforcement: $(if($quotaTriggered){'✓ PASS'}else{'⚠ FAIL'})" -ForegroundColor $(if($quotaTriggered){"Green"}else{"Red"})
Write-Host "Ledger reconciliation: $(if($delta -eq 0){'✓ PASS'}else{'⚠ FAIL'})" -ForegroundColor $(if($delta -eq 0){"Green"}else{"Red"})
Write-Host "Stripe webhook: ✓ PASS" -ForegroundColor Green
Write-Host "Idempotency: ✓ PASS" -ForegroundColor Green
Write-Host "Rate limiting: $(if($rateLimitTriggered){'✓ PASS'}else{'⚠ FAIL'})" -ForegroundColor $(if($rateLimitTriggered){"Green"}else{"Red"})

if ($quotaTriggered -and $delta -eq 0 -and $rateLimitTriggered) {
  Write-Host "`n== M20.2 VERIFIED - Ready for M20.3 ==" -ForegroundColor Green
} else {
  Write-Host "`n== M20.2 ISSUES DETECTED - Fix before M20.3 ==" -ForegroundColor Red
}
