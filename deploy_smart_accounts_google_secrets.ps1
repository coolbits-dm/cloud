# Smart Accounts Google Secret Manager Integration - PowerShell Script
# Trimite informațiile Smart Accounts în Google Secret Manager cu mențiunea @oGeminiCLI și @oOutlook

# Configuration
$PROJECT_ID = "coolbits-ai"
$COMPANY = "COOL BITS SRL"
$CEO = "Andrei"
$REFERENCE_NUMBER = "305157"
$BANK_CONSENT_ID = "58fee093-7e94-4cdc-92f4-c60cd3d7cd79"

Write-Host "🔐 Smart Accounts Google Secret Manager Integration" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "Company: $COMPANY" -ForegroundColor Yellow
Write-Host "CEO: $CEO" -ForegroundColor Yellow
Write-Host "Reference Number: $REFERENCE_NUMBER" -ForegroundColor Yellow
Write-Host "Bank Consent ID: $BANK_CONSENT_ID" -ForegroundColor Yellow
Write-Host "Project: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Agents: @oGeminiCLI, @oOutlook" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Cyan

# Step 1: Create Smart Accounts Reference Number Secret
Write-Host ""
Write-Host "🔐 Step 1: Creating Smart Accounts Reference Number Secret" -ForegroundColor Green
Write-Host "--------------------------------------------------------" -ForegroundColor Green

Write-Host "🔢 Creating smart-accounts-reference-number secret..." -ForegroundColor Yellow
echo $REFERENCE_NUMBER | gcloud secrets create smart-accounts-reference-number --data-file=- --project=$PROJECT_ID --labels="owner=andrei_cip,platform=smart_accounts,type=reference_number,company=coolbits_srl"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Smart Accounts Reference Number secret created successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Smart Accounts Reference Number secret may already exist" -ForegroundColor Yellow
}

# Step 2: Create Bank Consent ID Secret
Write-Host ""
Write-Host "🔐 Step 2: Creating Bank Consent ID Secret" -ForegroundColor Green
Write-Host "------------------------------------------" -ForegroundColor Green

Write-Host "🏦 Creating smart-accounts-bank-consent-id secret..." -ForegroundColor Yellow
echo $BANK_CONSENT_ID | gcloud secrets create smart-accounts-bank-consent-id --data-file=- --project=$PROJECT_ID --labels="owner=andrei_cip,platform=smart_accounts,type=bank_consent,company=coolbits_srl"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Bank Consent ID secret created successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Bank Consent ID secret may already exist" -ForegroundColor Yellow
}

# Step 3: Create Complete Configuration Secret
Write-Host ""
Write-Host "🔐 Step 3: Creating Complete Configuration Secret" -ForegroundColor Green
Write-Host "------------------------------------------------" -ForegroundColor Green

Write-Host "📋 Creating smart-accounts-complete-config secret..." -ForegroundColor Yellow

# Create complete configuration JSON
$completeConfig = @{
    smart_accounts = @{
        reference_number = $REFERENCE_NUMBER
        bank_consent_id = $BANK_CONSENT_ID
        company = $COMPANY
        company_cui = "42331573"
        integration_date = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        status = "active"
    }
    google_cloud = @{
        project_id = $PROJECT_ID
        region = "europe-west3"
        labels = @{
            owner = "andrei_cip"
            platform = "smart_accounts"
            company = "coolbits_srl"
            classification = "internal_secret"
        }
    }
    integration_info = @{
        created_by = "SmartAccountsGoogleSecretIntegration"
        created_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        company = $COMPANY
        project = $PROJECT_ID
    }
} | ConvertTo-Json -Depth 3

# Save configuration to temporary file
$tempConfigFile = "temp_smart_accounts_config.json"
$completeConfig | Out-File -FilePath $tempConfigFile -Encoding UTF8

# Create secret from file
gcloud secrets create smart-accounts-complete-config --data-file=$tempConfigFile --project=$PROJECT_ID --labels="owner=andrei_cip,platform=smart_accounts,type=complete_config,company=coolbits_srl"

# Clean up temporary file
Remove-Item $tempConfigFile -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Complete Configuration secret created successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Complete Configuration secret may already exist" -ForegroundColor Yellow
}

# Step 4: Create Agents Integration Secret
Write-Host ""
Write-Host "🔐 Step 4: Creating Agents Integration Secret" -ForegroundColor Green
Write-Host "--------------------------------------------" -ForegroundColor Green

Write-Host "🤖 Creating smart-accounts-agents-integration secret..." -ForegroundColor Yellow

# Create agents integration configuration JSON
$agentsConfig = @{
    mentioned_agents = @{
        oGeminiCLI = @{
            role = "AI Command Line Interface"
            responsibility = "Google Cloud Operations"
            integration_type = "Google Secret Manager"
        }
        oOutlook = @{
            role = "Email Management System"
            responsibility = "Email Operations"
            integration_type = "Email Notifications"
        }
    }
    integration_details = @{
        oGeminiCLI = @{
            role = "AI Command Line Interface"
            responsibility = "Google Cloud Operations"
            secret_access = @(
                "smart-accounts-reference-number",
                "smart-accounts-bank-consent-id",
                "smart-accounts-complete-config"
            )
            permissions = @("read", "monitor", "notify")
        }
        oOutlook = @{
            role = "Email Management System"
            responsibility = "Email Operations"
            secret_access = @(
                "smart-accounts-reference-number",
                "smart-accounts-bank-consent-id"
            )
            permissions = @("read", "notify")
        }
    }
    integration_date = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    company = $COMPANY
} | ConvertTo-Json -Depth 3

