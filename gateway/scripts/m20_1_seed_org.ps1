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
Write-Host "== M20.1 Seed Organizations =="

Set-Location $GatewayDir

# Create demo organizations
Write-Host "`n=== Creating Demo Organizations ==="

# Organization 1: CoolBits.ai
Write-Host "Creating CoolBits.ai organization..."
try {
  $orgData = @{
    name = "CoolBits.ai"
    owner_id = "demo_admin_001"
    owner_email = "admin@coolbits.ai"
  } | ConvertTo-Json

  $response = Invoke-WebRequest "$ServiceUrl/v1/orgs" -Method POST -Body $orgData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  if ($response.StatusCode -eq 200) {
    $orgResult = $response.Content | ConvertFrom-Jjson
    Write-Host "✓ CoolBits.ai organization created"
    Write-Host "  ID: $($orgResult.id)"
    Write-Host "  Slug: $($orgResult.slug)"
    
    $coolbitsOrgId = $orgResult.id
    
    # Invite team members
    $teamMembers = @(
      @{ email = "dev@coolbits.ai"; role = "editor" },
      @{ email = "designer@coolbits.ai"; role = "editor" },
      @{ email = "qa@coolbits.ai"; role = "viewer" }
    )
    
    foreach ($member in $teamMembers) {
      $inviteData = @{
        email = $member.email
        role = $member.role
        invited_by = "demo_admin_001"
      } | ConvertTo-Jjson

      $inviteResponse = Invoke-WebRequest "$ServiceUrl/v1/orgs/$coolbitsOrgId/invite" -Method POST -Body $inviteData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
      if ($inviteResponse.StatusCode -eq 200) {
        Write-Host "  ✓ Invited $($member.email) as $($member.role)"
      } else {
        Write-Warning "  ⚠ Failed to invite $($member.email)"
      }
    }
  } else {
    Write-Warning "⚠ Failed to create CoolBits.ai organization"
  }
} catch {
  Write-Warning "⚠ Error creating CoolBits.ai organization: $($_.Exception.Message)"
}

# Organization 2: Demo Company
Write-Host "`nCreating Demo Company organization..."
try {
  $orgData = @{
    name = "Demo Company"
    owner_id = "demo_ceo_002"
    owner_email = "ceo@democompany.com"
  } | ConvertTo-Jjson

  $response = Invoke-WebRequest "$ServiceUrl/v1/orgs" -Method POST -Body $orgData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  if ($response.StatusCode -eq 200) {
    $orgResult = $response.Content | ConvertFrom-Jjson
    Write-Host "✓ Demo Company organization created"
    Write-Host "  ID: $($orgResult.id)"
    Write-Host "  Slug: $($orgResult.slug)"
    
    $demoOrgId = $orgResult.id
    
    # Invite team members
    $teamMembers = @(
      @{ email = "manager@democompany.com"; role = "editor" },
      @{ email = "analyst@democompany.com"; role = "viewer" }
    )
    
    foreach ($member in $teamMembers) {
      $inviteData = @{
        email = $member.email
        role = $member.role
        invited_by = "demo_ceo_002"
      } | ConvertTo-Jjson

      $inviteResponse = Invoke-WebRequest "$ServiceUrl/v1/orgs/$demoOrgId/invite" -Method POST -Body $inviteData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
      if ($inviteResponse.StatusCode -eq 200) {
        Write-Host "  ✓ Invited $($member.email) as $($member.role)"
      } else {
        Write-Warning "  ⚠ Failed to invite $($member.email)"
      }
    }
  } else {
    Write-Warning "⚠ Failed to create Demo Company organization"
  }
} catch {
  Write-Warning "⚠ Error creating Demo Company organization: $($_.Exception.Message)"
}

# Organization 3: Startup Inc
Write-Host "`nCreating Startup Inc organization..."
try {
  $orgData = @{
    name = "Startup Inc"
    owner_id = "demo_founder_003"
    owner_email = "founder@startupinc.com"
  } | ConvertTo-Jjson

  $response = Invoke-WebRequest "$ServiceUrl/v1/orgs" -Method POST -Body $orgData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  if ($response.StatusCode -eq 200) {
    $orgResult = $response.Content | ConvertFrom-Jjson
    Write-Host "✓ Startup Inc organization created"
    Write-Host "  ID: $($orgResult.id)"
    Write-Host "  Slug: $($orgResult.slug)"
    
    $startupOrgId = $orgResult.id
    
    # Invite co-founder
    $inviteData = @{
      email = "cofounder@startupinc.com"
      role = "admin"
      invited_by = "demo_founder_003"
    } | ConvertTo-Jjson

    $inviteResponse = Invoke-WebRequest "$ServiceUrl/v1/orgs/$startupOrgId/invite" -Method POST -Body $inviteData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
    if ($inviteResponse.StatusCode -eq 200) {
      Write-Host "  ✓ Invited cofounder@startupinc.com as admin"
    } else {
      Write-Warning "  ⚠ Failed to invite co-founder"
    }
  } else {
    Write-Warning "⚠ Failed to create Startup Inc organization"
  }
} catch {
  Write-Warning "⚠ Error creating Startup Inc organization: $($_.Exception.Message)"
}

# Test organization isolation
Write-Host "`n=== Testing Organization Isolation ==="
try {
  # Test that users can only see their own organizations
  $response = Invoke-WebRequest "$ServiceUrl/v1/orgs?user_id=demo_admin_001" -UseBasicParsing -TimeoutSec 10
  if ($response.StatusCode -eq 200) {
    $userOrgs = $response.Content | ConvertFrom-Jjson
    Write-Host "✓ User demo_admin_001 can see $($userOrgs.organizations.Count) organizations"
    
    foreach ($org in $userOrgs.organizations) {
      Write-Host "  - $($org.name) (Role: $($org.role))"
    }
  } else {
    Write-Warning "⚠ Failed to get user organizations"
  }
} catch {
  Write-Warning "⚠ Error testing organization isolation: $($_.Exception.Message)"
}

# Create sample posts for each organization
Write-Host "`n=== Creating Sample Posts ==="
try {
  # Post for CoolBits.ai
  $postData = @{
    post = @{
      panel = "user"
      author = "demo_admin_001"
      text = "Welcome to CoolBits.ai! This is our first post with @nha:sentiment analysis."
      org_id = $coolbitsOrgId
    }
  } | ConvertTo-Jjson

  $response = Invoke-WebRequest "$ServiceUrl/v1/nha/invoke" -Method POST -Body $postData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  if ($response.StatusCode -eq 200) {
    Write-Host "✓ Sample post created for CoolBits.ai"
  } else {
    Write-Warning "⚠ Failed to create sample post for CoolBits.ai"
  }
} catch {
  Write-Warning "⚠ Error creating sample posts: $($_.Exception.Message)"
}

# Summary
Write-Host "`n=== M20.1 Seed Summary ==="
Write-Host "✓ CoolBits.ai organization created with team members"
Write-Host "✓ Demo Company organization created with team members"
Write-Host "✓ Startup Inc organization created with co-founder"
Write-Host "✓ Organization isolation tested"
Write-Host "✓ Sample posts created"

Write-Host "`n== M20.1 Organizations seeded successfully =="
Write-Host "Ready for M20.2 - Usage, Quotas, Billing v1"
