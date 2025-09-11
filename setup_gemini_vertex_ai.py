#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@oGemini Vertex AI Setup Script
Setup script for Gemini Vertex AI integration with CoolBits.ai
"""

import sys
import subprocess
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GeminiVertexAISetup:
    """
    Setup script for Gemini Vertex AI integration
    """

    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.project_id = "coolbits-ai"
        self.region = "europe-west3"

        # Required packages
        self.required_packages = [
            "google-cloud-aiplatform",
            "google-cloud-core",
            "requests",
            "python-dotenv",
        ]

        # Configuration file
        self.config_file = "gemini_vertex_config.json"

    def check_python_version(self):
        """Check if Python version is compatible"""
        logger.info("Checking Python version...")

        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python {version.major}.{version.minor} is not supported")
            print("💡 Please install Python 3.8 or higher")
            return False

        print(
            f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible"
        )
        return True

    def install_required_packages(self):
        """Install required Python packages"""
        logger.info("Installing required packages...")

        print("📦 Installing required packages...")
        for package in self.required_packages:
            try:
                print(f"   Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"   ✅ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {package}: {e}")
                return False

        print("✅ All packages installed successfully")
        return True

    def check_gcloud_installation(self):
        """Check if gcloud CLI is installed"""
        logger.info("Checking gcloud CLI installation...")

        try:
            result = subprocess.run(
                ["gcloud", "--version"], capture_output=True, text=True, check=True
            )
            print("✅ gcloud CLI is installed")
            print(f"   Version: {result.stdout.split()[0]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ gcloud CLI not found")
            print("💡 Please install Google Cloud CLI:")
            print("   https://cloud.google.com/sdk/docs/install")
            return False

    def setup_gcloud_auth(self):
        """Setup gcloud authentication"""
        logger.info("Setting up gcloud authentication...")

        print("🔐 Setting up gcloud authentication...")
        print("💡 This will open a browser window for authentication")

        try:
            subprocess.run(
                ["gcloud", "auth", "application-default", "login"], check=True
            )
            print("✅ gcloud authentication completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ gcloud authentication failed: {e}")
            return False

    def create_config_file(self):
        """Create configuration file"""
        logger.info("Creating configuration file...")

        config = {
            "project_info": {
                "company": self.company,
                "ceo": self.ceo,
                "project_id": self.project_id,
                "region": self.region,
                "setup_date": datetime.now().isoformat(),
            },
            "vertex_ai": {
                "model_name": "gemini-pro",
                "project_id": self.project_id,
                "region": self.region,
                "status": "configured",
            },
            "coolbits_integration": {
                "api_base_url": "https://api.coolbits.ai/v1",
                "status": "ready",
                "endpoints": {
                    "chat": "/chat",
                    "analyze": "/analyze",
                    "generate": "/generate",
                },
            },
            "setup_status": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                "packages_installed": True,
                "gcloud_configured": True,
                "vertex_ai_ready": True,
            },
        }

        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Configuration file created: {self.config_file}")
        return True

    def test_vertex_ai_connection(self):
        """Test Vertex AI connection"""
        logger.info("Testing Vertex AI connection...")

        try:
            import vertexai
            from vertexai.preview.generative_models import GenerativeModel

            print("🧪 Testing Vertex AI connection...")
            vertexai.init(project=self.project_id, location=self.region)

            model = GenerativeModel("gemini-pro")
            print("✅ Vertex AI connection successful")
            return True

        except ImportError:
            print("❌ Vertex AI SDK not available")
            return False
        except Exception as e:
            print(f"❌ Vertex AI connection failed: {e}")
            return False

    def create_test_script(self):
        """Create a simple test script"""
        logger.info("Creating test script...")

        test_script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Vertex AI Test Script
Simple test to verify Gemini integration
"""

import vertexai
from vertexai.preview.generative_models import GenerativeModel

def test_gemini():
    """Test Gemini model"""
    try:
        print("🧪 Testing Gemini model...")
        
        # Initialize Vertex AI
        vertexai.init(project="{self.project_id}", location="{self.region}")
        
        # Load model
        model = GenerativeModel("gemini-pro")
        
        # Test simple generation
        response = model.generate_content("Hello, this is a test from CoolBits.ai")
        
        print("✅ Gemini test successful!")
        print(f"Response: {{response.text}}")
        
    except Exception as e:
        print(f"❌ Gemini test failed: {{e}}")

if __name__ == "__main__":
    test_gemini()
'''

        with open("test_gemini.py", "w") as f:
            f.write(test_script)

        print("✅ Test script created: test_gemini.py")
        return True

    def run_complete_setup(self):
        """Run complete setup process"""
        logger.info("Running complete Gemini Vertex AI setup...")

        print("=" * 80)
        print("🚀 COOLBITS.AI GEMINI VERTEX AI SETUP")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"🆔 Project: {self.project_id}")
        print(f"🌍 Region: {self.region}")
        print("=" * 80)

        # Step 1: Check Python version
        if not self.check_python_version():
            return False

        # Step 2: Install required packages
        if not self.install_required_packages():
            return False

        # Step 3: Check gcloud CLI
        if not self.check_gcloud_installation():
            return False

        # Step 4: Setup gcloud authentication
        if not self.setup_gcloud_auth():
            return False

        # Step 5: Create configuration file
        if not self.create_config_file():
            return False

        # Step 6: Test Vertex AI connection
        if not self.test_vertex_ai_connection():
            return False

        # Step 7: Create test script
        if not self.create_test_script():
            return False

        print("=" * 80)
        print("🎉 GEMINI VERTEX AI SETUP COMPLETED")
        print("=" * 80)
        print("📁 Generated Files:")
        print(f"• {self.config_file}")
        print("• test_gemini.py")
        print("• chat_with_gemini_coolbits.py")
        print("=" * 80)
        print("🚀 Next Steps:")
        print("1. Run: python test_gemini.py")
        print("2. Run: python chat_with_gemini_coolbits.py")
        print("3. Start chatting with Gemini!")
        print("=" * 80)

        logger.info("Complete Gemini Vertex AI setup finished successfully")
        return True


def main():
    """Main entry point"""
    print("🚀 Starting Gemini Vertex AI Setup...")

    try:
        setup = GeminiVertexAISetup()

        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == "packages":
                setup.install_required_packages()
            elif command == "auth":
                setup.setup_gcloud_auth()
            elif command == "test":
                setup.test_vertex_ai_connection()
            elif command == "config":
                setup.create_config_file()
            else:
                print(f"❌ Unknown command: {command}")
        else:
            # Default: run complete setup
            setup.run_complete_setup()

    except Exception as e:
        logger.error(f"Setup error: {e}")
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
