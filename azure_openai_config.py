#!/usr/bin/env python3
"""
Azure OpenAI Configuration for COOL BITS SRL
Complete setup for Azure OpenAI integration with coolbits.ai and cblm.ai
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AzureOpenAIConfig:
    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.project_domains = ["coolbits.ai", "cblm.ai"]

        # Azure OpenAI Configuration from screenshot
        self.azure_openai_config = {
            "enabled": True,
            "base_url": "coolbits-ai.openai.azure.com",  # Your Azure OpenAI resource
            "deployment_name": "gpt-4o",  # Your deployment name
            "api_key": "",  # Will be set via environment variable
            "api_version": "2024-02-15-preview",
            "model": "gpt-4o",
            "max_tokens": 4000,
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }

        # AWS Bedrock Configuration (also from screenshot)
        self.aws_bedrock_config = {
            "enabled": False,  # Currently disabled as per screenshot
            "access_key_id": "",
            "secret_access_key": "",
            "region": "us-east-1",
            "test_model": "us.anthropic.claude-3-5-sonnet",
        }

        # Integration endpoints
        self.integration_endpoints = {
            "coolbits_ai": "https://api.coolbits.ai/v1/openai",
            "cblm_ai": "https://api.cblm.ai/v1/openai",
            "vertex_ai": "https://api.coolbits.ai/v1/vertex-ai",
        }

    def generate_environment_variables(self):
        """Generate environment variables for Azure OpenAI"""
        logger.info("🔧 Generating Azure OpenAI environment variables...")

        env_vars = {
            "AZURE_OPENAI_API_KEY": "your_azure_openai_api_key_here",
            "AZURE_OPENAI_ENDPOINT": f"https://{self.azure_openai_config['base_url']}",
            "AZURE_OPENAI_DEPLOYMENT_NAME": self.azure_openai_config["deployment_name"],
            "AZURE_OPENAI_API_VERSION": self.azure_openai_config["api_version"],
            "AZURE_OPENAI_MODEL": self.azure_openai_config["model"],
            "OPENAI_API_TYPE": "azure",
            "OPENAI_API_BASE": f"https://{self.azure_openai_config['base_url']}",
            "OPENAI_API_KEY": "your_azure_openai_api_key_here",
            "OPENAI_API_VERSION": self.azure_openai_config["api_version"],
        }

        return env_vars

    def create_azure_openai_config_file(self):
        """Create Azure OpenAI configuration file"""
        logger.info("📝 Creating Azure OpenAI configuration file...")

        config_data = {
            "company_info": {
                "name": self.company,
                "ceo": self.ceo,
                "domains": self.project_domains,
                "config_date": datetime.now().isoformat(),
            },
            "azure_openai": self.azure_openai_config,
            "aws_bedrock": self.aws_bedrock_config,
            "integration_endpoints": self.integration_endpoints,
            "usage_scenarios": {
                "coolbits_ai": [
                    "Code generation and analysis",
                    "Document processing",
                    "API integration",
                    "Business logic automation",
                ],
                "cblm_ai": [
                    "Language model training",
                    "Text processing",
                    "Content generation",
                    "AI model optimization",
                ],
            },
        }

        with open("azure_openai_config.json", "w") as f:
            json.dump(config_data, f, indent=2)

        logger.info(
            "✅ Azure OpenAI configuration file created: azure_openai_config.json"
        )
        return config_data

    def create_env_file(self):
        """Create .env file with Azure OpenAI credentials"""
        logger.info("🔐 Creating .env file for Azure OpenAI credentials...")

        env_content = f"""# Azure OpenAI Configuration for COOL BITS SRL
# Generated: {datetime.now().isoformat()}

# Azure OpenAI Settings
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://{self.azure_openai_config['base_url']}
AZURE_OPENAI_DEPLOYMENT_NAME={self.azure_openai_config['deployment_name']}
AZURE_OPENAI_API_VERSION={self.azure_openai_config['api_version']}
AZURE_OPENAI_MODEL={self.azure_openai_config['model']}

# OpenAI SDK Settings
OPENAI_API_TYPE=azure
OPENAI_API_BASE=https://{self.azure_openai_config['base_url']}
OPENAI_API_KEY=your_azure_openai_api_key_here
OPENAI_API_VERSION={self.azure_openai_config['api_version']}

# AWS Bedrock Settings (Currently Disabled)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=us.anthropic.claude-3-5-sonnet

# Project Settings
COOLBITS_AI_API_URL={self.integration_endpoints['coolbits_ai']}
CBLM_AI_API_URL={self.integration_endpoints['cblm_ai']}
VERTEX_AI_API_URL={self.integration_endpoints['vertex_ai']}

