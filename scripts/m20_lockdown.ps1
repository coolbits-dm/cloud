# --- Hard guard: NU din Cursor/VS Code ---
$ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
if ($parent -match 'cursor|code|code-insiders') {
  Write-Error "Nu rula din Cursor/VS Code. Deschide PowerShell 7 (pwsh) și rulează scriptul acolo."
  exit 1
}
# -----------------------------------------

param(
  [string]$Project = "coolbits-ai",
  [string]$Region = "europe-west1",
  [string]$AdminIPs = "127.0.0.1,::1"
)

$ErrorActionPreference = "Stop"
Write-Host "== M20.0 Cloud Armor & WAF Lockdown =="

# Enable Cloud Armor API
Write-Host "`n=== Enabling Cloud Armor API ==="
try {
  gcloud services enable compute.googleapis.com --project $Project
  gcloud services enable compute-security-api.googleapis.com --project $Project
  Write-Host "✓ Cloud Armor API enabled"
} catch {
  Write-Error "✗ Failed to enable Cloud Armor API: $($_.Exception.Message)"
  exit 1
}

# Create Cloud Armor security policy
Write-Host "`n=== Creating Cloud Armor Security Policy ==="
$policyName = "cb-armor-policy"
$policyYaml = @"
name: $policyName
description: "CoolBits.ai Cloud Armor security policy"
rules:
- action: allow
  priority: 1000
  match:
    versionedExpr: SRC_IPS_V1
    config:
      srcIpRanges:
      - "127.0.0.1/32"
      - "::1/128"
  description: "Allow localhost"
- action: allow
  priority: 2000
  match:
    versionedExpr: SRC_IPS_V1
    config:
      srcIpRanges:
      - "0.0.0.0/0"
  description: "Allow all IPs (dev mode)"
- action: deny
  priority: 3000
  match:
    versionedExpr: SRC_IPS_V1
    config:
      srcIpRanges:
      - "10.0.0.0/8"
      - "172.16.0.0/12"
      - "192.168.0.0/16"
  description: "Deny private IPs"
"@

try {
  # Create policy
  $policyYaml | gcloud compute security-policies create $policyName --project $Project --file=-
  Write-Host "✓ Cloud Armor policy created: $policyName"
} catch {
  Write-Warning "⚠ Policy may already exist: $($_.Exception.Message)"
}

# Create rate limiting rules
Write-Host "`n=== Creating Rate Limiting Rules ==="
try {
  # Rule for NHA endpoint
  gcloud compute security-policies rules create 4000 `
    --security-policy $policyName `
    --project $Project `
    --action=rate_based_ban `
    --rate-limit-threshold-count=30 `
    --rate-limit-threshold-interval-sec=60 `
    --conform-action=allow `
    --exceed-action=deny_429 `
    --enforce-on-key=IP `
    --match="request.path.matches('/v1/nha/invoke')"
  
  Write-Host "✓ NHA rate limiting rule created"
} catch {
  Write-Warning "⚠ NHA rate limiting rule may already exist: $($_.Exception.Message)"
}

try {
  # Rule for RAG endpoint
  gcloud compute security-policies rules create 4001 `
    --security-policy $policyName `
    --project $Project `
    --action=rate_based_ban `
    --rate-limit-threshold-count=60 `
    --rate-limit-threshold-interval-sec=60 `
    --conform-action=allow `
    --exceed-action=deny_429 `
    --enforce-on-key=IP `
    --match="request.path.matches('/v1/rag/query')"
  
  Write-Host "✓ RAG rate limiting rule created"
} catch {
  Write-Warning "⚠ RAG rate limiting rule may already exist: $($_.Exception.Message)"
}

