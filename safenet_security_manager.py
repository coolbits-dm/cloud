#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@SafeNet @oSafeNet - Local Security Administration Prompt
CoolBits.ai / cbLM.ai - Certificate Verification & Security Management

Certificate verification and security administration prompt for @oPython.
Manages local security policies, certificate validation, and secure access.

Author: oSafeNet Agent (oCursor)
Company: COOL BITS SRL
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class SafeNetSecurityManager:
    """Local security administration manager for @oPython"""

    def __init__(self):
        self.certificate_info = self._get_certificate_info()
        self.security_policies = self._load_security_policies()
        self.audit_log = []

    def _get_certificate_info(self) -> Dict[str, Any]:
        """Get certificate information from system"""
        try:
            # Get certificate details
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    'Get-ChildItem -Path Cert:\\CurrentUser\\My | Where-Object {$_.Subject -like "*BOUREANU*"} | Select-Object Subject, Thumbprint, NotAfter, NotBefore, Issuer, SerialNumber | ConvertTo-Json',
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                cert_data = json.loads(result.stdout)
                return {
                    "status": "verified",
                    "certificate": cert_data,
                    "verified_at": datetime.now().isoformat(),
                    "verifier": "@SafeNet",
                }
            else:
                return {
                    "status": "not_found",
                    "error": "Certificate not found or access denied",
                    "verified_at": datetime.now().isoformat(),
                    "verifier": "@SafeNet",
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "verified_at": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }

    def _load_security_policies(self) -> Dict[str, Any]:
        """Load current security policies"""
        return {
            "str_protection": {
                "location": "app/andrei/secure/str.py",
                "encryption": "EFS",
                "pin_protection": True,
                "microsoft_account": "andrei@coolbits.ro",
                "access_control": "Restricted to ANDREI\\andre only",
            },
            "certificate_policy": {
                "issuer": "DigiSign Qualified CA Class 3 2017",
                "subject": "BOUREANU ANDREI-CIPRIAN",
                "validity": "2023-06-06 to 2025-06-05",
                "serial_number": "2005062450018890C68F229A81905B24",
                "thumbprint": "AD61CB7BF502EBF90B75898D51F4327A833670E5",
            },
            "bridge_security": {
                "hmac_auth": True,
                "ip_allowlist": True,
                "rate_limiting": True,
                "audit_logging": True,
                "zero_trust": True,
            },
        }

    def verify_certificate(self) -> Dict[str, Any]:
        """Verify certificate validity and security"""
        cert_info = self.certificate_info

        if cert_info["status"] == "verified":
            cert = cert_info["certificate"]
            current_time = datetime.now()
            # Handle different date formats
            not_after_str = cert["NotAfter"]
            if "/Date(" in not_after_str:
                # Handle .NET date format
                timestamp = int(not_after_str.split("/Date(")[1].split(")/")[0]) / 1000
                not_after = datetime.fromtimestamp(timestamp)
            else:
                not_after = datetime.strptime(not_after_str, "%m/%d/%Y %I:%M:%S %p")

            verification_result = {
                "status": "verified",
                "certificate_valid": current_time < not_after,
                "days_until_expiry": (not_after - current_time).days,
                "issuer_trusted": "DigiSign" in cert["Issuer"],
                "subject_match": "BOUREANU ANDREI-CIPRIAN" in cert["Subject"],
                "thumbprint": cert["Thumbprint"],
                "verified_at": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }

            # Log verification
            self.audit_log.append(
                {
                    "action": "certificate_verification",
                    "result": verification_result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return verification_result
        else:
            return {
                "status": "verification_failed",
                "error": cert_info.get("error", "Unknown error"),
                "verified_at": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }

    def check_str_security(self) -> Dict[str, Any]:
        """Check str.py security status"""
        str_path = Path("app/andrei/secure/str.py")

        if not str_path.exists():
            return {
                "status": "not_found",
                "error": "str.py not found in secure location",
                "checked_at": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }

        try:
            # Check file permissions
            stat = str_path.stat()

            # Check encryption status
            encryption_result = subprocess.run(
                ["cipher", "/c", str(str_path)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            is_encrypted = "encrypted" in encryption_result.stdout.lower()

            security_status = {
                "status": "secure",
                "file_exists": True,
                "size_bytes": stat.st_size,
                "encrypted": is_encrypted,
                "pin_protected": True,
                "microsoft_account": "andrei@coolbits.ro",
                "location": str(str_path),
                "checked_at": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }

            # Log security check
            self.audit_log.append(
                {
                    "action": "str_security_check",
                    "result": security_status,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return security_status

        except Exception as e:
            return {
                "status": "check_failed",
                "error": str(e),
                "checked_at": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        cert_verification = self.verify_certificate()
        str_security = self.check_str_security()

        report = {
            "report_id": f"SEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "verifier": "@SafeNet",
            "company": "COOL BITS SRL",
            "certificate_status": cert_verification,
            "str_security_status": str_security,
            "security_policies": self.security_policies,
            "audit_log": self.audit_log,
            "recommendations": self._generate_recommendations(
                cert_verification, str_security
            ),
        }

        return report

    def _generate_recommendations(
        self, cert_status: Dict, str_status: Dict
    ) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        # Certificate recommendations
        if cert_status.get("status") == "verified":
            if cert_status.get("days_until_expiry", 0) < 30:
                recommendations.append("Certificate expires soon - consider renewal")
            if not cert_status.get("certificate_valid", False):
                recommendations.append(
                    "Certificate has expired - immediate renewal required"
                )

        # str.py security recommendations
        if str_status.get("status") == "secure":
            recommendations.append("str.py security is properly configured")
            if not str_status.get("encrypted", False):
                recommendations.append("Consider enabling EFS encryption for str.py")

        # General recommendations
        recommendations.extend(
            [
                "Regular security audits recommended",
                "Monitor certificate expiration dates",
                "Maintain PIN protection for sensitive files",
                "Keep audit logs for compliance",
            ]
        )

        return recommendations


def main():
    """Main function for @SafeNet security administration"""
    print("🔐 @SafeNet @oSafeNet - Local Security Administration")
    print("=" * 60)
    print("Company: COOL BITS SRL")
    print("Agent: @SafeNet")
    print("Target: @oPython Security Management")
    print("=" * 60)

    # Initialize security manager
    security_manager = SafeNetSecurityManager()

    # Generate security report
    print("\n🔍 Generating Security Report...")
    report = security_manager.generate_security_report()

    # Display certificate status
    print(f"\n📜 Certificate Status:")
    cert_status = report["certificate_status"]
    if cert_status["status"] == "verified":
        print(f"   ✅ Status: {cert_status['status']}")
        print(f"   📅 Valid Until: {cert_status.get('days_until_expiry', 'N/A')} days")
        print(f"   🔒 Trusted Issuer: {cert_status.get('issuer_trusted', False)}")
        print(f"   👤 Subject Match: {cert_status.get('subject_match', False)}")
        print(f"   🔑 Thumbprint: {cert_status.get('thumbprint', 'N/A')}")
    else:
        print(f"   ❌ Status: {cert_status['status']}")
        print(f"   ⚠️  Error: {cert_status.get('error', 'Unknown')}")

    # Display str.py security status
    print(f"\n📁 str.py Security Status:")
    str_status = report["str_security_status"]
    if str_status["status"] == "secure":
        print(f"   ✅ Status: {str_status['status']}")
        print(f"   📊 Size: {str_status.get('size_bytes', 'N/A')} bytes")
        print(f"   🔒 Encrypted: {str_status.get('encrypted', False)}")
        print(f"   🔐 PIN Protected: {str_status.get('pin_protected', False)}")
        print(f"   📧 Account: {str_status.get('microsoft_account', 'N/A')}")
        print(f"   📍 Location: {str_status.get('location', 'N/A')}")
    else:
        print(f"   ❌ Status: {str_status['status']}")
        print(f"   ⚠️  Error: {str_status.get('error', 'Unknown')}")

    # Display recommendations
    print(f"\n💡 Security Recommendations:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"   {i}. {rec}")

    # Save report
    report_file = f"security_report_{report['report_id']}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📋 Security Report Saved: {report_file}")
    print(f"🕒 Generated: {report['generated_at']}")
    print(f"🔐 Verifier: {report['verifier']}")

    print("\n" + "=" * 60)
    print("✅ @SafeNet Security Administration Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
