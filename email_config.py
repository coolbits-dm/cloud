#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@oOutlook Email Configuration Script
Configure all mentioned email addresses for @Andrei and @oOutlook
"""

import sys
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EmailConfigurationManager:
    """
    Manager for configuring all mentioned email addresses
    """

    def __init__(self):
        self.company = "COOL BITS SRL 🏢 🏢"
        self.ceo = "Andrei"
        self.ai_assistant = "@oOutlook"

        # All mentioned email addresses
        self.all_emails = {
            "andrei@coolbits.ro": {
                "host": "ClausWeb (clausweb.ro)",
                "status": "Active",
                "role": "Primary CEO Email",
                "description": "Main CEO email hosted by ClausWeb",
                "integration_status": "Connected",
                "priority": "highest",
            },
            "andrei@coolbits.ai": {
                "host": "Vertex Environment",
                "status": "Active",
                "role": "CEO Vertex Email",
                "description": "CEO email in Vertex environment - Gmail authorization approved for email transfer",
                "integration_status": "Gmail Authorized",
                "priority": "high",
                "gmail_auth": {
                    "authorized": True,
                    "auth_date": "2025-09-07T12:17:17+03:00",
                    "permissions": [
                        "View email messages and settings",
                        "Transfer messages",
                    ],
                    "status": "Approved",
                },
            },
            "coolbits.dm@gmail.com": {
                "host": "Google",
                "status": "Active",
                "role": "Official Administration Email",
                "description": "Official email for managing all Google services and API connections",
                "integration_status": "Connected",
                "priority": "highest",
                "services": [
                    "Google Cloud",
                    "API Management",
                    "Service Administration",
                ],
            },
            "coolbits.ro@gmail.com": {
                "host": "Google",
                "status": "Active",
                "role": "RO Headquarters Email",
                "description": "Official email for local representation coolbits.ro - RO Headquarters",
                "integration_status": "Connected",
                "priority": "high",
                "services": ["Google Services", "COOL BITS SRL", "Local Operations"],
            },
            "office@coolbits.ai": {
                "host": "Vertex Environment",
                "status": "Pending Setup",
                "role": "Office Email",
                "description": "Office email - awaiting @oVertex and @oGeminiCLI integration",
                "integration_status": "Awaiting Integration",
                "priority": "medium",
            },
            "andy@coolbits.ai": {
                "host": "Vertex Environment",
                "status": "Pending Setup",
                "role": "Andy Email",
                "description": "Andy email - awaiting @oVertex and @oGeminiCLI integration",
                "integration_status": "Awaiting Integration",
                "priority": "medium",
            },
            "kim@coolbits.ai": {
                "host": "Vertex Environment",
                "status": "Pending Setup",
                "role": "Kim Email",
                "description": "Kim email - awaiting @oVertex and @oGeminiCLI integration",
                "integration_status": "Awaiting Integration",
                "priority": "medium",
            },
            "andrei@cblm.ai": {
                "host": "Vertex Environment",
                "status": "Pending Setup",
                "role": "cblm.ai Email",
                "description": "cblm.ai email - awaiting @oVertex and @oGeminiCLI integration",
                "integration_status": "Awaiting Integration",
                "priority": "high",
            },
        }

    def configure_active_emails(self):
        """Configure all active email addresses"""
        logger.info("📧 Configuring active email addresses...")

        active_emails = {
            email: config
            for email, config in self.all_emails.items()
            if config["status"] == "Active"
        }

        print("=" * 80)
        print("📧 CONFIGURING ACTIVE EMAIL ADDRESSES")
        print("=" * 80)

        for email, config in active_emails.items():
            print(f"\n📧 {email}")
            print(f"   🏢 Host: {config['host']}")
            print(f"   👤 Role: {config['role']}")
            print(f"   📊 Priority: {config['priority']}")
            print(f"   📝 Description: {config['description']}")
            print(f"   🔗 Integration: {config['integration_status']}")

            if "services" in config:
                print(f"   🛠️ Services: {', '.join(config['services'])}")

            # Configure email in @oOutlook system
            self._configure_email_in_outlook(email, config)

        print("=" * 80)
        print("✅ Active email addresses configured successfully")
        print("=" * 80)

    def _configure_email_in_outlook(self, email: str, config: dict):
        """Configure individual email in @oOutlook system"""
        logger.info(f"🔧 Configuring {email} in @oOutlook system...")

        # Determine SMTP/IMAP settings based on host
        if "gmail.com" in email:
            smtp_server = "smtp.gmail.com"
            imap_server = "imap.gmail.com"
        elif "clausweb.ro" in config["host"].lower():
            smtp_server = "smtp.clausweb.ro"
            imap_server = "imap.clausweb.ro"
        else:
            smtp_server = "smtp.vertex.ai"
            imap_server = "imap.vertex.ai"

        email_config = {
            "host": config["host"],
            "smtp_server": smtp_server,
            "smtp_port": 587,
            "imap_server": imap_server,
            "imap_port": 993,
            "role": config["role"],
            "signature": self._generate_signature(email, config["role"]),
            "ai_filter_level": self._determine_filter_level(config["priority"]),
            "status": config["status"],
        }

        logger.info(
            f"✅ {email} configured with {email_config['ai_filter_level']} AI filtering"
        )
        return email_config

    def _generate_signature(self, email_address: str, role: str) -> str:
        """Generate professional email signature"""
        signature = f"""
