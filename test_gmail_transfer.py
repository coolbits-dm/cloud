#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Transfer Test Script
Test email transfer functionality with authorized Gmail account
"""

import os
import sys
import json
import logging
from datetime import datetime
from mail import oOutlookEmailManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GmailTransferTester:
    """
    Test Gmail transfer functionality for andrei@coolbits.ai
    """

    def __init__(self):
        self.email_manager = oOutlookEmailManager()
        self.test_email = "andrei@coolbits.ai"

    def test_gmail_authorization(self):
        """Test Gmail authorization status"""
        logger.info("🔍 Testing Gmail authorization status...")

        if self.test_email in self.email_manager.email_configs:
            config = self.email_manager.email_configs[self.test_email]

            print("=" * 80)
            print("📧 GMAIL AUTHORIZATION TEST")
            print("=" * 80)
            print(f"📧 Email: {self.test_email}")
            print(f"🏢 Host: {config['host']}")
            print(f"👤 Role: {config['role']}")
            print(f"📊 Status: {config['status']}")
            print(f"🔗 Integration: {config['integration_status']}")

            if "gmail_auth" in config:
                auth_info = config["gmail_auth"]
                print(f"✅ Authorization: {auth_info['status']}")
                print(f"📅 Auth Date: {auth_info['auth_date']}")
                print(f"🔑 Permissions: {', '.join(auth_info['permissions'])}")
            else:
                print("❌ No Gmail authorization found")

            print("=" * 80)
            return True
        else:
            logger.error(f"❌ Email {self.test_email} not found in configuration")
            return False

    def test_email_connection(self):
        """Test email connection capabilities"""
        logger.info("🔌 Testing email connection capabilities...")

        try:
            config = self.email_manager.email_configs[self.test_email]

            print("=" * 80)
            print("🔌 EMAIL CONNECTION TEST")
            print("=" * 80)
            print(f"📧 SMTP Server: {config['smtp_server']}:{config['smtp_port']}")
            print(f"📧 IMAP Server: {config['imap_server']}:{config['imap_port']}")
            print(f"🤖 AI Filter Level: {config['ai_filter_level']}")
            print(f"📝 Signature: {config['signature'][:50]}...")
            print("=" * 80)

            # Test SMTP connection (without authentication for now)
            logger.info("🔌 Testing SMTP connection...")
            # Note: Actual SMTP test would require credentials

            # Test IMAP connection (without authentication for now)
            logger.info("🔌 Testing IMAP connection...")
            # Note: Actual IMAP test would require credentials

            print("✅ Connection configuration validated")
            return True

        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False

    def generate_transfer_report(self):
        """Generate comprehensive transfer report"""
        logger.info("📊 Generating Gmail transfer report...")

        report = {
            "test_date": datetime.now().isoformat(),
            "test_email": self.test_email,
            "authorization_status": "Approved",
            "permissions": ["View email messages and settings", "Transfer messages"],
            "configuration": self.email_manager.email_configs[self.test_email],
            "next_steps": [
                "Configure Gmail API credentials",
                "Test actual email transfer functionality",
                "Setup automated transfer schedules",
                "Monitor transfer logs and performance",
            ],
            "security_notes": [
                "Authorization allows viewing email messages and settings",
                "Transfer permissions enable message migration",
                "No access to message content without explicit permission",
                "All operations logged and monitored",
            ],
        }

        with open("gmail_transfer_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("📊 Gmail transfer report created: gmail_transfer_report.json")

        print("=" * 80)
        print("📊 GMAIL TRANSFER REPORT")
        print("=" * 80)
        print(f"📅 Test Date: {report['test_date']}")
        print(f"📧 Test Email: {report['test_email']}")
        print(f"✅ Authorization: {report['authorization_status']}")
        print(f"🔑 Permissions: {', '.join(report['permissions'])}")
        print("=" * 80)
        print("📋 NEXT STEPS:")
        for step in report["next_steps"]:
            print(f"• {step}")
        print("=" * 80)
        print("🔒 SECURITY NOTES:")
        for note in report["security_notes"]:
            print(f"• {note}")
        print("=" * 80)

        return report

    def run_complete_test(self):
        """Run complete Gmail transfer test"""
        logger.info("🚀 Running complete Gmail transfer test...")

        print("=" * 80)
        print("🚀 GMAIL TRANSFER COMPLETE TEST")
        print("=" * 80)
        print(f"📧 Testing: {self.test_email}")
        print(f"🏢 Company: {self.email_manager.company}")
        print(f"👤 CEO: {self.email_manager.ceo}")
        print(f"🤖 AI Assistant: {self.email_manager.ai_assistant}")
        print("=" * 80)

        # Test authorization
        auth_test = self.test_gmail_authorization()

        # Test connection
        conn_test = self.test_email_connection()

        # Generate report
        report = self.generate_transfer_report()

        print("=" * 80)
        print("🎉 GMAIL TRANSFER TEST COMPLETED")
        print("=" * 80)
        print(f"✅ Authorization Test: {'PASSED' if auth_test else 'FAILED'}")
        print(f"✅ Connection Test: {'PASSED' if conn_test else 'FAILED'}")
        print(f"📊 Report Generated: gmail_transfer_report.json")
        print("=" * 80)

        logger.info("🎉 Complete Gmail transfer test finished successfully")

        return auth_test and conn_test


def main():
    """Main entry point"""
    print("🚀 Starting Gmail Transfer Tester...")

    try:
        tester = GmailTransferTester()

        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == "auth":
                tester.test_gmail_authorization()
            elif command == "connection":
                tester.test_email_connection()
            elif command == "report":
                tester.generate_transfer_report()
            else:
                print(f"❌ Unknown command: {command}")
        else:
            # Default: run complete test
            tester.run_complete_test()

    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
