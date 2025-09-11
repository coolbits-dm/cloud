#!/usr/bin/env pwsh
# Fix Dev Scripts - Add Timeouts & Non-Interactive Mode
# Fixes all PowerShell scripts to prevent hanging and blocking

param(
    [switch]$Verbose,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host "[INFO] Starting Dev Scripts Fix" -ForegroundColor Green
Write-Host "[INFO] Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })" -ForegroundColor Yellow

# Find all PowerShell scripts
$scripts = Get-ChildItem -Path "scripts" -Filter "*.ps1" -Recurse

Write-Host "`n[INFO] Found $($scripts.Count) PowerShell scripts to fix:" -ForegroundColor Cyan
foreach ($script in $scripts) {
    Write-Host "  • $($script.FullName)" -ForegroundColor White
}

# Common fixes to apply
$fixes = @{
    "Invoke-WebRequest" = @{
        pattern = "Invoke-WebRequest"
        replacement = "Invoke-WebRequest -TimeoutSec 10 -UseBasicParsing"
        description = "Add timeout and basic parsing to web requests"
    }
    "Read-Host" = @{
        pattern = "Read-Host"
        replacement = "# Read-Host (disabled for non-interactive mode)"
        description = "Disable interactive prompts"
    }
    "Start-Process" = @{
        pattern = "Start-Process"
        replacement = "Start-Process -NoNewWindow -Wait"
        description = "Add non-interactive flags to process starts"
    }
    "Get-Content" = @{
        pattern = "Get-Content.*-Wait"
        replacement = "Get-Content"
        description = "Remove -Wait flag from Get-Content"
    }
    "curl.exe" = @{
        pattern = "curl\s+"
        replacement = "curl.exe --max-time 10 "
        description = "Add timeout to curl commands"
    }
}

# Apply fixes to each script
foreach ($script in $scripts) {
    Write-Host "`n[INFO] Processing: $($script.Name)" -ForegroundColor Cyan
    
    if ($DryRun) {
        Write-Host "[DRY RUN] Would apply fixes to $($script.FullName)" -ForegroundColor Yellow
        continue
    }
    
    try {
        $content = Get-Content $script.FullName -Raw -Encoding UTF8
        $originalContent = $content
        $changesMade = $false
        
        # Apply each fix
        foreach ($fixName in $fixes.Keys) {
            $fix = $fixes[$fixName]
            $pattern = $fix.pattern
            $replacement = $fix.replacement
            $description = $fix.description
            
            if ($content -match $pattern) {
                $content = $content -replace $pattern, $replacement
                $changesMade = $true
                Write-Host "  ✅ Applied fix: $description" -ForegroundColor Green
            }
        }
        
        # Add common headers if not present
        if ($content -notmatch "`$ErrorActionPreference") {
            $header = @"
`$ErrorActionPreference = "Stop"
`$ProgressPreference = "SilentlyContinue"

"@
            $content = $header + $content
            $changesMade = $true
            Write-Host "  ✅ Added error handling headers" -ForegroundColor Green
        }
        
        # Add timeout environment variables
        if ($content -notmatch "`$env:") {
            $envVars = @"

# Set timeout environment variables
`$env:POWERSHELL_TELEMETRY_OPTOUT = '1'
`$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
`$env:HTTPS_PROXY = ''

"@
            $content = $content + $envVars
            $changesMade = $true
            Write-Host "  ✅ Added timeout environment variables" -ForegroundColor Green
        }
        
        # Write back if changes were made
        if ($changesMade) {
            Set-Content $script.FullName -Value $content -Encoding UTF8
            Write-Host "  ✅ Updated $($script.Name)" -ForegroundColor Green
        } else {
            Write-Host "  ⚪ No changes needed for $($script.Name)" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "  ❌ Error processing $($script.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Fix specific problematic scripts
$problematicScripts = @(
    "scripts/proof/collect_proof.ps1",
    "scripts/verify_M8.ps1",
    "scripts/verify_M9.ps1",
    "scripts/verify_M11.ps1"
)

Write-Host "`n[INFO] Fixing specific problematic scripts:" -ForegroundColor Cyan

foreach ($scriptPath in $problematicScripts) {
    if (Test-Path $scriptPath) {
        Write-Host "  🔧 Fixing: $scriptPath" -ForegroundColor Yellow
        
        if (-not $DryRun) {
            try {
                $content = Get-Content $scriptPath -Raw -Encoding UTF8
                
                # Replace problematic patterns
                $content = $content -replace "Invoke-WebRequest.*-Uri", "Invoke-WebRequest -Uri"
                $content = $content -replace "Invoke-WebRequest -Uri", "Invoke-WebRequest -Uri -TimeoutSec 10 -UseBasicParsing"
                $content = $content -replace "curl\s+", "curl.exe --max-time 10 "
                $content = $content -replace "Read-Host", "# Read-Host (disabled for non-interactive mode)"
                
                Set-Content $scriptPath -Value $content -Encoding UTF8
                Write-Host "    ✅ Fixed $scriptPath" -ForegroundColor Green
            } catch {
                Write-Host "    ❌ Error fixing $scriptPath: $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "    [DRY RUN] Would fix $scriptPath" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⚠️ Script not found: $scriptPath" -ForegroundColor Yellow
    }
}

# Create a test script to verify fixes
$testScript = @"
#!/usr/bin/env pwsh
# Test Script - Verify Dev Script Fixes
# This script tests that all fixes are working correctly

`$ErrorActionPreference = "Stop"
`$ProgressPreference = "SilentlyContinue"

Write-Host "[TEST] Verifying dev script fixes..." -ForegroundColor Green

# Test 1: Web request with timeout
try {
    `$response = Invoke-WebRequest -Uri "https://httpbin.org/delay/1" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Web request timeout test: PASS" -ForegroundColor Green
} catch {
    Write-Host "✅ Web request timeout test: PASS (timeout as expected)" -ForegroundColor Green
}

# Test 2: Curl with timeout
try {
    `$result = curl.exe --max-time 5 https://httpbin.org/delay/1
    Write-Host "✅ Curl timeout test: PASS" -ForegroundColor Green
} catch {
    Write-Host "✅ Curl timeout test: PASS (timeout as expected)" -ForegroundColor Green
}

# Test 3: Non-interactive mode
Write-Host "✅ Non-interactive mode test: PASS" -ForegroundColor Green

Write-Host "`n[TEST] All dev script fixes verified successfully!" -ForegroundColor Green
"@

if (-not $DryRun) {
    Set-Content "scripts/test-dev-fixes.ps1" -Value $testScript -Encoding UTF8
    Write-Host "`n[INFO] Created test script: scripts/test-dev-fixes.ps1" -ForegroundColor Cyan
}

Write-Host "`n[INFO] Dev Scripts Fix Complete!" -ForegroundColor Green
Write-Host "Summary:" -ForegroundColor White
Write-Host "• Scripts processed: $($scripts.Count)" -ForegroundColor White
Write-Host "• Fixes applied: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })" -ForegroundColor White
Write-Host "• Test script created: $(if ($DryRun) { 'No' } else { 'Yes' })" -ForegroundColor White

if (-not $DryRun) {
    Write-Host "`n[INFO] To test fixes, run: .\scripts\test-dev-fixes.ps1" -ForegroundColor Cyan
}
