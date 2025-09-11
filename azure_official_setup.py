#!/usr/bin/env python3
"""
Azure OpenAI Official Setup for COOL BITS SRL
Configuration for official Microsoft Azure account: andrei@coolbits.ro
"""

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AzureOfficialSetup:
    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.official_email = "andrei@coolbits.ro"
        self.project_email = "andrei@coolbits.ai"
        self.project_domains = ["coolbits.ai", "cblm.ai"]

        # Azure Official Account Configuration
        self.azure_official_config = {
            "account_type": "Microsoft Azure Free Tier",
            "primary_email": self.official_email,
            "project_email": self.project_email,
            "subscription_id": "",  # Will be retrieved from Azure CLI
            "resource_group": "coolbits-ai-rg",
            "location": "East US",  # Free tier regions
            "openai_resource": "coolbits-ai-openai",
            "openai_endpoint": "https://coolbits-ai-openai.openai.azure.com/",
            "deployment_name": "gpt-4o-mini",  # Free tier model
            "api_version": "2024-02-15-preview",
            "model": "gpt-4o-mini",
            "max_tokens": 4000,
            "temperature": 0.7,
        }

        # Chrome Session Integration
        self.chrome_session_config = {
            "browser": "Chrome",
            "session_email": self.project_email,
            "azure_portal_url": "https://portal.azure.com",
            "openai_studio_url": "https://oai.azure.com",
            "authentication_method": "Azure AD SSO",
        }

    def create_azure_cli_setup_script(self):
        """Create Azure CLI setup script for official account"""
        logger.info("🔧 Creating Azure CLI setup script...")

        setup_script = f"""#!/bin/bash
# Azure CLI Setup Script for COOL BITS SRL Official Account
# Email: {self.official_email}
# Project: {self.project_email}

echo "🚀 Setting up Azure CLI for COOL BITS SRL Official Account"
echo "📧 Official Email: {self.official_email}"
echo "🌐 Project Email: {self.project_email}"
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
az group create --name {self.azure_official_config["resource_group"]} --location "{self.azure_official_config["location"]}"

# Create Azure OpenAI resource
echo "🤖 Creating Azure OpenAI resource..."
az cognitiveservices account create \\
    --name {self.azure_official_config["openai_resource"]} \\
    --resource-group {self.azure_official_config["resource_group"]} \\
    --location "{self.azure_official_config["location"]}" \\
    --kind OpenAI \\
    --sku S0 \\
    --yes

# Get API key
echo "🔑 Retrieving API key..."
API_KEY=$(az cognitiveservices account keys list \\
    --name {self.azure_official_config["openai_resource"]} \\
    --resource-group {self.azure_official_config["resource_group"]} \\
    --query key1 -o tsv)

echo "✅ Azure OpenAI resource created successfully!"
echo "🔑 API Key: $API_KEY"
echo "🌐 Endpoint: {self.azure_official_config["openai_endpoint"]}"

# Save configuration
echo "💾 Saving configuration..."
cat > azure_official_config.json << EOF
{{
    "company": "{self.company}",
    "ceo": "{self.ceo}",
    "official_email": "{self.official_email}",
    "project_email": "{self.project_email}",
    "subscription_id": "$(az account show --query id -o tsv)",
    "resource_group": "{self.azure_official_config["resource_group"]}",
    "openai_resource": "{self.azure_official_config["openai_resource"]}",
    "api_key": "$API_KEY",
    "endpoint": "{self.azure_official_config["openai_endpoint"]}",
    "deployment_name": "{self.azure_official_config["deployment_name"]}",
    "model": "{self.azure_official_config["model"]}",
    "setup_date": "{datetime.now().isoformat()}"
}}
EOF

echo "🎉 Azure OpenAI setup completed for COOL BITS SRL!"
echo "📁 Configuration saved to: azure_official_config.json"
"""

        with open("azure_official_setup.sh", "w", encoding="utf-8") as f:
            f.write(setup_script)

        logger.info("✅ Azure CLI setup script created: azure_official_setup.sh")

    def create_powershell_setup_script(self):
        """Create PowerShell setup script for Windows"""
        logger.info("🔧 Creating PowerShell setup script...")

        ps_script = f"""# Azure PowerShell Setup Script for COOL BITS SRL Official Account
# Email: {self.official_email}
# Project: {self.project_email}

Write-Host "🚀 Setting up Azure PowerShell for COOL BITS SRL Official Account" -ForegroundColor Green
Write-Host "📧 Official Email: {self.official_email}" -ForegroundColor Cyan
Write-Host "🌐 Project Email: {self.project_email}" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Yellow

# Install Azure PowerShell module if not present
if (-not (Get-Module -ListAvailable -Name Az)) {{
    Write-Host "📦 Installing Azure PowerShell module..." -ForegroundColor Yellow
    Install-Module -Name Az -AllowClobber -Force
}}

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
New-AzResourceGroup -Name "{self.azure_official_config["resource_group"]}" -Location "{self.azure_official_config["location"]}"

# Create Azure OpenAI resource
Write-Host "🤖 Creating Azure OpenAI resource..." -ForegroundColor Yellow
New-AzCognitiveServicesAccount `
    -Name "{self.azure_official_config["openai_resource"]}" `
    -ResourceGroupName "{self.azure_official_config["resource_group"]}" `
    -Location "{self.azure_official_config["location"]}" `
    -Kind "OpenAI" `
    -SkuName "S0"

# Get API key
Write-Host "🔑 Retrieving API key..." -ForegroundColor Yellow
$apiKey = (Get-AzCognitiveServicesAccountKey -Name "{self.azure_official_config["openai_resource"]}" -ResourceGroupName "{self.azure_official_config["resource_group"]}").Key1

Write-Host "✅ Azure OpenAI resource created successfully!" -ForegroundColor Green
Write-Host "🔑 API Key: $apiKey" -ForegroundColor Cyan
Write-Host "🌐 Endpoint: {self.azure_official_config["openai_endpoint"]}" -ForegroundColor Cyan

# Save configuration
Write-Host "💾 Saving configuration..." -ForegroundColor Yellow
$config = @{{
    company = "{self.company}"
    ceo = "{self.ceo}"
    official_email = "{self.official_email}"
    project_email = "{self.project_email}"
    subscription_id = (Get-AzContext).Subscription.Id
    resource_group = "{self.azure_official_config["resource_group"]}"
    openai_resource = "{self.azure_official_config["openai_resource"]}"
    api_key = $apiKey
    endpoint = "{self.azure_official_config["openai_endpoint"]}"
    deployment_name = "{self.azure_official_config["deployment_name"]}"
    model = "{self.azure_official_config["model"]}"
    setup_date = "{datetime.now().isoformat()}"
}}

$config | ConvertTo-Json -Depth 3 | Out-File -FilePath "azure_official_config.json" -Encoding UTF8

Write-Host "🎉 Azure OpenAI setup completed for COOL BITS SRL!" -ForegroundColor Green
Write-Host "📁 Configuration saved to: azure_official_config.json" -ForegroundColor Cyan
"""

        with open("azure_official_setup.ps1", "w", encoding="utf-8") as f:
            f.write(ps_script)

        logger.info("✅ PowerShell setup script created: azure_official_setup.ps1")

    def create_chrome_session_integration(self):
        """Create Chrome session integration guide"""
        logger.info("🌐 Creating Chrome session integration guide...")

        chrome_guide = f"""# Chrome Session Integration for Azure OpenAI - COOL BITS SRL

## Overview
This guide explains how to integrate Azure OpenAI with your Chrome session using the official Microsoft Azure account.

## Current Setup
- **Official Email**: {self.official_email}
- **Project Email**: {self.project_email}
- **Browser**: Chrome
- **Authentication**: Azure AD SSO

## Step-by-Step Integration

### 1. Chrome Session Setup
1. Open Chrome browser
2. Sign in with {self.project_email}
3. Navigate to Azure Portal: https://portal.azure.com
4. Sign in with {self.official_email}

### 2. Azure OpenAI Resource Creation
1. In Azure Portal, search for "OpenAI"
2. Click "Create" to create a new Azure OpenAI resource
3. Fill in the details:
   - **Subscription**: Your free tier subscription
   - **Resource Group**: {self.azure_official_config["resource_group"]}
   - **Region**: {self.azure_official_config["location"]}
   - **Name**: {self.azure_official_config["openai_resource"]}
   - **Pricing Tier**: Free (F0) or Standard (S0)

### 3. Model Deployment
1. Go to Azure OpenAI Studio: https://oai.azure.com
2. Select your resource
3. Deploy a model:
   - **Model**: {self.azure_official_config["model"]}
   - **Deployment Name**: {self.azure_official_config["deployment_name"]}
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
AZURE_OPENAI_ENDPOINT=https://{self.azure_official_config["openai_resource"]}.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME={self.azure_official_config["deployment_name"]}
AZURE_OPENAI_API_VERSION={self.azure_official_config["api_version"]}
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
- **Company**: {self.company}
- **CEO**: {self.ceo}
- **Official Email**: {self.official_email}
- **Project Email**: {self.project_email}

Generated: {datetime.now().isoformat()}
"""

        with open("CHROME_AZURE_INTEGRATION_GUIDE.md", "w", encoding="utf-8") as f:
            f.write(chrome_guide)

        logger.info(
            "✅ Chrome integration guide created: CHROME_AZURE_INTEGRATION_GUIDE.md"
        )

    def create_official_client(self):
        """Create official Azure OpenAI client"""
        logger.info("🤖 Creating official Azure OpenAI client...")

        client_code = f'''#!/usr/bin/env python3
"""
Official Azure OpenAI Client for COOL BITS SRL
Integration with official Microsoft Azure account: {self.official_email}
"""

import os
import openai
from openai import AzureOpenAI
from dotenv import load_dotenv
import logging
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoolBitsOfficialAzureOpenAI:
    def __init__(self):
        self.company = "{self.company}"
        self.ceo = "{self.ceo}"
        self.official_email = "{self.official_email}"
        self.project_email = "{self.project_email}"
        self.domains = {self.project_domains}
        
        # Load official configuration
        self.config = self._load_official_config()
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=self.config.get('api_key', os.getenv("AZURE_OPENAI_API_KEY")),
            api_version=self.config.get('api_version', os.getenv("AZURE_OPENAI_API_VERSION")),
            azure_endpoint=self.config.get('endpoint', os.getenv("AZURE_OPENAI_ENDPOINT"))
        )
        
        self.deployment_name = self.config.get('deployment_name', os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))
        self.model = self.config.get('model', os.getenv("AZURE_OPENAI_MODEL"))
        
        logger.info(f"✅ Official Azure OpenAI client initialized for {{self.company}}")
        logger.info(f"📧 Official Email: {{self.official_email}}")
        logger.info(f"🌐 Project Email: {{self.project_email}}")
        logger.info(f"🏢 Domains: {{', '.join(self.domains)}}")
        logger.info(f"🤖 Model: {{self.model}}")
        logger.info(f"📦 Deployment: {{self.deployment_name}}")

    def _load_official_config(self):
        """Load official Azure configuration"""
        try:
            with open("azure_official_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("⚠️ Official config not found, using environment variables")
            return {{}}

    def generate_text(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7):
        """Generate text using official Azure OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {{"role": "system", "content": f"You are an AI assistant for {{self.company}}, helping with {{', '.join(self.domains)}} projects. Official account: {{self.official_email}}."}},
                    {{"role": "user", "content": prompt}}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error generating text: {{e}}")
            return None

    def generate_code(self, prompt: str, language: str = "python"):
        """Generate code using official Azure OpenAI"""
        system_prompt = f"""You are a senior software engineer for {self.company}, specializing in {{language}} development for {", ".join(self.project_domains)} projects.
        
        Official Microsoft Azure account: {self.official_email}
        Project email: {self.project_email}
        
        Generate clean, efficient, and well-documented code that follows best practices.
        Include proper error handling and logging.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {{"role": "system", "content": system_prompt}},
                    {{"role": "user", "content": f"Generate {{language}} code for: {{prompt}}"}}
                ],
                max_tokens=4000,
                temperature=0.3,
                top_p=1.0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error generating code: {{e}}")
            return None

    def get_account_info(self):
        """Get official Azure account information"""
        return {{
            "company": self.company,
            "ceo": self.ceo,
            "official_email": self.official_email,
            "project_email": self.project_email,
            "domains": self.domains,
            "azure_resource": self.config.get('openai_resource', 'N/A'),
            "subscription_id": self.config.get('subscription_id', 'N/A'),
            "resource_group": self.config.get('resource_group', 'N/A'),
            "model": self.model,
            "deployment": self.deployment_name,
            "last_updated": "{datetime.now().isoformat()}"
        }}

def main():
    """Main function for testing official Azure OpenAI client"""
    print("=" * 80)
    print("🤖 COOL BITS SRL OFFICIAL AZURE OPENAI CLIENT")
    print("=" * 80)
    print(f"🏢 Company: {self.company}")
    print(f"👤 CEO: {self.ceo}")
    print(f"📧 Official Email: {self.official_email}")
    print(f"🌐 Project Email: {self.project_email}")
    print(f"🏢 Domains: {", ".join(self.project_domains)}")
    print("=" * 80)
    
    client = CoolBitsOfficialAzureOpenAI()
    
    # Display account info
    print("\\n📊 Official Account Information:")
    account_info = client.get_account_info()
    for key, value in account_info.items():
        print(f"  {{key}}: {{value}}")
    
    # Test text generation
    print("\\n🧪 Testing text generation...")
    test_prompt = "Explain the benefits of using official Azure OpenAI for enterprise applications"
    response = client.generate_text(test_prompt)
    
    if response:
        print(f"✅ Text generation successful")
        print(f"📝 Response: {{response[:200]}}...")
    else:
        print("❌ Text generation failed")
    
    # Test code generation
    print("\\n🧪 Testing code generation...")
    code_prompt = "Create a Python function to validate email addresses"
    code_response = client.generate_code(code_prompt)
    
    if code_response:
        print(f"✅ Code generation successful")
        print(f"💻 Code: {{code_response[:200]}}...")
    else:
        print("❌ Code generation failed")

if __name__ == "__main__":
    main()
'''

        with open("azure_official_client.py", "w", encoding="utf-8") as f:
            f.write(client_code)

        logger.info("✅ Official Azure OpenAI client created: azure_official_client.py")

    def run_complete_setup(self):
        """Run complete official Azure OpenAI setup"""
        logger.info(
            "🚀 Running complete official Azure OpenAI setup for COOL BITS SRL..."
        )

        print("=" * 80)
        print("🤖 OFFICIAL AZURE OPENAI SETUP FOR COOL BITS SRL")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"📧 Official Email: {self.official_email}")
        print(f"🌐 Project Email: {self.project_email}")
        print(f"🏢 Domains: {', '.join(self.project_domains)}")
        print("=" * 80)

        # Generate setup files
        self.create_azure_cli_setup_script()
        self.create_powershell_setup_script()
        self.create_chrome_session_integration()
        self.create_official_client()

        print("\n✅ Official Azure OpenAI setup completed successfully!")
        print("\n📁 Generated Files:")
        print("  • azure_official_setup.sh - Linux/macOS setup script")
        print("  • azure_official_setup.ps1 - Windows PowerShell setup script")
        print("  • CHROME_AZURE_INTEGRATION_GUIDE.md - Chrome integration guide")
        print("  • azure_official_client.py - Official Python client")

        print("\n🔧 Next Steps:")
        print("  1. Run the PowerShell script: .\\azure_official_setup.ps1")
        print("  2. Follow the Chrome integration guide")
        print("  3. Test with: python azure_official_client.py")
        print("  4. Integrate with your coolbits.ai and cblm.ai projects")

        print("\n🌐 Chrome Session Integration:")
        print(f"  • Sign in to Chrome with: {self.project_email}")
        print(f"  • Access Azure Portal with: {self.official_email}")
        print("  • Follow the integration guide for seamless setup")

        logger.info("🎉 Complete official Azure OpenAI setup finished successfully")


def main():
    """Main function"""
    setup = AzureOfficialSetup()
    setup.run_complete_setup()


if __name__ == "__main__":
    main()
