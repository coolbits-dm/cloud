# Chrome Session Integration for Azure OpenAI - COOL BITS SRL

## Overview
This guide explains how to integrate Azure OpenAI with your Chrome session using the official Microsoft Azure account.

## Current Setup
- **Official Email**: andrei@coolbits.ro
- **Project Email**: andrei@coolbits.ai
- **Browser**: Chrome
- **Authentication**: Azure AD SSO

## Step-by-Step Integration

### 1. Chrome Session Setup
1. Open Chrome browser
2. Sign in with andrei@coolbits.ai
3. Navigate to Azure Portal: https://portal.azure.com
4. Sign in with andrei@coolbits.ro

### 2. Azure OpenAI Resource Creation
1. In Azure Portal, search for "OpenAI"
2. Click "Create" to create a new Azure OpenAI resource
3. Fill in the details:
   - **Subscription**: Your free tier subscription
   - **Resource Group**: coolbits-ai-rg
   - **Region**: East US
   - **Name**: coolbits-ai-openai
   - **Pricing Tier**: Free (F0) or Standard (S0)

### 3. Model Deployment
1. Go to Azure OpenAI Studio: https://oai.azure.com
2. Select your resource
3. Deploy a model:
   - **Model**: gpt-4o-mini
   - **Deployment Name**: gpt-4o-mini
   - **Version**: Latest

### 4. API Key Retrieval
1. In Azure Portal, go to your OpenAI resource
2. Navigate to "Keys and Endpoint"
3. Copy Key 1 or Key 2
4. Note the endpoint URL

### 5. Environment Configuration
Update your `.env` file with the official credentials:
```
AZURE_OPENAI_API_KEY=your_actual_api_key_from_azure
AZURE_OPENAI_ENDPOINT=https://coolbits-ai-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Chrome Extensions (Optional)
- **Azure Account**: For easy Azure resource management
- **Azure CLI**: For command-line operations
- **Azure Storage Explorer**: For file management

## Security Best Practices
- Use Azure Key Vault for production API keys
- Enable MFA on your Azure account
- Regularly rotate API keys
- Monitor usage and costs

## Troubleshooting
- Clear Chrome cache if authentication issues occur
- Check Azure subscription limits
- Verify resource group permissions
- Ensure model deployment is active

## Support
- **Company**: COOL BITS SRL
- **CEO**: Andrei
- **Official Email**: andrei@coolbits.ro
- **Project Email**: andrei@coolbits.ai

Generated: 2025-09-07T13:47:51.642395
