#!/usr/bin/env python3
"""
oVertex Agent - Direct Communication with Gemini CLI
Bridge communication for COOL BITS SRL infrastructure setup
"""

import json
import time
from datetime import datetime
from coolbits_bridge import CoolBitsBridge


class oVertexGeminiCLICommunication:
    def __init__(self):
        self.bridge = CoolBitsBridge()
        self.bridge.initialize_bridge()

    def send_gemini_cli_message(self, message_type, content):
        """Send message to Gemini CLI agent"""
        message = {
            "from": "oVertex",
            "to": "oGeminiCLI",
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "priority": "high",
        }

        return self.bridge.send_to_gemini_cli(json.dumps(message), "gemini_cli_command")

    def request_infrastructure_analysis(self):
        """Request infrastructure analysis from Gemini CLI"""
        analysis_request = {
            "task": "infrastructure_analysis",
            "requirements": {
                "company": "COOL BITS SRL",
                "project_id": "coolbits-ai",
                "local_os": "Windows 11",
                "gpu": "NVIDIA RTX 2060",
                "cuda_version": "12.6",
                "storage": "NVMe SSD",
                "cpu_architecture": "x64",
            },
            "objectives": [
                "Best practices for CPU/GPU/Storage dependencies",
                "Certificate registration under COOL BITS SRL",
                "Vertex AI Layout Parser integration",
                "Document AI API setup",
                "Real-time sync pipeline implementation",
            ],
        }

        return self.send_gemini_cli_message(
            "infrastructure_analysis_request", analysis_request
        )

    def request_vertex_ai_setup(self):
        """Request Vertex AI setup from Gemini CLI"""
        vertex_setup = {
            "task": "vertex_ai_setup",
            "requirements": {
                "project_id": "coolbits-ai",
                "region": "europe-west3",
                "apis_to_enable": [
                    "Document AI API",
                    "Vertex AI API",
                    "Cloud Storage API",
                    "Secret Manager API",
                ],
                "layout_parser": {
                    "processor_type": "LAYOUT_PARSER_PROCESSOR",
                    "model": "gemini-2.5-pro-preview-05-06",
                },
            },
        }

        return self.send_gemini_cli_message("vertex_ai_setup_request", vertex_setup)


if __name__ == "__main__":
    # Initialize communication
    comm = oVertexGeminiCLICommunication()

    print("🚀 oVertex Agent - Initiating communication with Gemini CLI")
    print("=" * 60)

    # Send infrastructure analysis request
    print("📊 Sending infrastructure analysis request...")
    comm.request_infrastructure_analysis()

    # Send Vertex AI setup request
    print("🔧 Sending Vertex AI setup request...")
    comm.request_vertex_ai_setup()

    print("✅ Communication initiated successfully!")
    print("📡 Waiting for Gemini CLI responses...")

    # Wait for responses
    time.sleep(5)
    responses = comm.bridge.receive_from_gemini_cli()

    if responses:
        print(f"📥 Received {len(responses)} responses from Gemini CLI")
        for response in responses:
            print(f"Response: {response}")
    else:
        print("⏳ No responses yet - Gemini CLI may be processing...")
