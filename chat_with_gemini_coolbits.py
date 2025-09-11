#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@oGemini Vertex AI Chat Integration
Interactive chat with Gemini model on Google Cloud Vertex AI for CoolBits.ai
"""

import sys
import os
import json
import logging
import requests
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import vertexai
    from vertexai.preview.generative_models import GenerativeModel, Part, ChatSession

    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logger.warning(
        "Vertex AI SDK not installed. Run: pip install google-cloud-aiplatform"
    )


class CoolBitsGeminiChat:
    """
    Interactive Gemini chat with CoolBits.ai integration
    """

    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.project_id = "coolbits-ai"
        self.region = "europe-west3"
        self.model_name = "gemini-pro"

        # CoolBits.ai API configuration
        self.coolbits_api_config = {
            "base_url": "https://api.coolbits.ai/v1",
            "endpoints": {
                "chat": "/chat",
                "analyze": "/analyze",
                "generate": "/generate",
                "platform": "/platform",
            },
        }

        # Initialize chat session
        self.chat_session = None
        self.model = None

    def setup_vertex_ai(self):
        """Setup Vertex AI with project configuration"""
        if not VERTEX_AI_AVAILABLE:
            print("❌ Vertex AI SDK not available. Please install with:")
            print("   pip install google-cloud-aiplatform")
            return False

        try:
            logger.info(f"Initializing Vertex AI for project: {self.project_id}")
            vertexai.init(project=self.project_id, location=self.region)

            logger.info(f"Loading Gemini model: {self.model_name}")
            self.model = GenerativeModel(self.model_name)
            self.chat_session = self.model.start_chat()

            logger.info("✅ Vertex AI initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Vertex AI setup failed: {e}")
            print(f"❌ Error: {e}")
            print(
                "💡 Make sure you're authenticated with: gcloud auth application-default login"
            )
            return False

    def call_coolbits_api(self, user_input: str) -> Optional[str]:
        """Call CoolBits.ai API for enhanced responses"""
        try:
            # Simulate CoolBits.ai API call
            # In production, replace with actual API calls

            if "coolbits" in user_input.lower() or "cblm" in user_input.lower():
                api_response = {
                    "status": "success",
                    "response": f"CoolBits.ai API response for: {user_input[:50]}...",
                    "timestamp": datetime.now().isoformat(),
                    "company": self.company,
                    "ceo": self.ceo,
                }

                logger.info("CoolBits.ai API called successfully")
                return json.dumps(api_response, indent=2)

            return None

        except Exception as e:
            logger.error(f"CoolBits.ai API call failed: {e}")
            return f"API Error: {e}"

    def process_user_input(self, user_input: str) -> str:
        """Process user input and generate response"""
        try:
            # Check for CoolBits.ai specific commands
            if user_input.lower().startswith("/coolbits"):
                return self.handle_coolbits_command(user_input)

            # Check for system commands
            if user_input.lower().startswith("/"):
                return self.handle_system_command(user_input)

            # Send to Gemini model
            if self.chat_session:
                response = self.chat_session.send_message(user_input)
                return response.text
            else:
                return "❌ Chat session not initialized"

        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return f"❌ Error: {e}"

    def handle_coolbits_command(self, command: str) -> str:
        """Handle CoolBits.ai specific commands"""
        cmd_parts = command.split()

        if len(cmd_parts) < 2:
            return "Usage: /coolbits <command>\nCommands: info, status, api, help"

        subcommand = cmd_parts[1].lower()

        if subcommand == "info":
            return f"""
🏢 CoolBits.ai Information:
   Company: {self.company}
   CEO: {self.ceo}
   Project ID: {self.project_id}
   Region: {self.region}
   Model: {self.model_name}
   Status: Active
"""

        elif subcommand == "status":
            return f"""
📊 CoolBits.ai Status:
   Vertex AI: {'✅ Active' if self.chat_session else '❌ Inactive'}
   Model: {self.model_name}
   Chat Session: {'✅ Active' if self.chat_session else '❌ Not started'}
   API Integration: ✅ Ready
"""

        elif subcommand == "api":
            api_response = self.call_coolbits_api("CoolBits.ai API test")
            return f"🔌 CoolBits.ai API Response:\n{api_response}"

        elif subcommand == "help":
            return """
🆘 CoolBits.ai Commands:
   /coolbits info    - Show company information
   /coolbits status  - Show system status
   /coolbits api     - Test API integration
   /coolbits help    - Show this help
"""

        else:
            return f"❌ Unknown command: {subcommand}\nType '/coolbits help' for available commands"

    def handle_system_command(self, command: str) -> str:
        """Handle system commands"""
        cmd_parts = command.split()
        cmd = cmd_parts[0].lower()

        if cmd == "/help":
            return """
🆘 Available Commands:
   /help           - Show this help
   /clear          - Clear chat history
   /status         - Show system status
   /coolbits <cmd> - CoolBits.ai commands
   /quit, /exit    - Exit chat
"""

        elif cmd == "/clear":
            if self.chat_session:
                self.chat_session = self.model.start_chat()
                return "✅ Chat history cleared"
            else:
                return "❌ No active chat session"

        elif cmd == "/status":
            return f"""
📊 System Status:
   Company: {self.company}
   Project: {self.project_id}
   Region: {self.region}
   Model: {self.model_name}
   Chat Session: {'✅ Active' if self.chat_session else '❌ Not started'}
   Vertex AI: {'✅ Available' if VERTEX_AI_AVAILABLE else '❌ Not installed'}
"""

        else:
            return f"❌ Unknown command: {cmd}\nType '/help' for available commands"

    def start_chat(self):
        """Start interactive chat session"""
        print("=" * 80)
        print("🤖 COOLBITS.AI GEMINI VERTEX AI CHAT")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"🆔 Project: {self.project_id}")
        print(f"🌍 Region: {self.region}")
        print(f"🤖 Model: {self.model_name}")
        print("=" * 80)

        # Setup Vertex AI
        if not self.setup_vertex_ai():
            print("❌ Failed to setup Vertex AI. Exiting...")
            return

        print("✅ Gemini chat initialized successfully!")
        print("💬 Type your message and press Enter to chat with Gemini")
        print("🆘 Type '/help' for available commands")
        print("🚪 Type 'quit' or 'exit' to end the conversation")
        print("-" * 80)

        # Main chat loop
        while True:
            try:
                # Non-interactive mode check
                if os.getenv('CI') == '1' or os.getenv('NO_COLOR') == '1':
                    print("🤖 Non-interactive mode: Chat session running in background")
                    time.sleep(60)  # Sleep for 1 minute then check again
                    continue
                    
                # Get user input
                user_input = input("\n👤 You: ").strip()

                # Check for exit commands
                if user_input.lower() in ["quit", "exit", "/quit", "/exit"]:
                    print("\n👋 Goodbye! Thanks for chatting with CoolBits.ai Gemini!")
                    break

                # Skip empty input
                if not user_input:
                    continue

                # Process input and get response
                response = self.process_user_input(user_input)

                # Print response
                print(f"\n🤖 Gemini: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Chat error: {e}")
                print(f"\n❌ Error: {e}")
                print("💡 Try again or type '/help' for assistance")


def main():
    """Main entry point"""
    print("🚀 Starting CoolBits.ai Gemini Vertex AI Chat...")

    try:
        chat = CoolBitsGeminiChat()
        chat.start_chat()

    except Exception as e:
        logger.error(f"Failed to start chat: {e}")
        print(f"❌ Failed to start chat: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
