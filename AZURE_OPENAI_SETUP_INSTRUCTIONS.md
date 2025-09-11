# Azure OpenAI Setup Instructions for COOL BITS SRL

## Overview
This guide provides step-by-step instructions for setting up Azure OpenAI integration for COOL BITS SRL projects: coolbits.ai, cblm.ai.

## Prerequisites
- Azure subscription with OpenAI access
- Azure OpenAI resource created
- API key generated
- Deployment configured

## Configuration Steps

### 1. Azure OpenAI Resource Setup
1. Go to Azure Portal (https://portal.azure.com)
2. Create a new Azure OpenAI resource
3. Note your resource name and endpoint
4. Create a deployment for your model

### 2. API Key Generation
1. In your Azure OpenAI resource, go to "Keys and Endpoint"
2. Copy your API key
3. Update the `.env` file with your actual API key

### 3. Environment Configuration
Update the following variables in your `.env` file:
```
AZURE_OPENAI_API_KEY=your_actual_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

### 4. Model Configuration
Current configuration:
- **Model**: gpt-4o
- **Deployment**: gpt-4o
- **API Version**: 2024-02-15-preview
- **Max Tokens**: 4000
- **Temperature**: 0.7

### 5. Testing
Run the test script to verify configuration:
```bash
python azure_openai_client.py
```

## Integration Points

### coolbits.ai Integration
- **Endpoint**: https://api.coolbits.ai/v1/openai
- **Use Cases**: Code generation, document processing, API integration
- **Authentication**: Azure OpenAI API key

### cblm.ai Integration
- **Endpoint**: https://api.cblm.ai/v1/openai
- **Use Cases**: Language model training, text processing, content generation
- **Authentication**: Azure OpenAI API key

## Security Considerations
- Store API keys securely in environment variables
- Use Azure Key Vault for production deployments
- Implement proper access controls
- Monitor usage and costs

## Troubleshooting
- Verify API key is correct
- Check endpoint URL format
- Ensure deployment is active
- Monitor Azure OpenAI quotas

## Support
For technical support, contact:
- **Company**: COOL BITS SRL
- **CEO**: Andrei
- **Domains**: coolbits.ai, cblm.ai

Generated: 2025-09-07T13:45:14.304935