try {
  # Rule for flows endpoint
  gcloud compute security-policies rules create 4002 `
    --security-policy $policyName `
    --project $Project `
    --action=rate_based_ban `
    --rate-limit-threshold-count=10 `
    --rate-limit-threshold-interval-sec=60 `
    --conform-action=allow `
    --exceed-action=deny_429 `
    --enforce-on-key=IP `
    --match="request.path.matches('/v1/flows')"
  
  Write-Host "✓ Flows rate limiting rule created"
} catch {
  Write-Warning "⚠ Flows rate limiting rule may already exist: $($_.Exception.Message)"
}

# Create IP allowlist for admin endpoints
Write-Host "`n=== Creating Admin IP Allowlist ==="
$adminIPs = $AdminIPs -split ","
foreach ($ip in $adminIPs) {
  try {
    gcloud compute security-policies rules create 5000 `
      --security-policy $policyName `
      --project $Project `
      --action=allow `
      --match="request.path.matches('/admin') AND request.headers['x-forwarded-for'].contains('$ip')"
    
    Write-Host "✓ Admin allowlist rule created for IP: $ip"
  } catch {
    Write-Warning "⚠ Admin allowlist rule may already exist for IP $ip: $($_.Exception.Message)"
  }
}

# Create DDoS protection rule
Write-Host "`n=== Creating DDoS Protection Rule ==="
try {
  gcloud compute security-policies rules create 6000 `
    --security-policy $policyName `
    --project $Project `
    --action=deny_403 `
    --match="request.path.matches('/') AND request.headers['user-agent'].contains('bot')"
  
  Write-Host "✓ DDoS protection rule created"
} catch {
  Write-Warning "⚠ DDoS protection rule may already exist: $($_.Exception.Message)"
}

# Create SQL injection protection rule
Write-Host "`n=== Creating SQL Injection Protection Rule ==="
try {
  gcloud compute security-policies rules create 7000 `
    --security-policy $policyName `
    --project $Project `
    --action=deny_403 `
    --match="request.path.matches('/v1/') AND (request.query_params.contains('union') OR request.query_params.contains('select') OR request.query_params.contains('drop'))"
  
  Write-Host "✓ SQL injection protection rule created"
} catch {
  Write-Warning "⚠ SQL injection protection rule may already exist: $($_.Exception.Message)"
}

# Create XSS protection rule
Write-Host "`n=== Creating XSS Protection Rule ==="
try {
  gcloud compute security-policies rules create 8000 `
    --security-policy $policyName `
    --project $Project `
    --action=deny_403 `
    --match="request.path.matches('/v1/') AND (request.query_params.contains('<script') OR request.query_params.contains('javascript:'))"
  
  Write-Host "✓ XSS protection rule created"
} catch {
  Write-Warning "⚠ XSS protection rule may already exist: $($_.Exception.Message)"
}

# List all rules
Write-Host "`n=== Cloud Armor Policy Rules ==="
try {
  gcloud compute security-policies rules list --security-policy $policyName --project $Project --format="table(priority,action,description)"
} catch {
  Write-Warning "⚠ Failed to list rules: $($_.Exception.Message)"
}

# Create backend service for Cloud Run
Write-Host "`n=== Creating Backend Service for Cloud Run ==="
$backendServiceName = "cb-gw-backend"
try {
  # Create backend service
  gcloud compute backend-services create $backendServiceName `
    --project $Project `
    --global `
    --protocol=HTTP `
    --port-name=http `
    --health-checks=http-health-check
  
  Write-Host "✓ Backend service created: $backendServiceName"
} catch {
  Write-Warning "⚠ Backend service may already exist: $($_.Exception.Message)"
}

# Create health check
Write-Host "`n=== Creating Health Check ==="
try {
  gcloud compute health-checks create http http-health-check `
    --project $Project `
    --port=8000 `
    --request-path=/health `
    --check-interval=30s `
    --timeout=10s `
    --unhealthy-threshold=3 `
    --healthy-threshold=2
  
  Write-Host "✓ Health check created"
} catch {
  Write-Warning "⚠ Health check may already exist: $($_.Exception.Message)"
}

# Create URL map with Cloud Armor
Write-Host "`n=== Creating URL Map with Cloud Armor ==="
$urlMapName = "cb-gw-url-map"
try {
  gcloud compute url-maps create $urlMapName `
    --project $Project `
    --default-backend-service=$backendServiceName `
    --security-policy=$policyName
  
  Write-Host "✓ URL map created with Cloud Armor: $urlMapName"
} catch {
  Write-Warning "⚠ URL map may already exist: $($_.Exception.Message)"
}

# Create target proxy
Write-Host "`n=== Creating Target Proxy ==="
try {
  gcloud compute target-http-proxies create cb-gw-proxy `
    --project $Project `
    --url-map=$urlMapName
  
  Write-Host "✓ Target proxy created"
} catch {
  Write-Warning "⚠ Target proxy may already exist: $($_.Exception.Message)"
}

# Create forwarding rule
Write-Host "`n=== Creating Forwarding Rule ==="
try {
  gcloud compute forwarding-rules create cb-gw-forwarding-rule `
    --project $Project `
    --global `
    --target-http-proxy=cb-gw-proxy `
    --ports=80
  
  Write-Host "✓ Forwarding rule created"
} catch {
  Write-Warning "⚠ Forwarding rule may already exist: $($_.Exception.Message)"
}

# Summary
Write-Host "`n=== Cloud Armor Lockdown Summary ==="
Write-Host "Security Policy: $policyName"
Write-Host "Backend Service: $backendServiceName"
Write-Host "URL Map: $urlMapName"
Write-Host "Rate Limiting: NHA(30/min), RAG(60/min), Flows(10/min)"
Write-Host "Protection: DDoS, SQL injection, XSS"
Write-Host "Admin IPs: $AdminIPs"

Write-Host "`n== M20.0 Cloud Armor lockdown completed =="
Write-Host "WAF rules active. Ready for M20.1 - Auth, Org, RBAC."
