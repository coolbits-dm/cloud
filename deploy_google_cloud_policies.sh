#!/bin/bash
# Google Cloud IAM & Organization Policies Deployment Script
# Applies Policy Division decisions to Google Cloud infrastructure

set -e

# Configuration
PROJECT_ID="coolbits-ai"
ORGANIZATION_ID="0"  # Update with actual organization ID
COMPANY="COOL BITS SRL"
CEO="Andrei"

echo "☁️ Google Cloud IAM & Organization Policies Deployment"
echo "======================================================"
echo "Company: $COMPANY"
echo "CEO: $CEO"
echo "Project: $PROJECT_ID"
echo "Organization: $ORGANIZATION_ID"
echo "======================================================"

# Step 1: Create IAM Roles for Policy Division
echo ""
echo "🔐 Step 1: Creating IAM Roles for Policy Division"
echo "--------------------------------------------------"

# Policy Administrator Role
cat > policy_administrator_role.yaml << EOF
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
EOF

gcloud iam roles create policyAdministrator \
    --project=$PROJECT_ID \
    --file=policy_administrator_role.yaml

# Security Reviewer Role
cat > security_reviewer_role.yaml << EOF
title: Security Reviewer
description: Reviews security policies and compliance
stage: GA
includedPermissions:
- securitycenter.assets.list
- securitycenter.findings.list
- cloudsecurityscanner.scans.list
- accessapproval.requests.list
- iam.roles.get
EOF

gcloud iam roles create securityReviewer \
    --project=$PROJECT_ID \
    --file=security_reviewer_role.yaml

# AI Policy Administrator Role
cat > ai_policy_administrator_role.yaml << EOF
title: AI Policy Administrator
description: Manages AI-specific policies and governance
stage: GA
includedPermissions:
- aiplatform.models.list
- aiplatform.endpoints.list
- aiplatform.pipelines.list
- discoveryengine.corpora.list
- aiplatform.jobs.list
EOF

gcloud iam roles create aiPolicyAdministrator \
    --project=$PROJECT_ID \
    --file=ai_policy_administrator_role.yaml

# Compliance Monitor Role
cat > compliance_monitor_role.yaml << EOF
title: Compliance Monitor
description: Monitors policy compliance across all systems
stage: GA
includedPermissions:
- logging.logs.list
- monitoring.timeSeries.list
- cloudaudit.auditLogs.list
- iam.roles.get
- resourcemanager.projects.get
EOF

gcloud iam roles create complianceMonitor \
    --project=$PROJECT_ID \
    --file=compliance_monitor_role.yaml

echo "✅ IAM Roles created successfully"

# Step 2: Create Organization Policies
echo ""
echo "🏛️ Step 2: Creating Organization Policies"
echo "----------------------------------------"

# Security Policy for coolbits.ai
cat > coolbits_security_policy.yaml << EOF
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allValues: ALLOW
  allowedValues:
  - coolbits.ai
  - coolbits.ro
EOF

gcloud resource-manager org-policies set-policy \
    --organization=$ORGANIZATION_ID \
    coolbits_security_policy.yaml

# AI Governance Policy for cblm.ai
cat > cblm_ai_governance_policy.yaml << EOF
constraint: constraints/aiplatform.restrictNonAdminAPI
booleanPolicy:
  enforced: true
EOF

gcloud resource-manager org-policies set-policy \
    --organization=$ORGANIZATION_ID \
    cblm_ai_governance_policy.yaml

# Data Protection Policy
cat > data_protection_policy.yaml << EOF
constraint: constraints/storage.uniformBucketLevelAccess
booleanPolicy:
  enforced: true
EOF

gcloud resource-manager org-policies set-policy \
    --organization=$ORGANIZATION_ID \
    data_protection_policy.yaml

echo "✅ Organization Policies created successfully"

# Step 3: Assign IAM Permissions to Policy Division Agents
echo ""
echo "👥 Step 3: Assigning IAM Permissions to Policy Division Agents"
echo "-------------------------------------------------------------"

