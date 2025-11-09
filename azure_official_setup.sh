#!/bin/bash
# Azure CLI Setup Script for COOL BITS SRL Official Account
# Email: andrei@coolbits.ro
# Project: andrei@coolbits.ai

echo "🚀 Setting up Azure CLI for COOL BITS SRL Official Account"
echo "📧 Official Email: andrei@coolbits.ro"
echo "🌐 Project Email: andrei@coolbits.ai"
echo "=" * 80

# Install Azure CLI if not present
if ! command -v az &> /dev/null; then
    echo "📦 Installing Azure CLI..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Login to Azure with official account
echo "🔐 Logging in to Azure with official account..."
az login --use-device-code

# Set subscription
echo "📋 Setting subscription..."
az account set --subscription "Free Trial"  # or your specific subscription name

# Create resource group
echo "🏗️ Creating resource group..."
az group create --name coolbits-ai-rg --location "East US"

# Create Azure OpenAI resource
echo "🤖 Creating Azure OpenAI resource..."
az cognitiveservices account create \
    --name coolbits-ai-openai \
    --resource-group coolbits-ai-rg \
    --location "East US" \
    --kind OpenAI \
    --sku S0 \
    --yes

# Get API key
echo "🔑 Retrieving API key..."
API_KEY=$(az cognitiveservices account keys list \
    --name coolbits-ai-openai \
    --resource-group coolbits-ai-rg \
    --query key1 -o tsv)

echo "✅ Azure OpenAI resource created successfully!"
echo "🔑 API Key: $API_KEY"
echo "🌐 Endpoint: https://coolbits-ai-openai.openai.azure.com/"

# Save configuration
echo "💾 Saving configuration..."
cat > azure_official_config.json << EOF
{
    "company": "COOL BITS SRL",
    "ceo": "Andrei",
    "official_email": "andrei@coolbits.ro",
    "project_email": "andrei@coolbits.ai",
    "subscription_id": "$(az account show --query id -o tsv)",
    "resource_group": "coolbits-ai-rg",
    "openai_resource": "coolbits-ai-openai",
    "api_key": "$API_KEY",
    "endpoint": "https://coolbits-ai-openai.openai.azure.com/",
    "deployment_name": "gpt-4o-mini",
    "model": "gpt-4o-mini",
    "setup_date": "2025-09-07T13:47:51.640395"
}
EOF

echo "🎉 Azure OpenAI setup completed for COOL BITS SRL!"
echo "📁 Configuration saved to: azure_official_config.json"
