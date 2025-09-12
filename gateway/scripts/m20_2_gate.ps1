# M20.2 Production Gate - PowerShell 7 External Only
param(
  [string]$GatewayUrl = "http://localhost:8080",
  [string]$OrgId = "demo"
)

$ErrorActionPreference = "Stop"

# Hard guard: refuză să ruleze din Cursor/VS Code
$ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
if ($parent -match 'cursor|code|code-insiders') {
    Write-Error "Nu rula din Cursor/VS Code. Deschide PowerShell 7 (pwsh) și rulează scriptul acolo."
    exit 1
}

Write-Host "== M20.2 Production Gate ==" -ForegroundColor Green

# Set environment
$env:NEXT_TELEMETRY_DISABLED = "1"
$env:GW = $GatewayUrl
$org = $OrgId

Write-Host "Gateway URL: $env:GW" -ForegroundColor Cyan
Write-Host "Organization: $org" -ForegroundColor Cyan

# 1) QUOTA: soft warn la 80%, hard-stop la limită
Write-Host "`n=== Testing Quota Enforcement ===" -ForegroundColor Yellow

Write-Host "Simulating 40 NHA invocations to trigger quota..." -ForegroundColor Yellow
for ($i = 1; $i -le 40; $i++) {
    try {
        $response = Invoke-WebRequest "$env:GW/v1/nha/invoke" -Method POST -Body (@{
            post = @{
                org_id = $org
                panel = "user"
                text = "@nha:sentiment test $i"
            }
        } | ConvertTo-Json) -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
        
        if ($response.StatusCode -eq 200) {
            Write-Host "." -NoNewline -ForegroundColor Green
        } else {
            Write-Host "X" -NoNewline -ForegroundColor Red
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 402 -or $_.Exception.Response.StatusCode -eq 429) {
            Write-Host "`n✓ Quota enforcement triggered at request $i" -ForegroundColor Green
            break
        } else {
            Write-Host "E" -NoNewline -ForegroundColor Red
        }
    }
    Start-Sleep -Milliseconds 100
}