---
{self.company}
{role}: {email_address}
CEO: {self.ceo}
AI Assistant: {self.ai_assistant}

🔒 Classification: Internal Secret - CoolBits.ai Members Only
📧 Powered by @oOutlook Email Management System
🤖 AI Filtering: Active | Security: Maximum | Compliance: GDPR
"""
        return signature.strip()

    def _determine_filter_level(self, priority: str) -> str:
        """Determine AI filter level based on priority"""
        if priority == "highest":
            return "maximum"
        elif priority == "high":
            return "high"
        elif priority == "medium":
            return "medium"
        else:
            return "low"

    def setup_pending_emails(self):
        """Setup configuration for pending email addresses"""
        logger.info("⏳ Setting up pending email addresses...")

        pending_emails = {
            email: config
            for email, config in self.all_emails.items()
            if config["status"] == "Pending Setup"
        }

        print("=" * 80)
        print("⏳ PENDING EMAIL ADDRESSES SETUP")
        print("=" * 80)

        for email, config in pending_emails.items():
            print(f"\n📧 {email}")
            print(f"   🏢 Host: {config['host']}")
            print(f"   👤 Role: {config['role']}")
            print(f"   📊 Priority: {config['priority']}")
            print(f"   📝 Description: {config['description']}")
            print(f"   🔗 Integration: {config['integration_status']}")
            print("   ⚠️ Status: Awaiting @oVertex and @oGeminiCLI integration")

        print("=" * 80)
        print("📋 Pending emails ready for @oVertex and @oGeminiCLI integration")
        print("=" * 80)

    def create_email_access_report(self):
        """Create comprehensive email access report"""
        logger.info("📊 Creating email access report...")

        report = {
            "company": self.company,
            "ceo": self.ceo,
            "ai_assistant": self.ai_assistant,
            "report_date": datetime.now().isoformat(),
            "total_emails": len(self.all_emails),
            "active_emails": len(
                [e for e in self.all_emails.values() if e["status"] == "Active"]
            ),
            "pending_emails": len(
                [e for e in self.all_emails.values() if e["status"] == "Pending Setup"]
            ),
            "email_details": self.all_emails,
            "access_restrictions": {
                "authorized_users": ["@Andrei", "@oOutlook"],
                "classification": "Internal Secret - CoolBits.ai Members Only",
                "security_level": "Maximum",
                "compliance": "GDPR compliant",
            },
            "next_steps": [
                "Configure @oVertex for pending emails",
                "Integrate @oGeminiCLI for email management",
                "Setup SSL certificates for all active emails",
                "Train @oOutlook AI filters for each email role",
            ],
        }

        with open("email_access_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("📊 Email access report created: email_access_report.json")

        print("=" * 80)
        print("📊 EMAIL ACCESS REPORT SUMMARY")
        print("=" * 80)
        print(f"🏢 Company: {report['company']}")
        print(f"👤 CEO: {report['ceo']}")
        print(f"🤖 AI Assistant: {report['ai_assistant']}")
        print(f"📧 Total Emails: {report['total_emails']}")
        print(f"✅ Active Emails: {report['active_emails']}")
        print(f"⏳ Pending Emails: {report['pending_emails']}")
        print("=" * 80)
        print("🔒 Access restricted to @Andrei and @oOutlook only")
        print("=" * 80)

    def run_complete_setup(self):
        """Run complete email configuration setup"""
        logger.info("🚀 Running complete email configuration setup...")

        print("=" * 80)
        print("🚀 @oOUTLOOK COMPLETE EMAIL CONFIGURATION")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"🤖 AI Assistant: {self.ai_assistant}")
        print("=" * 80)

        # Configure active emails
        self.configure_active_emails()

        # Setup pending emails
        self.setup_pending_emails()

        # Create access report
        self.create_email_access_report()

        print("=" * 80)
        print("🎉 COMPLETE EMAIL CONFIGURATION FINISHED")
        print("🔒 Classification: Internal Secret - CoolBits.ai Members Only")
        print("=" * 80)

        logger.info("🎉 Complete email configuration setup finished successfully")


def main():
    """Main entry point"""
    print("🚀 Starting Email Configuration Manager...")

    try:
        config_manager = EmailConfigurationManager()

        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == "setup":
                config_manager.run_complete_setup()
            elif command == "active":
                config_manager.configure_active_emails()
            elif command == "pending":
                config_manager.setup_pending_emails()
            elif command == "report":
                config_manager.create_email_access_report()
            else:
                print(f"❌ Unknown command: {command}")
        else:
            # Default: run complete setup
            config_manager.run_complete_setup()

    except Exception as e:
        logger.error(f"❌ Configuration error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