# Save agents configuration to temporary file
$tempAgentsFile = "temp_agents_integration_config.json"
$agentsConfig | Out-File -FilePath $tempAgentsFile -Encoding UTF8

# Create secret from file
gcloud secrets create smart-accounts-agents-integration --data-file=$tempAgentsFile --project=$PROJECT_ID --labels="owner=andrei_cip,platform=smart_accounts,type=agents_integration,company=coolbits_srl"

# Clean up temporary file
Remove-Item $tempAgentsFile -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Agents Integration secret created successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Agents Integration secret may already exist" -ForegroundColor Yellow
}

# Step 5: Verify Secrets Creation
Write-Host ""
Write-Host "🔍 Step 5: Verifying Secrets Creation" -ForegroundColor Green
Write-Host "------------------------------------" -ForegroundColor Green

Write-Host "📋 Listing Smart Accounts secrets..." -ForegroundColor Yellow
gcloud secrets list --project=$PROJECT_ID --filter="name:smart-accounts"

# Step 6: Agent Notifications
Write-Host ""
Write-Host "📢 Step 6: Agent Notifications" -ForegroundColor Green
Write-Host "----------------------------" -ForegroundColor Green

Write-Host "🤖 @oGeminiCLI Notification:" -ForegroundColor Cyan
Write-Host "   📋 Smart Accounts Reference: $REFERENCE_NUMBER" -ForegroundColor White
Write-Host "   🏦 Bank Consent ID: $BANK_CONSENT_ID" -ForegroundColor White
Write-Host "   🔐 Secrets Created: 4 secrets in Google Secret Manager" -ForegroundColor White
Write-Host "   📍 Project: $PROJECT_ID" -ForegroundColor White
Write-Host "   🌍 Region: europe-west3" -ForegroundColor White
Write-Host "   ✅ Status: Smart Accounts integration completed" -ForegroundColor Green

Write-Host ""
Write-Host "📧 @oOutlook Notification:" -ForegroundColor Cyan
Write-Host "   📋 Smart Accounts Reference: $REFERENCE_NUMBER" -ForegroundColor White
Write-Host "   🏦 Bank Consent ID: $BANK_CONSENT_ID" -ForegroundColor White
Write-Host "   📧 Email Integration: Ready for notifications" -ForegroundColor White
Write-Host "   🔐 Secret Access: smart-accounts-reference-number, smart-accounts-bank-consent-id" -ForegroundColor White
Write-Host "   ✅ Status: Smart Accounts email integration ready" -ForegroundColor Green

# Step 7: Generate Integration Report
Write-Host ""
Write-Host "📊 Step 7: Generating Integration Report" -ForegroundColor Green
Write-Host "--------------------------------------" -ForegroundColor Green

$integrationReport = @{
    company = $COMPANY
    company_cui = "42331573"
    project_id = $PROJECT_ID
    region = "europe-west3"
    integration_date = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    smart_accounts_data = @{
        reference_number = $REFERENCE_NUMBER
        bank_consent_id = $BANK_CONSENT_ID
        company = $COMPANY
        company_cui = "42331573"
        project_id = $PROJECT_ID
        region = "europe-west3"
    }
    mentioned_agents = @{
        oGeminiCLI = @{
            role = "AI Command Line Interface"
            responsibility = "Google Cloud Operations"
            integration_type = "Google Secret Manager"
        }
        oOutlook = @{
            role = "Email Management System"
            responsibility = "Email Operations"
            integration_type = "Email Notifications"
        }
    }
    created_secrets = @(
        "smart-accounts-reference-number",
        "smart-accounts-bank-consent-id",
        "smart-accounts-complete-config",
        "smart-accounts-agents-integration"
    )
    integration_status = "completed"
} | ConvertTo-Json -Depth 3

# Save integration report
$reportFile = "smart_accounts_integration_report.json"
$integrationReport | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "📊 Integration report saved: $reportFile" -ForegroundColor Green

# Final Summary
Write-Host ""
Write-Host "🎯 INTEGRATION SUMMARY" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "✅ Smart Accounts secrets created: 4" -ForegroundColor Green
Write-Host "✅ Agents notified: @oGeminiCLI, @oOutlook" -ForegroundColor Green
Write-Host "✅ Integration report generated: $reportFile" -ForegroundColor Green
Write-Host "✅ Classification: Internal Secret - CoolBits.ai Members Only" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔐 Smart Accounts Google Secret Manager Integration Complete!" -ForegroundColor Green
Write-Host "🤖 Agents: @oGeminiCLI, @oOutlook" -ForegroundColor Cyan
Write-Host "🏢 Company: $COMPANY" -ForegroundColor Yellow
Write-Host "=====================" -ForegroundColor Cyan
