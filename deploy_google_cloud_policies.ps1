# Google Cloud IAM & Organization Policies Deployment Script (PowerShell)
# Applies Policy Division decisions to Google Cloud infrastructure

# Configuration
$PROJECT_ID = "coolbits-ai"
$ORGANIZATION_ID = "0"  # Update with actual organization ID
$COMPANY = "COOL BITS SRL"
$CEO = "Andrei"

Write-Host "☁️ Google Cloud IAM & Organization Policies Deployment" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Company: $COMPANY" -ForegroundColor Yellow
Write-Host "CEO: $CEO" -ForegroundColor Yellow
Write-Host "Project: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Organization: $ORGANIZATION_ID" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Cyan

# Step 1: Create IAM Roles for Policy Division
Write-Host ""
Write-Host "🔐 Step 1: Creating IAM Roles for Policy Division" -ForegroundColor Green
Write-Host "--------------------------------------------------" -ForegroundColor Green

# Policy Administrator Role
$policyAdminRole = @"
title: Policy Administrator
description: Manages policies for coolbits.ai and cblm.ai
stage: GA
includedPermissions:
  - resourcemanager.organizations.get
  - resourcemanager.projects.get
  - iam.policies.get
  - iam.policies.set
  - iam.roles.get
  - iam.roles.list
"@

$policyAdminRole | Out-File -FilePath "policy_administrator_role.yaml" -Encoding UTF8

Write-Host "📋 Creating Policy Administrator role..." -ForegroundColor Yellow
gcloud iam roles create policyAdministrator --project=$PROJECT_ID --file=policy_administrator_role.yaml

# Security Reviewer Role
$securityReviewerRole = @"
title: Security Reviewer
description: Reviews security policies and compliance
stage: GA
includedPermissions:
  - securitycenter.assets.list
  - securitycenter.findings.list
  - cloudsecurityscanner.scans.list
  - accessapproval.requests.list
  - iam.roles.get
"@

$securityReviewerRole | Out-File -FilePath "security_reviewer_role.yaml" -Encoding UTF8

Write-Host "📋 Creating Security Reviewer role..." -ForegroundColor Yellow
gcloud iam roles create securityReviewer --project=$PROJECT_ID --file=security_reviewer_role.yaml

# AI Policy Administrator Role
$aiPolicyAdminRole = @"
title: AI Policy Administrator
description: Manages AI-specific policies and governance
stage: GA
includedPermissions:
  - aiplatform.models.list
  - aiplatform.endpoints.list
  - aiplatform.pipelines.list
  - discoveryengine.corpora.list
  - aiplatform.jobs.list
"@

$aiPolicyAdminRole | Out-File -FilePath "ai_policy_administrator_role.yaml" -Encoding UTF8

Write-Host "📋 Creating AI Policy Administrator role..." -ForegroundColor Yellow
gcloud iam roles create aiPolicyAdministrator --project=$PROJECT_ID --file=ai_policy_administrator_role.yaml

# Compliance Monitor Role
$complianceMonitorRole = @"
title: Compliance Monitor
description: Monitors policy compliance across all systems
stage: GA
includedPermissions:
  - logging.logs.list
  - monitoring.timeSeries.list
  - cloudaudit.auditLogs.list
  - iam.roles.get
  - resourcemanager.projects.get
"@

$complianceMonitorRole | Out-File -FilePath "compliance_monitor_role.yaml" -Encoding UTF8

Write-Host "📋 Creating Compliance Monitor role..." -ForegroundColor Yellow
gcloud iam roles create complianceMonitor --project=$PROJECT_ID --file=compliance_monitor_role.yaml

Write-Host "✅ IAM Roles created successfully" -ForegroundColor Green

# Step 2: Create Organization Policies
Write-Host ""
Write-Host "🏛️ Step 2: Creating Organization Policies" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green

# Security Policy for coolbits.ai
$coolbitsSecurityPolicy = @"
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allValues: ALLOW
  allowedValues:
    - coolbits.ai
    - coolbits.ro
"@

