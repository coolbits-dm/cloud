# Azure PowerShell Setup Script for COOL BITS SRL Official Account
# Email: andrei@coolbits.ro
# Project: andrei@coolbits.ai

Write-Host "🚀 Setting up Azure PowerShell for COOL BITS SRL Official Account" -ForegroundColor Green
Write-Host "📧 Official Email: andrei@coolbits.ro" -ForegroundColor Cyan
Write-Host "🌐 Project Email: andrei@coolbits.ai" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Yellow

# Install Azure PowerShell module if not present
if (-not (Get-Module -ListAvailable -Name Az)) {
    Write-Host "📦 Installing Azure PowerShell module..." -ForegroundColor Yellow
    Install-Module -Name Az -AllowClobber -Force
}

# Import Azure module
Import-Module Az

# Login to Azure with official account
Write-Host "🔐 Logging in to Azure with official account..." -ForegroundColor Yellow
Connect-AzAccount -UseDeviceAuthentication

# Set subscription
Write-Host "📋 Setting subscription..." -ForegroundColor Yellow
Set-AzContext -Subscription "Free Trial"  # or your specific subscription name

# Create resource group
Write-Host "🏗️ Creating resource group..." -ForegroundColor Yellow
New-AzResourceGroup -Name "coolbits-ai-rg" -Location "East US"

# Create Azure OpenAI resource
Write-Host "🤖 Creating Azure OpenAI resource..." -ForegroundColor Yellow
New-AzCognitiveServicesAccount `
    -Name "coolbits-ai-openai" `
    -ResourceGroupName "coolbits-ai-rg" `
    -Location "East US" `
    -Kind "OpenAI" `
    -SkuName "S0"

# Get API key
Write-Host "🔑 Retrieving API key..." -ForegroundColor Yellow
$apiKey = (Get-AzCognitiveServicesAccountKey -Name "coolbits-ai-openai" -ResourceGroupName "coolbits-ai-rg").Key1

Write-Host "✅ Azure OpenAI resource created successfully!" -ForegroundColor Green
Write-Host "🔑 API Key: $apiKey" -ForegroundColor Cyan
Write-Host "🌐 Endpoint: https://coolbits-ai-openai.openai.azure.com/" -ForegroundColor Cyan

# Save configuration
Write-Host "💾 Saving configuration..." -ForegroundColor Yellow
$config = @{
    company = "COOL BITS SRL"
    ceo = "Andrei"
    official_email = "andrei@coolbits.ro"
    project_email = "andrei@coolbits.ai"
    subscription_id = (Get-AzContext).Subscription.Id
    resource_group = "coolbits-ai-rg"
    openai_resource = "coolbits-ai-openai"
    api_key = $apiKey
    endpoint = "https://coolbits-ai-openai.openai.azure.com/"
    deployment_name = "gpt-4o-mini"
    model = "gpt-4o-mini"
    setup_date = "2025-09-07T13:47:51.641395"
}

$config | ConvertTo-Json -Depth 3 | Out-File -FilePath "azure_official_config.json" -Encoding UTF8

Write-Host "🎉 Azure OpenAI setup completed for COOL BITS SRL!" -ForegroundColor Green
Write-Host "📁 Configuration saved to: azure_official_config.json" -ForegroundColor Cyan