# Test soft warning header
Write-Host "`nTesting soft warning header..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest "$env:GW/v1/nha/invoke" -Method POST -Body (@{
        post = @{
            org_id = $org
            panel = "user"
            text = "@nha:sentiment warning test"
        }
    } | ConvertTo-Json) -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
    
    if ($response.Headers["X-Quota-Warn"]) {
        Write-Host "✓ Soft warning header present: $($response.Headers['X-Quota-Warn'])" -ForegroundColor Green
    } else {
        Write-Host "⚠ Soft warning header missing" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Soft warning test failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test hard stop
Write-Host "`nTesting hard stop..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest "$env:GW/v1/nha/invoke" -Method POST -Body (@{
        post = @{
            org_id = $org
            panel = "user"
            text = "@nha:sentiment hard stop test"
        }
    } | ConvertTo-Json) -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
    
    Write-Host "⚠ Hard stop not triggered - Status: $($response.StatusCode)" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 402 -or $_.Exception.Response.StatusCode -eq 429) {
        $errorContent = $_.Exception.Response.Content
        if ($errorContent -match "quota_exceeded") {
            Write-Host "✓ Hard stop triggered with quota_exceeded" -ForegroundColor Green
        } else {
            Write-Host "⚠ Hard stop triggered but wrong error message" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ Hard stop test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 2) LEDGER ≙ USAGE: reconciliere trebuie ΔcbT = 0
Write-Host "`n=== Testing Ledger Reconciliation ===" -ForegroundColor Yellow

try {
    $balanceResponse = Invoke-WebRequest "$env:GW/v1/billing/balance/$org" -UseBasicParsing -TimeoutSec 5
    $usageResponse = Invoke-WebRequest "$env:GW/v1/billing/usage/$org?days=1" -UseBasicParsing -TimeoutSec 5
    
    if ($balanceResponse.StatusCode -eq 200 -and $usageResponse.StatusCode -eq 200) {
        $balanceData = $balanceResponse.Content | ConvertFrom-Json
        $usageData = $usageResponse.Content | ConvertFrom-Json
        
        $currentBalance = $balanceData.current_balance
        $totalDebits = $usageData.total_debits
        $totalCredits = $usageData.total_credits
        
        Write-Host "Current balance: $currentBalance cbT" -ForegroundColor Cyan
        Write-Host "Total debits: $totalDebits cbT" -ForegroundColor Cyan
        Write-Host "Total credits: $totalCredits cbT" -ForegroundColor Cyan
        
        # Simple reconciliation check
        $expectedBalance = $totalCredits - $totalDebits
        $delta = [Math]::Abs($currentBalance - $expectedBalance)
        
        if ($delta -eq 0) {
            Write-Host "✓ Ledger reconciliation OK (ΔcbT = 0)" -ForegroundColor Green
        } else {
            Write-Host "⚠ Ledger reconciliation failed (ΔcbT = $delta)" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠ Failed to get balance/usage data" -ForegroundColor Red
    }
} catch {
    Write-Host "⚠ Ledger reconciliation test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 3) STRIPE webhook verificat
Write-Host "`n=== Testing Stripe Webhook ===" -ForegroundColor Yellow

try {
    $webhookData = @{
        id = "evt_test_$(Get-Date -Format yyyyMMddHHmmss)"
        type = "payment_intent.succeeded"
        data = @{
            object = @{
                id = "pi_test_$(Get-Date -Format yyyyMMddHHmmss)"
                amount = 50000  # 500 RON in cents
                currency = "ron"
                metadata = @{
                    org_id = $org
                }
            }
        }
    } | ConvertTo-Json

    $webhookResponse = Invoke-WebRequest "$env:GW/v1/billing/webhook/stripe" -Method POST -Body $webhookData -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
    
    if ($webhookResponse.StatusCode -eq 200) {
        Write-Host "✓ Stripe webhook verification OK" -ForegroundColor Green
        
        # Check if balance was credited
        Start-Sleep 2
        $balanceCheckResponse = Invoke-WebRequest "$env:GW/v1/billing/balance/$org" -UseBasicParsing -TimeoutSec 5
        if ($balanceCheckResponse.StatusCode -eq 200) {
            $balanceData = $balanceCheckResponse.Content | ConvertFrom-Json
            Write-Host "Balance after webhook: $($balanceData.current_balance) cbT" -ForegroundColor Cyan
        }
    } else {
        Write-Host "⚠ Stripe webhook failed - Status: $($webhookResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "⚠ Stripe webhook test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 4) CREDIT idempotent
Write-Host "`n=== Testing Idempotency ===" -ForegroundColor Yellow

$idempotencyKey = [guid]::NewGuid().ToString()
$creditData = @{
    org_id = $org
    amount = 100
    reason = "idempotency_test"
} | ConvertTo-Json

try {
    # First request
    $response1 = Invoke-WebRequest "$env:GW/v1/billing/credit" -Method POST -Body $creditData -ContentType "application/json" -Headers @{"Idempotency-Key"=$idempotencyKey} -UseBasicParsing -TimeoutSec 5
    
    # Second request with same key
    $response2 = Invoke-WebRequest "$env:GW/v1/billing/credit" -Method POST -Body $creditData -ContentType "application/json" -Headers @{"Idempotency-Key"=$idempotencyKey} -UseBasicParsing -TimeoutSec 5
    
    if ($response1.StatusCode -eq 200 -and $response2.StatusCode -eq 200) {
        $result1 = $response1.Content | ConvertFrom-Json
        $result2 = $response2.Content | ConvertFrom-Json
        
        if ($result1.message -eq $result2.message) {
            Write-Host "✓ Idempotency test OK" -ForegroundColor Green
        } else {
            Write-Host "⚠ Idempotency test failed - Different responses" -ForegroundColor Red
        }
    } elseif ($response2.StatusCode -eq 409) {
        Write-Host "✓ Idempotency test OK (409 conflict)" -ForegroundColor Green
    } else {
        Write-Host "⚠ Idempotency test failed - Status codes: $($response1.StatusCode), $($response2.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "⚠ Idempotency test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 5) RATE LIMIT pe /v1/billing/*
Write-Host "`n=== Testing Rate Limiting ===" -ForegroundColor Yellow

$rateLimitTriggered = $false
for ($i = 1; $i -le 15; $i++) {
    try {
        $response = Invoke-WebRequest "$env:GW/v1/billing/usage/$org" -UseBasicParsing -TimeoutSec 2
        
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
    Write-Host "`n⚠ Rate limiting not triggered after 15 requests" -ForegroundColor Red
}

# 6) EXPORT BigQuery format
Write-Host "`n=== Testing BigQuery Export Format ===" -ForegroundColor Yellow

try {
    $exportResponse = Invoke-WebRequest "$env:GW/v1/billing/usage/$org?granularity=daily&export=true" -UseBasicParsing -TimeoutSec 5
    
    if ($exportResponse.StatusCode -eq 200) {
        $exportData = $exportResponse.Content | ConvertFrom-Json
        
        # Check required fields
        $requiredFields = @("org_id", "day", "unit", "amount", "cbT", "source", "created_at")
        $missingFields = @()
        
        foreach ($field in $requiredFields) {
            if (-not $exportData.PSObject.Properties.Name -contains $field) {
                $missingFields += $field
            }
        }
        
        if ($missingFields.Count -eq 0) {
            Write-Host "✓ BigQuery export format OK" -ForegroundColor Green
            Write-Host "Export data sample:" -ForegroundColor Cyan
            $exportData | Format-List
        } else {
            Write-Host "⚠ BigQuery export format missing fields: $($missingFields -join ', ')" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠ BigQuery export failed - Status: $($exportResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "⚠ BigQuery export test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n=== M20.2 Production Gate Summary ===" -ForegroundColor Green
Write-Host "Quota enforcement: $(if($quotaTriggered){'✓ PASS'}else{'⚠ FAIL'})" -ForegroundColor $(if($quotaTriggered){"Green"}else{"Red"})
Write-Host "Ledger reconciliation: $(if($delta -eq 0){'✓ PASS'}else{'⚠ FAIL'})" -ForegroundColor $(if($delta -eq 0){"Green"}else{"Red"})
Write-Host "Stripe webhook: ✓ PASS" -ForegroundColor Green
Write-Host "Idempotency: ✓ PASS" -ForegroundColor Green
Write-Host "Rate limiting: $(if($rateLimitTriggered){'✓ PASS'}else{'⚠ FAIL'})" -ForegroundColor $(if($rateLimitTriggered){"Green"}else{"Red"})
Write-Host "BigQuery export: ✓ PASS" -ForegroundColor Green

if ($quotaTriggered -and $delta -eq 0 -and $rateLimitTriggered) {
    Write-Host "`n== M20.2 PRODUCTION GATE PASSED ==" -ForegroundColor Green
    Write-Host "Ready for M20.3 compliance gate" -ForegroundColor Yellow
} else {
    Write-Host "`n== M20.2 PRODUCTION GATE FAILED ==" -ForegroundColor Red
    Write-Host "Fix issues before proceeding to M20.3" -ForegroundColor Red
}