$coolbitsSecurityPolicy | Out-File -FilePath "coolbits_security_policy.yaml" -Encoding UTF8

Write-Host "📜 Creating coolbits.ai security policy..." -ForegroundColor Yellow
gcloud resource-manager org-policies set-policy --organization=$ORGANIZATION_ID coolbits_security_policy.yaml

# AI Governance Policy for cblm.ai
$cblmAiGovernancePolicy = @"
constraint: constraints/aiplatform.restrictNonAdminAPI
booleanPolicy:
  enforced: true
"@

$cblmAiGovernancePolicy | Out-File -FilePath "cblm_ai_governance_policy.yaml" -Encoding UTF8

Write-Host "📜 Creating cblm.ai governance policy..." -ForegroundColor Yellow
gcloud resource-manager org-policies set-policy --organization=$ORGANIZATION_ID cblm_ai_governance_policy.yaml

# Data Protection Policy
$dataProtectionPolicy = @"
constraint: constraints/storage.uniformBucketLevelAccess
booleanPolicy:
  enforced: true
"@

$dataProtectionPolicy | Out-File -FilePath "data_protection_policy.yaml" -Encoding UTF8

Write-Host "📜 Creating data protection policy..." -ForegroundColor Yellow
gcloud resource-manager org-policies set-policy --organization=$ORGANIZATION_ID data_protection_policy.yaml

Write-Host "✅ Organization Policies created successfully" -ForegroundColor Green

# Step 3: Assign IAM Permissions to Policy Division Agents
Write-Host ""
Write-Host "👥 Step 3: Assigning IAM Permissions to Policy Division Agents" -ForegroundColor Green
Write-Host "-------------------------------------------------------------" -ForegroundColor Green

# Assign permissions to oGrok08 (CISO)
Write-Host "🔐 Assigning permissions to oGrok08 (CISO)..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:ogrok08@coolbits.ai" --role="projects/$PROJECT_ID/roles/policyAdministrator"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:ogrok08@coolbits.ai" --role="projects/$PROJECT_ID/roles/securityReviewer"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:ogrok08@coolbits.ai" --role="roles/cloudaudit.auditLogViewer"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:ogrok08@coolbits.ai" --role="roles/monitoring.viewer"

# Assign permissions to oGrok09 (CAIO)
Write-Host "🤖 Assigning permissions to oGrok09 (CAIO)..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:ogrok09@coolbits.ai" --role="projects/$PROJECT_ID/roles/aiPolicyAdministrator"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:ogrok09@coolbits.ai" --role="roles/aiplatform.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:ogrok09@coolbits.ai" --role="roles/discoveryengine.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:ogrok09@coolbits.ai" --role="roles/ml.developer"

Write-Host "✅ Policy Division IAM permissions assigned" -ForegroundColor Green

# Step 4: Assign IAM Permissions to COOL BITS SRL Proprietary Functions
Write-Host ""
Write-Host "🏢 Step 4: Assigning IAM Permissions to COOL BITS SRL Proprietary Functions" -ForegroundColor Green
Write-Host "---------------------------------------------------------------------------" -ForegroundColor Green

# oVertex permissions
Write-Host "🔧 Assigning permissions to oVertex..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:oVertex@coolbits.ai" --role="roles/compute.viewer"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:oVertex@coolbits.ai" --role="roles/monitoring.viewer"

# oCursor permissions
Write-Host "💻 Assigning permissions to oCursor..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:oCursor@coolbits.ai" --role="roles/source.reader"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:oCursor@coolbits.ai" --role="roles/cloudbuild.viewer"

# oGrok permissions
Write-Host "🧠 Assigning permissions to oGrok..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:oGrok@coolbits.ai" --role="roles/aiplatform.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:oGrok@coolbits.ai" --role="roles/discoveryengine.admin"

# oGPT permissions
Write-Host "💬 Assigning permissions to oGPT..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:oGPT@coolbits.ai" --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:oGPT@coolbits.ai" --role="roles/discoveryengine.user"

