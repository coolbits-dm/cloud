# CoolBits.ai Doctor Script - Non-Interactive Health Check
# ========================================================

param([int]$Wait=0)

$ok = $true
$BASE = $null

Write-Host "🔍 CoolBits.ai Doctor - Non-Interactive Health Check"
Write-Host "====================================================="

# Check runtime configuration
try {
    if (Test-Path ".runtime.json") {
        $rt = Get-Content .runtime.json | ConvertFrom-Json
        $BASE = "http://127.0.0.1:$($rt.port)"
        Write-Host "✅ Runtime config found: $BASE"
    } else {
        Write-Host "⚠️  No .runtime.json found - using detected ports"
        # Auto-detect running services
        $ports = @(8080, 8100, 3001, 8000)
        $BASE = $null
        foreach ($p in $ports) {
            if ((Test-NetConnection -ComputerName 127.0.0.1 -Port $p -InformationLevel Quiet)) {
                $BASE = "http://127.0.0.1:$p"
                Write-Host "✅ Auto-detected service on port $p"
                break
            }
        }
        if (-not $BASE) {
            $BASE = "http://127.0.0.1:8080"  # fallback to main dashboard
        }
    }
} catch { 
    $ok = $false
    Write-Host "❌ Runtime config FAIL"
}

# Health checks
if ($BASE) {
    Write-Host "`n🏥 Health Checks:"
    Write-Host "================="
    
    # API Status
    try { 
        $status = Invoke-RestMethod "$BASE/api/services/status" -TimeoutSec 3
        Write-Host "✅ /api/services/status OK"
    } catch { 
        $ok = $false
        Write-Host "❌ /api/services/status FAIL"
    }
    
    # Health endpoint
    try { 
        Invoke-RestMethod "$BASE/api/health" -TimeoutSec 3 | Out-Null
        Write-Host "✅ /api/health OK"
    } catch { 
        Write-Host "⚠️  /api/health missing"
    }
    
    # GPU Check
    try { 
        $gpu = Invoke-RestMethod "$BASE/api/check-gpu" -TimeoutSec 5
        Write-Host "✅ GPU Check OK"
    } catch { 
        Write-Host "❌ GPU check FAIL"
    }
    
    # GCloud Connection
    try { 
        $gcloud = Invoke-RestMethod "$BASE/api/connect-gcloud" -Method POST -TimeoutSec 8
        Write-Host "✅ GCloud connection OK"
    } catch { 
        Write-Host "❌ GCloud FAIL"
    }
    
    # RAG Test
    try { 
        $rag = Invoke-RestMethod "$BASE/api/test-rag" -Method POST -TimeoutSec 8
        Write-Host "✅ RAG system OK"
    } catch { 
        Write-Host "❌ RAG FAIL"
    }
}

# Port checks
Write-Host "`n🔌 Port Status:"
Write-Host "==============="
$ports = @(3001, 8000, 8080, 8100, 8101, 8102)
foreach ($p in $ports) {
    $isOpen = (Test-NetConnection -ComputerName 127.0.0.1 -Port $p -InformationLevel Quiet)
    $status = if ($isOpen) { "✅" } else { "❌" }
    Write-Host "$status Port $p : $(if($isOpen){'OPEN'}else{'CLOSED'})"
}

# Bridge specific check (port 8100)
if ((Test-NetConnection -ComputerName 127.0.0.1 -Port 8100 -InformationLevel Quiet)) {
    try { 
        $bridge = Invoke-RestMethod "http://127.0.0.1:8100/health" -TimeoutSec 3
        Write-Host "✅ Bridge 8100 healthy"
    } catch { 
        Write-Host "⚠️  Bridge 8100 responding but health endpoint issues"
    }
} else { 
    Write-Host "❌ Bridge 8100 unavailable"
}

if ($Wait -gt 0) { 
    Write-Host "`n⏳ Waiting $Wait seconds..."
    Start-Sleep $Wait 
}

Write-Host "`n📊 FINAL STATUS: $(if($ok){'✅ OK'}else{'❌ BROKEN'})"
Write-Host "====================================================="

return $ok