# Company Information
COMPANY_NAME={self.company}
CEO_NAME={self.ceo}
PROJECT_DOMAINS={','.join(self.project_domains)}
"""

        with open(".env", "w") as f:
            f.write(env_content)

        logger.info("✅ .env file created with Azure OpenAI configuration")

    def create_azure_openai_client(self):
        """Create Azure OpenAI client configuration"""
        logger.info("🤖 Creating Azure OpenAI client configuration...")

        client_code = f'''#!/usr/bin/env python3
"""
Azure OpenAI Client for COOL BITS SRL
Integration with coolbits.ai and cblm.ai
"""

import os
import openai
from openai import AzureOpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoolBitsAzureOpenAIClient:
    def __init__(self):
        self.company = "{self.company}"
        self.ceo = "{self.ceo}"
        self.domains = {self.project_domains}
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.model = os.getenv("AZURE_OPENAI_MODEL")
        
        logger.info(f"✅ Azure OpenAI client initialized for {{self.company}}")
        logger.info(f"🏢 Domains: {{', '.join(self.domains)}}")
        logger.info(f"🤖 Model: {{self.model}}")
        logger.info(f"📦 Deployment: {{self.deployment_name}}")

    def generate_text(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7):
        """Generate text using Azure OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {{"role": "system", "content": f"You are an AI assistant for {{self.company}}, helping with {{', '.join(self.domains)}} projects."}},
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
        """Generate code using Azure OpenAI"""
        system_prompt = f"""You are a senior software engineer for {self.company}, specializing in {{language}} development for {', '.join(self.project_domains)} projects.
        
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

    def analyze_document(self, content: str, analysis_type: str = "general"):
        """Analyze document content using Azure OpenAI"""
        system_prompt = f"""You are a document analysis specialist for {self.company}, working on {', '.join(self.project_domains)} projects.
        
        Provide detailed analysis of the document content, including:
        - Key insights and findings
        - Technical recommendations
        - Business implications
        - Action items
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {{"role": "system", "content": system_prompt}},
                    {{"role": "user", "content": f"Analyze this document ({{analysis_type}}): {{content}}"}}
                ],
                max_tokens=4000,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error analyzing document: {{e}}")
            return None

    def get_usage_stats(self):
        """Get usage statistics for Azure OpenAI"""
        try:
            # This would typically call Azure OpenAI usage API
            # For now, return mock data
            return {{
                "company": self.company,
                "domains": self.domains,
                "total_requests": 0,
                "total_tokens": 0,
                "cost_estimate": 0.0,
                "last_updated": "{datetime.now().isoformat()}"
            }}
            
        except Exception as e:
            logger.error(f"❌ Error getting usage stats: {{e}}")
            return None

def main():
    """Main function for testing Azure OpenAI client"""
    print("=" * 80)
    print("🤖 COOL BITS SRL AZURE OPENAI CLIENT")
    print("=" * 80)
    print(f"🏢 Company: {self.company}")
    print(f"👤 CEO: {self.ceo}")
    print(f"🌐 Domains: {', '.join(self.project_domains)}")
    print("=" * 80)
    
    client = CoolBitsAzureOpenAIClient()
    
    # Test text generation
    print("\\n🧪 Testing text generation...")
    test_prompt = "Explain the benefits of using Azure OpenAI for enterprise applications"
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
    
    # Get usage stats
    print("\\n📊 Usage Statistics:")
    stats = client.get_usage_stats()
    if stats:
        print(f"📈 Total Requests: {{stats['total_requests']}}")
        print(f"🔢 Total Tokens: {{stats['total_tokens']}}")
        print(f"💰 Cost Estimate: ${{stats['cost_estimate']:.2f}}")

if __name__ == "__main__":
    main()
'''

        with open("azure_openai_client.py", "w", encoding="utf-8") as f:
            f.write(client_code)

        logger.info("✅ Azure OpenAI client created: azure_openai_client.py")

    def create_setup_instructions(self):
        """Create setup instructions for Azure OpenAI"""
        logger.info("📋 Creating Azure OpenAI setup instructions...")

        instructions = f"""# Azure OpenAI Setup Instructions for COOL BITS SRL

## Overview
This guide provides step-by-step instructions for setting up Azure OpenAI integration for {self.company} projects: {', '.join(self.project_domains)}.

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
- **Model**: {self.azure_openai_config['model']}
- **Deployment**: {self.azure_openai_config['deployment_name']}
- **API Version**: {self.azure_openai_config['api_version']}
- **Max Tokens**: {self.azure_openai_config['max_tokens']}
- **Temperature**: {self.azure_openai_config['temperature']}

### 5. Testing
Run the test script to verify configuration:
```bash
python azure_openai_client.py
```

## Integration Points

### coolbits.ai Integration
- **Endpoint**: {self.integration_endpoints['coolbits_ai']}
- **Use Cases**: Code generation, document processing, API integration
- **Authentication**: Azure OpenAI API key

### cblm.ai Integration
- **Endpoint**: {self.integration_endpoints['cblm_ai']}
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
- **Company**: {self.company}
- **CEO**: {self.ceo}
- **Domains**: {', '.join(self.project_domains)}

Generated: {datetime.now().isoformat()}
"""

        with open("AZURE_OPENAI_SETUP_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
            f.write(instructions)

        logger.info("✅ Setup instructions created: AZURE_OPENAI_SETUP_INSTRUCTIONS.md")

    def run_complete_setup(self):
        """Run complete Azure OpenAI setup"""
        logger.info("🚀 Running complete Azure OpenAI setup for COOL BITS SRL...")

        print("=" * 80)
        print("🤖 AZURE OPENAI SETUP FOR COOL BITS SRL")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"🌐 Domains: {', '.join(self.project_domains)}")
        print("=" * 80)

        # Generate configuration files
        self.create_azure_openai_config_file()
        self.create_env_file()
        self.create_azure_openai_client()
        self.create_setup_instructions()

        print("\n✅ Azure OpenAI setup completed successfully!")
        print("\n📁 Generated Files:")
        print("  • azure_openai_config.json - Configuration data")
        print("  • .env - Environment variables")
        print("  • azure_openai_client.py - Python client")
        print("  • AZURE_OPENAI_SETUP_INSTRUCTIONS.md - Setup guide")

        print("\n🔧 Next Steps:")
        print("  1. Update .env file with your actual Azure OpenAI API key")
        print("  2. Configure your Azure OpenAI resource endpoint")
        print("  3. Test the configuration with: python azure_openai_client.py")
        print("  4. Integrate with your coolbits.ai and cblm.ai projects")

        logger.info("🎉 Complete Azure OpenAI setup finished successfully")


def main():
    """Main function"""
    config = AzureOpenAIConfig()
    config.run_complete_setup()


if __name__ == "__main__":
    main()
