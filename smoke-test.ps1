#!/usr/bin/env powershell
# Smoke script pentru verificări rapide după boot
# Usage: .\smoke-test.ps1

param(
    [switch]$Verbose
)

function Write-TestResult {
    param([string]$Test, [bool]$Passed, [string]$Details = "")
    $status = if ($Passed) { "✅" } else { "❌" }
    $color = if ($Passed) { "Green" } else { "Red" }
    Write-Host "$status $Test" -ForegroundColor $color
    if ($Details -and $Verbose) {
        Write-Host "   $Details" -ForegroundColor Gray
    }
}

Write-Host "🧪 CoolBits Admin Console - Smoke Test" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# 1) Check runtime.json exists
$runtimeExists = Test-Path ".runtime.json"
Write-TestResult "Runtime file exists" $runtimeExists

if (-not $runtimeExists) {
    Write-Host "❌ .runtime.json not found. Server may not be running." -ForegroundColor Red
    exit 1
}

# 2) Read runtime info
try {
    $rt = Get-Content .runtime.json | ConvertFrom-Json
    $baseUrl = "http://127.0.0.1:$($rt.port)"
    Write-TestResult "Runtime info loaded" $true "Port: $($rt.port), Node: $($rt.node)"
} catch {
    Write-TestResult "Runtime info loaded" $false $_.Exception.Message
    exit 1
}

# 3) Test port connectivity
try {
    $connection = Test-NetConnection -ComputerName 127.0.0.1 -Port $rt.port -WarningAction SilentlyContinue
    Write-TestResult "Port connectivity" $connection.TcpTestSucceeded
} catch {
    Write-TestResult "Port connectivity" $false $_.Exception.Message
}

# 4) Test API endpoints
$endpoints = @(
    @{ Path = "/api/status"; Method = "GET"; Name = "Status endpoint" },
    @{ Path = "/api/board/members"; Method = "GET"; Name = "Board members" },
    @{ Path = "/api/history"; Method = "GET"; Name = "History endpoint" },
    @{ Path = "/api/check-gpu"; Method = "GET"; Name = "GPU check" }
)

foreach ($endpoint in $endpoints) {
    try {
        if ($endpoint.Method -eq "GET") {
            $response = Invoke-RestMethod "$baseUrl$($endpoint.Path)" -TimeoutSec 5
        } else {
            $response = Invoke-RestMethod "$baseUrl$($endpoint.Path)" -Method $endpoint.Method -TimeoutSec 5
        }
        Write-TestResult $endpoint.Name $true
    } catch {
        Write-TestResult $endpoint.Name $false $_.Exception.Message
    }
}

# 5) Check system info
try {
    $status = Invoke-RestMethod "$baseUrl/api/status" -TimeoutSec 5
    Write-TestResult "System info" $true "CPU: $($status.cpu)%, Memory: $($status.memory)%, Uptime: $([math]::Round($status.version.uptime))s"
} catch {
    Write-TestResult "System info" $false $_.Exception.Message
}

# 6) Check Node.js and pnpm versions
try {
    $nodeVersion = node -v
    $pnpmVersion = pnpm -v
    Write-TestResult "Node.js version" $true $nodeVersion
    Write-TestResult "pnpm version" $true $pnpmVersion
} catch {
    Write-TestResult "Node.js/pnpm versions" $false $_.Exception.Message
}

# 7) Check git commit
try {
    $gitCommit = git rev-parse --short HEAD
    Write-TestResult "Git commit" $true $gitCommit
} catch {
    Write-TestResult "Git commit" $false $_.Exception.Message
}

Write-Host "`n🎯 Smoke test completed!" -ForegroundColor Cyan
Write-Host "For detailed output, run: .\smoke-test.ps1 -Verbose" -ForegroundColor Gray
