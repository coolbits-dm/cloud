#!/usr/bin/env python3
"""
Azure OpenAI Client for COOL BITS SRL
Integration with coolbits.ai and cblm.ai
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CoolBitsAzureOpenAIClient:
    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.domains = ["coolbits.ai", "cblm.ai"]

        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )

        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.model = os.getenv("AZURE_OPENAI_MODEL")

        logger.info(f"✅ Azure OpenAI client initialized for {self.company}")
        logger.info(f"🏢 Domains: {', '.join(self.domains)}")
        logger.info(f"🤖 Model: {self.model}")
        logger.info(f"📦 Deployment: {self.deployment_name}")

    def generate_text(
        self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7
    ):
        """Generate text using Azure OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an AI assistant for {self.company}, helping with {', '.join(self.domains)} projects.",
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
        """Generate code using Azure OpenAI"""
        system_prompt = f"""You are a senior software engineer for COOL BITS SRL, specializing in {language} development for coolbits.ai, cblm.ai projects.
        
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

    def analyze_document(self, content: str, analysis_type: str = "general"):
        """Analyze document content using Azure OpenAI"""
        system_prompt = """You are a document analysis specialist for COOL BITS SRL, working on coolbits.ai, cblm.ai projects.
        
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
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Analyze this document ({analysis_type}): {content}",
                    },
                ],
                max_tokens=4000,
                temperature=0.5,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ Error analyzing document: {e}")
            return None

    def get_usage_stats(self):
        """Get usage statistics for Azure OpenAI"""
        try:
            # This would typically call Azure OpenAI usage API
            # For now, return mock data
            return {
                "company": self.company,
                "domains": self.domains,
                "total_requests": 0,
                "total_tokens": 0,
                "cost_estimate": 0.0,
                "last_updated": "2025-09-07T13:45:14.304935",
            }

        except Exception as e:
            logger.error(f"❌ Error getting usage stats: {e}")
            return None


def main():
    """Main function for testing Azure OpenAI client"""
    print("=" * 80)
    print("🤖 COOL BITS SRL AZURE OPENAI CLIENT")
    print("=" * 80)
    print("🏢 Company: COOL BITS SRL")
    print("👤 CEO: Andrei")
    print("🌐 Domains: coolbits.ai, cblm.ai")
    print("=" * 80)

    client = CoolBitsAzureOpenAIClient()

    # Test text generation
    print("\n🧪 Testing text generation...")
    test_prompt = (
        "Explain the benefits of using Azure OpenAI for enterprise applications"
    )
    response = client.generate_text(test_prompt)

    if response:
        print("✅ Text generation successful")
        print(f"📝 Response: {response[:200]}...")
    else:
        print("❌ Text generation failed")

    # Test code generation
    print("\n🧪 Testing code generation...")
    code_prompt = "Create a Python function to validate email addresses"
    code_response = client.generate_code(code_prompt)

    if code_response:
        print("✅ Code generation successful")
        print(f"💻 Code: {code_response[:200]}...")
    else:
        print("❌ Code generation failed")

    # Get usage stats
    print("\n📊 Usage Statistics:")
    stats = client.get_usage_stats()
    if stats:
        print(f"📈 Total Requests: {stats['total_requests']}")
        print(f"🔢 Total Tokens: {stats['total_tokens']}")
        print(f"💰 Cost Estimate: ${stats['cost_estimate']:.2f}")


if __name__ == "__main__":
    main()