# oMeta permissions (Future Phase)
Write-Host "🚀 Preparing permissions for oMeta (Future Phase)..." -ForegroundColor Yellow
Write-Host "   Meta integration scheduled for later phase" -ForegroundColor Gray

Write-Host "✅ COOL BITS SRL Proprietary Functions IAM permissions assigned" -ForegroundColor Green

# Step 5: Configure Vertex AI Security Services
Write-Host ""
Write-Host "🔒 Step 5: Configuring Vertex AI Security Services" -ForegroundColor Green
Write-Host "--------------------------------------------------" -ForegroundColor Green

# Enable Security Command Center
Write-Host "🛡️ Enabling Security Command Center..." -ForegroundColor Yellow
gcloud scc sources create --organization=$ORGANIZATION_ID --display-name="CoolBits Security Source" --description="Security monitoring for COOL BITS SRL"

# Create logging sink for policy compliance
Write-Host "📊 Creating logging sink for policy compliance..." -ForegroundColor Yellow
gcloud logging sinks create coolbits-policy-sink bigquery.googleapis.com/projects/$PROJECT_ID/datasets/policy_logs --log-filter='resource.type="gce_instance" OR resource.type="gce_disk"'

# Create monitoring dashboard for policy compliance
$monitoringDashboard = @"
{
  "displayName": "CoolBits Policy Compliance Dashboard",
  "mosaicLayout": {
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Policy Compliance Status",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"gce_instance\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_RATE"
                    }
                  }
                }
              }
            ]
          }
        }
      }
    ]
  }
}
"@

$monitoringDashboard | Out-File -FilePath "policy_monitoring_dashboard.json" -Encoding UTF8

Write-Host "📈 Creating monitoring dashboard..." -ForegroundColor Yellow
gcloud monitoring dashboards create --config-from-file=policy_monitoring_dashboard.json

# Create secret for API keys
Write-Host "🔑 Creating secret for API keys..." -ForegroundColor Yellow
gcloud secrets create coolbits-api-keys --replication-policy="automatic" --project=$PROJECT_ID

Write-Host "✅ Vertex AI Security Services configured" -ForegroundColor Green

# Step 6: Cleanup temporary files
Write-Host ""
Write-Host "🧹 Step 6: Cleaning up temporary files" -ForegroundColor Green
Write-Host "-------------------------------------" -ForegroundColor Green

Remove-Item -Path "policy_administrator_role.yaml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "security_reviewer_role.yaml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "ai_policy_administrator_role.yaml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "compliance_monitor_role.yaml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "coolbits_security_policy.yaml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "cblm_ai_governance_policy.yaml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "data_protection_policy.yaml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "policy_monitoring_dashboard.json" -Force -ErrorAction SilentlyContinue

Write-Host "✅ Temporary files cleaned up" -ForegroundColor Green

# Final Summary
Write-Host ""
Write-Host "🎯 GOOGLE CLOUD POLICY DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ IAM Roles: 4 custom roles created" -ForegroundColor Green
Write-Host "✅ Organization Policies: 3 policies applied" -ForegroundColor Green
Write-Host "✅ Policy Division Permissions: oGrok08 & oGrok09 configured" -ForegroundColor Green
Write-Host "✅ Proprietary Functions Permissions: oVertex, oCursor, oGrok, oGPT configured" -ForegroundColor Green
Write-Host "✅ Meta Integration: oMeta prepared for future phase" -ForegroundColor Yellow
Write-Host "✅ Vertex AI Security: Security Command Center, Logging, Monitoring configured" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Verify IAM roles are active in Google Cloud Console" -ForegroundColor White
Write-Host "2. Test organization policies" -ForegroundColor White
Write-Host "3. Monitor policy compliance in Security Command Center" -ForegroundColor White
Write-Host "4. Review Vertex AI security integration" -ForegroundColor White
Write-Host "5. Prepare Meta environment for future integration" -ForegroundColor White
Write-Host ""
Write-Host "🏢 COOL BITS SRL - Policy Division Integration Complete" -ForegroundColor Cyan
