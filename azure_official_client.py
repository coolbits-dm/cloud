#!/usr/bin/env python3
"""
Official Azure OpenAI Client for COOL BITS SRL
Integration with official Microsoft Azure account: andrei@coolbits.ro
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
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CoolBitsOfficialAzureOpenAI:
    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.official_email = "andrei@coolbits.ro"
        self.project_email = "andrei@coolbits.ai"
        self.domains = ["coolbits.ai", "cblm.ai"]

        # Load official configuration
        self.config = self._load_official_config()

        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=self.config.get("api_key", os.getenv("AZURE_OPENAI_API_KEY")),
            api_version=self.config.get(
                "api_version", os.getenv("AZURE_OPENAI_API_VERSION")
            ),
            azure_endpoint=self.config.get(
                "endpoint", os.getenv("AZURE_OPENAI_ENDPOINT")
            ),
        )

        self.deployment_name = self.config.get(
            "deployment_name", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        )
        self.model = self.config.get("model", os.getenv("AZURE_OPENAI_MODEL"))

        logger.info(f"✅ Official Azure OpenAI client initialized for {self.company}")
        logger.info(f"📧 Official Email: {self.official_email}")
        logger.info(f"🌐 Project Email: {self.project_email}")
        logger.info(f"🏢 Domains: {', '.join(self.domains)}")
        logger.info(f"🤖 Model: {self.model}")
        logger.info(f"📦 Deployment: {self.deployment_name}")

    def _load_official_config(self):
        """Load official Azure configuration"""
        try:
            with open("azure_official_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("⚠️ Official config not found, using environment variables")
            return {}

    def generate_text(
        self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7
    ):
        """Generate text using official Azure OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an AI assistant for {self.company}, helping with {', '.join(self.domains)} projects. Official account: {self.official_email}.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ Error generating text: {e}")
            return None

    def generate_code(self, prompt: str, language: str = "python"):
        """Generate code using official Azure OpenAI"""
        system_prompt = f"""You are a senior software engineer for COOL BITS SRL, specializing in {language} development for coolbits.ai, cblm.ai projects.
        
        Official Microsoft Azure account: andrei@coolbits.ro
        Project email: andrei@coolbits.ai
        
        Generate clean, efficient, and well-documented code that follows best practices.
        Include proper error handling and logging.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Generate {language} code for: {prompt}",
                    },
                ],
                max_tokens=4000,
                temperature=0.3,
                top_p=1.0,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ Error generating code: {e}")
            return None

    def get_account_info(self):
        """Get official Azure account information"""
        return {
            "company": self.company,
            "ceo": self.ceo,
            "official_email": self.official_email,
            "project_email": self.project_email,
            "domains": self.domains,
            "azure_resource": self.config.get("openai_resource", "N/A"),
            "subscription_id": self.config.get("subscription_id", "N/A"),
            "resource_group": self.config.get("resource_group", "N/A"),
            "model": self.model,
            "deployment": self.deployment_name,
            "last_updated": "2025-09-07T13:47:51.643397",
        }


def main():
    """Main function for testing official Azure OpenAI client"""
    print("=" * 80)
    print("🤖 COOL BITS SRL OFFICIAL AZURE OPENAI CLIENT")
    print("=" * 80)
    print(f"🏢 Company: COOL BITS SRL")
    print(f"👤 CEO: Andrei")
    print(f"📧 Official Email: andrei@coolbits.ro")
    print(f"🌐 Project Email: andrei@coolbits.ai")
    print(f"🏢 Domains: coolbits.ai, cblm.ai")
    print("=" * 80)

    client = CoolBitsOfficialAzureOpenAI()

    # Display account info
    print("\n📊 Official Account Information:")
    account_info = client.get_account_info()
    for key, value in account_info.items():
        print(f"  {key}: {value}")

    # Test text generation
    print("\n🧪 Testing text generation...")
    test_prompt = "Explain the benefits of using official Azure OpenAI for enterprise applications"
    response = client.generate_text(test_prompt)

    if response:
        print(f"✅ Text generation successful")
        print(f"📝 Response: {response[:200]}...")
    else:
        print("❌ Text generation failed")

    # Test code generation
    print("\n🧪 Testing code generation...")
    code_prompt = "Create a Python function to validate email addresses"
    code_response = client.generate_code(code_prompt)

    if code_response:
        print(f"✅ Code generation successful")
        print(f"💻 Code: {code_response[:200]}...")
    else:
        print("❌ Code generation failed")


if __name__ == "__main__":
    main()
