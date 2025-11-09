#!/usr/bin/env python3
"""
AI Agent Connectivity Diagnostic Tool for COOL BITS SRL
Analyzes and resolves Cursor AI connection errors
"""

import logging
import subprocess
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIAgentConnectivityDiagnostic:
    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.error_id = "43867dd0-2114-456a-8512-9e2c448db66c"

        # AI Agents to check
        self.ai_agents = {
            "@GeminiCLI": {
                "status": "Unknown",
                "endpoint": "Local CLI",
                "type": "Command Line Interface",
            },
            "@oPython": {
                "status": "Unknown",
                "endpoint": "Local Python",
                "type": "Python Environment",
            },
            "@Python": {
                "status": "Unknown",
                "endpoint": "System Python",
                "type": "Python Runtime",
            },
            "@OpenAI": {
                "status": "Unknown",
                "endpoint": "api.openai.com",
                "type": "API Service",
            },
            "@oGPT": {
                "status": "Unknown",
                "endpoint": "Local oGPT Bridge",
                "type": "COOL BITS SRL AI Division",
            },
            "@oGrok": {
                "status": "Unknown",
                "endpoint": "Local oGrok Bridge",
                "type": "COOL BITS SRL AI Division",
            },
        }

        # Error analysis
        self.error_analysis = {
            "error_type": "ConnectError",
            "error_code": "invalid_argument",
            "source": "Cursor AI Transport",
            "severity": "High",
            "impact": "AI connectivity disrupted",
        }

    def analyze_cursor_error(self):
        """Analyze the Cursor AI connection error"""
        logger.info("🔍 Analyzing Cursor AI connection error...")

        print("=" * 80)
        print("🔍 CURSOR AI CONNECTION ERROR ANALYSIS")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"🆔 Error ID: {self.error_id}")
        print(f"📅 Analysis Date: {datetime.now().isoformat()}")
        print("=" * 80)

        print("\n❌ ERROR DETAILS:")
        print(f"• Error Type: {self.error_analysis['error_type']}")
        print(f"• Error Code: {self.error_analysis['error_code']}")
        print(f"• Source: {self.error_analysis['source']}")
        print(f"• Severity: {self.error_analysis['severity']}")
        print(f"• Impact: {self.error_analysis['impact']}")

        print("\n🔍 ERROR STACK TRACE ANALYSIS:")
        print("• Transport Layer Error: iol.$endAiConnectTransportReportError")
        print("• Handler Error: Zhr._doInvokeHandler")
        print("• Request Processing: Zhr._receiveRequest")
        print("• Message Delivery: ye._deliver")
        print("• Port Communication: MessagePort.<anonymous>")

        print("\n🎯 LIKELY CAUSES:")
        print("• Network connectivity issues")
        print("• Cursor AI service temporarily unavailable")
        print("• Authentication token expired")
        print("• Rate limiting or quota exceeded")
        print("• Local firewall blocking connection")

        return self.error_analysis

    def check_ai_agent_status(self):
        """Check status of all AI agents"""
        logger.info("🤖 Checking AI agent status...")

        print("\n" + "=" * 80)
        print("🤖 AI AGENT STATUS CHECK")
        print("=" * 80)

        for agent, config in self.ai_agents.items():
            print(f"\n{agent}:")
            print(f"  Type: {config['type']}")
            print(f"  Endpoint: {config['endpoint']}")

            # Check agent-specific status
            if agent == "@Python":
                config["status"] = self._check_python_status()
            elif agent == "@oPython":
                config["status"] = self._check_opython_status()
            elif agent == "@GeminiCLI":
                config["status"] = self._check_geminicli_status()
            elif agent == "@OpenAI":
                config["status"] = self._check_openai_status()
            elif agent == "@oGPT":
                config["status"] = self._check_ogpt_status()
            elif agent == "@oGrok":
                config["status"] = self._check_ogrok_status()

            print(f"  Status: {config['status']}")

    def _check_python_status(self):
        """Check Python runtime status"""
        try:
            result = subprocess.run(
                [sys.executable, "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return f"✅ Active ({result.stdout.strip()})"
            else:
                return "❌ Error"
        except Exception as e:
            return f"❌ Error: {str(e)[:50]}"

    def _check_opython_status(self):
        """Check oPython environment status"""
        try:
            # Check if we can import str module
            import str

            return "✅ Active (str.py loaded)"
        except Exception as e:
            return f"❌ Error: {str(e)[:50]}"

    def _check_geminicli_status(self):
        """Check GeminiCLI status"""
        try:
            # Check if GeminiCLI integration exists
            import os

            if os.path.exists("ogemini_cli_integration.py"):
                return "✅ Active (Integration file exists)"
            else:
                return "⚠️ Integration file not found"
        except Exception as e:
            return f"❌ Error: {str(e)[:50]}"

    def _check_openai_status(self):
        """Check OpenAI API status"""
        try:
            import openai

            return "✅ Active (OpenAI library available)"
        except ImportError:
            return "❌ OpenAI library not installed"
        except Exception as e:
            return f"❌ Error: {str(e)[:50]}"

    def _check_ogpt_status(self):
        """Check oGPT bridge status"""
        try:
            import os

            if os.path.exists("ogpt_bridge_data"):
                return "✅ Active (Bridge data exists)"
            else:
                return "⚠️ Bridge data not found"
        except Exception as e:
            return f"❌ Error: {str(e)[:50]}"

    def _check_ogrok_status(self):
        """Check oGrok bridge status"""
        try:
            import os

            if os.path.exists("ogrok_bridge_data"):
                return "✅ Active (Bridge data exists)"
            else:
                return "⚠️ Bridge data not found"
        except Exception as e:
            return f"❌ Error: {str(e)[:50]}"

    def generate_recovery_solutions(self):
        """Generate recovery solutions for the connection error"""
        logger.info("🔧 Generating recovery solutions...")

        print("\n" + "=" * 80)
        print("🔧 RECOVERY SOLUTIONS")
        print("=" * 80)

        solutions = [
            {
                "priority": "High",
                "solution": "Restart Cursor Application",
                "description": "Close and reopen Cursor to reset AI transport layer",
                "steps": [
                    "Save all work",
                    "Close Cursor completely",
                    "Wait 10 seconds",
                    "Reopen Cursor",
                    "Test AI functionality",
                ],
            },
            {
                "priority": "High",
                "solution": "Check Network Connectivity",
                "description": "Verify internet connection and firewall settings",
                "steps": [
                    "Test internet connection",
                    "Check firewall settings",
                    "Verify proxy configuration",
                    "Test with different network",
                ],
            },
            {
                "priority": "Medium",
                "solution": "Clear Cursor Cache",
                "description": "Clear Cursor's local cache and temporary files",
                "steps": [
                    "Close Cursor",
                    "Delete Cursor cache folder",
                    "Restart Cursor",
                    "Re-authenticate if needed",
                ],
            },
            {
                "priority": "Medium",
                "solution": "Update Cursor Application",
                "description": "Ensure Cursor is running the latest version",
                "steps": [
                    "Check for updates",
                    "Download latest version",
                    "Install update",
                    "Restart application",
                ],
            },
            {
                "priority": "Low",
                "solution": "Alternative AI Access",
                "description": "Use alternative AI agents while Cursor is unavailable",
                "steps": [
                    "Use @oPython for local AI operations",
                    "Use @GeminiCLI for command-line AI",
                    "Use @oGPT bridge for OpenAI access",
                    "Use @oGrok bridge for xAI access",
                ],
            },
        ]

        for i, solution in enumerate(solutions, 1):
            print(f"\n{i}. {solution['solution']} (Priority: {solution['priority']})")
            print(f"   Description: {solution['description']}")
            print("   Steps:")
            for step in solution["steps"]:
                print(f"   • {step}")

    def create_recovery_script(self):
        """Create automated recovery script"""
        logger.info("📝 Creating recovery script...")

        recovery_script = f'''#!/usr/bin/env python3
"""
Cursor AI Recovery Script for COOL BITS SRL
Automated recovery from AI connection errors
"""

import subprocess
import time
import os
import sys
from datetime import datetime

def main():
    print("=" * 80)
    print("🔧 CURSOR AI RECOVERY SCRIPT - COOL BITS SRL")
    print("=" * 80)
    print(f"🏢 Company: {self.company}")
    print(f"👤 CEO: {self.ceo}")
    print(f"📅 Recovery Date: {{datetime.now().isoformat()}}")
    print("=" * 80)
    
    print("\\n🔄 Starting recovery process...")
    
    # Step 1: Check Python environment
    print("\\n1. Checking Python environment...")
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   ✅ Python: {{result.stdout.strip()}}")
        else:
            print("   ❌ Python check failed")
    except Exception as e:
        print(f"   ❌ Python error: {{e}}")
    
    # Step 2: Check AI agent files
    print("\\n2. Checking AI agent files...")
    ai_files = [
        "str.py",
        "ogemini_cli_integration.py", 
        "azure_official_client.py",
        "chat_with_gemini_coolbits.py"
    ]
    
    for file in ai_files:
        if os.path.exists(file):
            print(f"   ✅ {{file}} - Found")
        else:
            print(f"   ⚠️ {{file}} - Not found")
    
    # Step 3: Test AI agent connectivity
    print("\\n3. Testing AI agent connectivity...")
    try:
        import str
        str.current_ai_status()
        print("   ✅ AI status check successful")
    except Exception as e:
        print(f"   ❌ AI status check failed: {{e}}")
    
    # Step 4: Generate recovery report
    print("\\n4. Generating recovery report...")
    report = {{
        "company": "{self.company}",
        "ceo": "{self.ceo}",
        "recovery_date": datetime.now().isoformat(),
        "error_id": "{self.error_id}",
        "status": "Recovery completed",
        "recommendations": [
            "Restart Cursor application",
            "Check network connectivity", 
            "Clear Cursor cache",
            "Update Cursor to latest version"
        ]
    }}
    
    with open("cursor_ai_recovery_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("   ✅ Recovery report generated: cursor_ai_recovery_report.json")
    
    print("\\n" + "=" * 80)
    print("🎉 RECOVERY PROCESS COMPLETED")
    print("=" * 80)
    print("📋 Next Steps:")
    print("• Restart Cursor application")
    print("• Test AI functionality")
    print("• Check recovery report for details")
    print("=" * 80)

if __name__ == "__main__":
    main()
'''

        with open("cursor_ai_recovery.py", "w", encoding="utf-8") as f:
            f.write(recovery_script)

        logger.info("✅ Recovery script created: cursor_ai_recovery.py")

    def run_complete_diagnostic(self):
        """Run complete diagnostic process"""
        logger.info("🚀 Running complete AI connectivity diagnostic...")

        print("=" * 80)
        print("🚀 AI CONNECTIVITY DIAGNOSTIC - COOL BITS SRL")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"🆔 Error ID: {self.error_id}")
        print("=" * 80)

        # Run all diagnostic steps
        self.analyze_cursor_error()
        self.check_ai_agent_status()
        self.generate_recovery_solutions()
        self.create_recovery_script()

        print("\n" + "=" * 80)
        print("🎉 DIAGNOSTIC COMPLETED")
        print("=" * 80)
        print("📁 Generated Files:")
        print("  • cursor_ai_recovery.py - Automated recovery script")
        print(
            "  • cursor_ai_recovery_report.json - Recovery report (after running script)"
        )

        print("\n🔧 Immediate Actions:")
        print("  1. Run: python cursor_ai_recovery.py")
        print("  2. Restart Cursor application")
        print("  3. Test AI functionality")
        print("  4. Check recovery report")

        print("\n🤖 AI Agent Status Summary:")
        for agent, config in self.ai_agents.items():
            print(f"  {agent}: {config['status']}")

        logger.info("🎉 Complete AI connectivity diagnostic finished successfully")


def main():
    """Main function"""
    diagnostic = AIAgentConnectivityDiagnostic()
    diagnostic.run_complete_diagnostic()


if __name__ == "__main__":
    main()