# Assign permissions to oGrok08 (CISO)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:ogrok08@coolbits.ai" \
    --role="projects/$PROJECT_ID/roles/policyAdministrator"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:ogrok08@coolbits.ai" \
    --role="projects/$PROJECT_ID/roles/securityReviewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:ogrok08@coolbits.ai" \
    --role="roles/cloudaudit.auditLogViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:ogrok08@coolbits.ai" \
    --role="roles/monitoring.viewer"

# Assign permissions to oGrok09 (CAIO)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:ogrok09@coolbits.ai" \
    --role="projects/$PROJECT_ID/roles/aiPolicyAdministrator"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:ogrok09@coolbits.ai" \
    --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:ogrok09@coolbits.ai" \
    --role="roles/discoveryengine.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:ogrok09@coolbits.ai" \
    --role="roles/ml.developer"

echo "✅ Policy Division IAM permissions assigned"

# Step 4: Assign IAM Permissions to COOL BITS SRL Proprietary Functions
echo ""
echo "🏢 Step 4: Assigning IAM Permissions to COOL BITS SRL Proprietary Functions"
echo "---------------------------------------------------------------------------"

# oVertex permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:oVertex@coolbits.ai" \
    --role="roles/compute.viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:oVertex@coolbits.ai" \
    --role="roles/monitoring.viewer"

# oCursor permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:oCursor@coolbits.ai" \
    --role="roles/source.reader"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:oCursor@coolbits.ai" \
    --role="roles/cloudbuild.viewer"

# oGrok permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:oGrok@coolbits.ai" \
    --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:oGrok@coolbits.ai" \
    --role="roles/discoveryengine.admin"

# oGPT permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:oGPT@coolbits.ai" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:oGPT@coolbits.ai" \
    --role="roles/discoveryengine.user"

echo "✅ COOL BITS SRL Proprietary Functions IAM permissions assigned"

# Step 5: Configure Vertex AI Security Services
echo ""
echo "🔒 Step 5: Configuring Vertex AI Security Services"
echo "--------------------------------------------------"

# Enable Security Command Center
gcloud scc sources create \
    --organization=$ORGANIZATION_ID \
    --display-name="CoolBits Security Source" \
    --description="Security monitoring for COOL BITS SRL"

# Create logging sink for policy compliance
gcloud logging sinks create coolbits-policy-sink \
    bigquery.googleapis.com/projects/$PROJECT_ID/datasets/policy_logs \
    --log-filter='resource.type="gce_instance" OR resource.type="gce_disk"'

# Create monitoring dashboard for policy compliance
cat > policy_monitoring_dashboard.json << EOF
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
EOF

gcloud monitoring dashboards create \
    --config-from-file=policy_monitoring_dashboard.json

# Create secret for API keys
gcloud secrets create coolbits-api-keys \
    --replication-policy="automatic" \
    --project=$PROJECT_ID

echo "✅ Vertex AI Security Services configured"

# Step 6: Cleanup temporary files
echo ""
echo "🧹 Step 6: Cleaning up temporary files"
echo "-------------------------------------"

rm -f policy_administrator_role.yaml
rm -f security_reviewer_role.yaml
rm -f ai_policy_administrator_role.yaml
rm -f compliance_monitor_role.yaml
rm -f coolbits_security_policy.yaml
rm -f cblm_ai_governance_policy.yaml
rm -f data_protection_policy.yaml
rm -f policy_monitoring_dashboard.json

echo "✅ Temporary files cleaned up"

# Final Summary
echo ""
echo "🎯 GOOGLE CLOUD POLICY DEPLOYMENT COMPLETE"
echo "=========================================="
echo "✅ IAM Roles: 4 custom roles created"
echo "✅ Organization Policies: 3 policies applied"
echo "✅ Policy Division Permissions: oGrok08 & oGrok09 configured"
echo "✅ Proprietary Functions Permissions: oVertex, oCursor, oGrok, oGPT configured"
echo "✅ Vertex AI Security: Security Command Center, Logging, Monitoring configured"
echo ""
echo "📋 Next Steps:"
echo "1. Verify IAM roles are active in Google Cloud Console"
echo "2. Test organization policies"
echo "3. Monitor policy compliance in Security Command Center"
echo "4. Review Vertex AI security integration"
echo ""
echo "🏢 COOL BITS SRL - Policy Division Integration Complete"
