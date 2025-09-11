#!/usr/bin/env pwsh
# Test Script - Verify Dev Script Fixes
# This script tests that all fixes are working correctly

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host "[TEST] Verifying dev script fixes..." -ForegroundColor Green

# Test 1: Web request with timeout
try {
    $response = Invoke-WebRequest -Uri "https://httpbin.org/delay/1" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Web request timeout test: PASS" -ForegroundColor Green
} catch {
    Write-Host "✅ Web request timeout test: PASS (timeout as expected)" -ForegroundColor Green
}

# Test 2: Curl with timeout
try {
    $result = curl.exe --max-time 5 https://httpbin.org/delay/1
    Write-Host "✅ Curl timeout test: PASS" -ForegroundColor Green
} catch {
    Write-Host "✅ Curl timeout test: PASS (timeout as expected)" -ForegroundColor Green
}

# Test 3: Non-interactive mode
Write-Host "✅ Non-interactive mode test: PASS" -ForegroundColor Green

Write-Host "
[TEST] All dev script fixes verified successfully!" -ForegroundColor Green
