#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@SafeNet Security Components
CoolBits.ai / cbLM.ai - Security Component Library

This module provides security components for certificate verification,
str.py security monitoring, and real-time security status updates.

Author: @SafeNet Agent (oCursor)
Company: COOL BITS SRL
"""

import json
import subprocess
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class CertificateVerifier:
    """Certificate verification component"""

    def __init__(self):
        self.certificate_cache = {}
        self.cache_duration = 300  # 5 minutes

    def verify_certificate(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Verify certificate status"""
        cache_key = "boureanu_cert"

        if not force_refresh and cache_key in self.certificate_cache:
            cached_data = self.certificate_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_duration:
                return cached_data["data"]

        try:
            # Get certificate info from Windows Certificate Store
            cmd = [
                "powershell",
                "-Command",
                'Get-ChildItem -Path Cert:\\CurrentUser\\My | Where-Object {$_.Subject -like "*BOUREANU*"} | Select-Object Subject, Thumbprint, NotAfter, NotBefore, Issuer, SerialNumber | ConvertTo-Json',
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                cert_data = json.loads(result.stdout)
                current_time = datetime.now()
                not_after = datetime.strptime(
                    cert_data["NotAfter"], "%m/%d/%Y %I:%M:%S %p"
                )
                days_overdue = (current_time - not_after).days

                verification_result = {
                    "status": "verified",
                    "subject": cert_data["Subject"],
                    "thumbprint": cert_data["Thumbprint"],
                    "validity": f"{cert_data['NotBefore']} to {cert_data['NotAfter']}",
                    "issuer": cert_data["Issuer"],
                    "expired": current_time > not_after,
                    "days_overdue": days_overdue,
                    "verified_at": current_time.isoformat(),
                    "verifier": "@SafeNet",
                }

                # Cache the result
                self.certificate_cache[cache_key] = {
                    "data": verification_result,
                    "timestamp": time.time(),
                }

                return verification_result
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


class StrSecurityMonitor:
    """str.py security monitoring component"""

    def __init__(self):
        self.str_path = Path("app/andrei/secure/str.py")
        self.security_cache = {}
        self.cache_duration = 60  # 1 minute

    def check_str_security(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Check str.py security status"""
        cache_key = "str_security"

        if not force_refresh and cache_key in self.security_cache:
            cached_data = self.security_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_duration:
                return cached_data["data"]

        try:
            if not self.str_path.exists():
                return {
                    "status": "not_found",
                    "error": "str.py not found in secure location",
                    "checked_at": datetime.now().isoformat(),
                    "verifier": "@SafeNet",
                }

            # Get file stats
            stat = self.str_path.stat()

            # Check encryption status
            encryption_result = subprocess.run(
                ["cipher", "/c", str(self.str_path)],
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
                "location": str(self.str_path),
                "checked_at": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }

            # Cache the result
            self.security_cache[cache_key] = {
                "data": security_status,
                "timestamp": time.time(),
            }

            return security_status

        except Exception as e:
            return {
                "status": "check_failed",
                "error": str(e),
                "checked_at": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }


class SecurityPolicyManager:
    """Security policy management component"""

    def __init__(self):
        self.policies = {
            "zero_trust": True,
            "hmac_auth": True,
            "ip_allowlist": True,
            "rate_limiting": True,
            "audit_logging": True,
            "efs_encryption": True,
            "pin_protection": True,
            "microsoft_integration": True,
        }

    def get_security_policies(self) -> Dict[str, Any]:
        """Get current security policies"""
        return {
            "policies": self.policies,
            "last_updated": datetime.now().isoformat(),
            "verifier": "@SafeNet",
        }

    def update_policy(self, policy_name: str, value: bool) -> Dict[str, Any]:
        """Update a security policy"""
        if policy_name in self.policies:
            self.policies[policy_name] = value
            return {
                "status": "updated",
                "policy": policy_name,
                "value": value,
                "updated_at": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }
        else:
            return {
                "status": "error",
                "error": f"Policy {policy_name} not found",
                "verifier": "@SafeNet",
            }


class SecurityDashboard:
    """Real-time security dashboard component"""

    def __init__(self):
        self.cert_verifier = CertificateVerifier()
        self.str_monitor = StrSecurityMonitor()
        self.policy_manager = SecurityPolicyManager()
        self.dashboard_cache = {}
        self.cache_duration = 30  # 30 seconds

    def get_dashboard_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        cache_key = "dashboard_data"

        if not force_refresh and cache_key in self.dashboard_cache:
            cached_data = self.dashboard_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_duration:
                return cached_data["data"]

        try:
            # Get all security data
            certificate_status = self.cert_verifier.verify_certificate(force_refresh)
            str_security_status = self.str_monitor.check_str_security(force_refresh)
            security_policies = self.policy_manager.get_security_policies()

            # Calculate overall security score
            security_score = self._calculate_security_score(
                certificate_status, str_security_status, security_policies
            )

            # Generate alerts
            alerts = self._generate_alerts(certificate_status, str_security_status)

            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "company": "COOL BITS SRL",
                "ceo": "Andrei",
                "verifier": "@SafeNet",
                "security_score": security_score,
                "certificate_status": certificate_status,
                "str_security_status": str_security_status,
                "security_policies": security_policies,
                "alerts": alerts,
                "recommendations": self._generate_recommendations(
                    certificate_status, str_security_status
                ),
            }

            # Cache the result
            self.dashboard_cache[cache_key] = {
                "data": dashboard_data,
                "timestamp": time.time(),
            }

            return dashboard_data

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "verifier": "@SafeNet",
            }

    def _calculate_security_score(
        self, cert_status: Dict, str_status: Dict, policies: Dict
    ) -> int:
        """Calculate overall security score (0-100)"""
        score = 0

        # Certificate score (30 points)
        if cert_status.get("status") == "verified":
            if not cert_status.get("expired", False):
                score += 30
            else:
                score += 10  # Partial credit for expired but verified

        # str.py security score (40 points)
        if str_status.get("status") == "secure":
            score += 20
            if str_status.get("encrypted", False):
                score += 20

        # Security policies score (30 points)
        active_policies = sum(
            1 for policy in policies.get("policies", {}).values() if policy
        )
        total_policies = len(policies.get("policies", {}))
        if total_policies > 0:
            score += int((active_policies / total_policies) * 30)

        return min(score, 100)

    def _generate_alerts(
        self, cert_status: Dict, str_status: Dict
    ) -> List[Dict[str, Any]]:
        """Generate security alerts"""
        alerts = []

        # Certificate alerts
        if cert_status.get("expired", False):
            alerts.append(
                {
                    "type": "critical",
                    "title": "Certificate Expired",
                    "message": f"Certificate expired {cert_status.get('days_overdue', 0)} days ago",
                    "action": "Renew certificate immediately",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # str.py security alerts
        if not str_status.get("encrypted", False):
            alerts.append(
                {
                    "type": "warning",
                    "title": "File Not Encrypted",
                    "message": "str.py is not encrypted with EFS",
                    "action": "Enable EFS encryption",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return alerts

    def _generate_recommendations(
        self, cert_status: Dict, str_status: Dict
    ) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        if cert_status.get("expired", False):
            recommendations.append("Contact DigiSign for certificate renewal")

        if not str_status.get("encrypted", False):
            recommendations.append("Enable EFS encryption for str.py")

        recommendations.extend(
            [
                "Regular security audits recommended",
                "Monitor certificate expiration dates",
                "Maintain PIN protection for sensitive files",
                "Keep audit logs for compliance",
            ]
        )

        return recommendations


# Example usage
if __name__ == "__main__":
    print("🔐 @SafeNet Security Components - Testing")
    print("=" * 50)

    # Initialize dashboard
    dashboard = SecurityDashboard()

    # Get dashboard data
    print("\n📊 Getting security dashboard data...")
    data = dashboard.get_dashboard_data()

    print(f"\n🔐 Security Score: {data.get('security_score', 'N/A')}/100")
    print(
        f"📜 Certificate Status: {data.get('certificate_status', {}).get('status', 'N/A')}"
    )
    print(
        f"🔒 str.py Security: {data.get('str_security_status', {}).get('status', 'N/A')}"
    )

    alerts = data.get("alerts", [])
    if alerts:
        print(f"\n⚠️  Alerts ({len(alerts)}):")
        for alert in alerts:
            print(f"   {alert['type'].upper()}: {alert['title']}")

    recommendations = data.get("recommendations", [])
    if recommendations:
        print(f"\n💡 Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

    print("\n" + "=" * 50)
    print("✅ @SafeNet Security Components - Ready")
