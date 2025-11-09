#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Health Endpoint - CoolBits.ai
Provides real-time policy enforcement status for fail-closed mode
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from cblm.opipe.nha.enforcer import PolicyEnforcer
    from cblm.opipe.nha.registry import load_yaml
except ImportError:
    # Fallback for development
    PolicyEnforcer = None
    load_yaml = None


class PolicyHealthChecker:
    def __init__(self):
        self.enforcement_mode = os.getenv("NHA_ENFORCEMENT_MODE", "fail-closed")
        self.registry_path = "cblm/opipe/nha/agents.yaml"
        self.enforcer = None
        self.last_check = None
        self.health_status = "unknown"

    def load_enforcer(self) -> bool:
        """Load the policy enforcer"""
        try:
            if PolicyEnforcer and load_yaml:
                registry = load_yaml(self.registry_path)
                self.enforcer = PolicyEnforcer(registry)
                return True
            return False
        except Exception as e:
            print(f"Failed to load enforcer: {e}")
            return False

    def check_registry_integrity(self) -> Dict[str, Any]:
        """Check NHA registry integrity"""
        try:
            if not os.path.exists(self.registry_path):
                return {
                    "status": "error",
                    "message": "Registry file not found",
                    "critical": True,
                }

            # Check file size and modification time
            stat = os.stat(self.registry_path)
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

            # Check if registry is too old (stale)
            now = datetime.now(timezone.utc)
            age_hours = (now - mtime).total_seconds() / 3600

            if age_hours > 24:
                return {
                    "status": "warning",
                    "message": f"Registry is {age_hours:.1f} hours old",
                    "critical": False,
                    "age_hours": age_hours,
                }

            return {
                "status": "ok",
                "message": "Registry integrity verified",
                "critical": False,
                "size_bytes": size,
                "last_modified": mtime.isoformat(),
                "age_hours": age_hours,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Registry check failed: {e}",
                "critical": True,
            }

    def check_enforcement_mode(self) -> Dict[str, Any]:
        """Check enforcement mode configuration"""
        expected_mode = "fail-closed"
        current_mode = self.enforcement_mode

        if current_mode == expected_mode:
            return {
                "status": "ok",
                "message": f"Enforcement mode correct: {current_mode}",
                "critical": False,
                "mode": current_mode,
            }
        else:
            return {
                "status": "error",
                "message": f"Enforcement mode incorrect: {current_mode} (expected: {expected_mode})",
                "critical": True,
                "mode": current_mode,
                "expected_mode": expected_mode,
            }

    def check_audit_logging(self) -> Dict[str, Any]:
        """Check audit logging functionality"""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return {
                    "status": "warning",
                    "message": "Audit logs directory not found",
                    "critical": False,
                }

            # Check for recent audit files
            audit_files = list(logs_dir.glob("policy-enforcement-*.jsonl"))
            if not audit_files:
                return {
                    "status": "warning",
                    "message": "No audit log files found",
                    "critical": False,
                }

            # Check latest audit file
            latest_file = max(audit_files, key=lambda f: f.stat().st_mtime)
            stat = latest_file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600

            return {
                "status": "ok",
                "message": "Audit logging functional",
                "critical": False,
                "latest_file": latest_file.name,
                "age_hours": age_hours,
                "file_count": len(audit_files),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Audit logging check failed: {e}",
                "critical": True,
            }

    def check_proof_pack_status(self) -> Dict[str, Any]:
        """Check Proof Pack status"""
        try:
            proof_pack_path = Path("proof_pack.zip")
            if not proof_pack_path.exists():
                return {
                    "status": "warning",
                    "message": "Proof Pack not found",
                    "critical": False,
                }

            stat = proof_pack_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600

            if age_hours > 24:
                return {
                    "status": "error",
                    "message": f"Proof Pack is stale: {age_hours:.1f} hours old",
                    "critical": True,
                    "age_hours": age_hours,
                }

            return {
                "status": "ok",
                "message": "Proof Pack is current",
                "critical": False,
                "age_hours": age_hours,
                "size_bytes": stat.st_size,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Proof Pack check failed: {e}",
                "critical": True,
            }

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        self.last_check = datetime.now(timezone.utc)

        checks = {
            "registry_integrity": self.check_registry_integrity(),
            "enforcement_mode": self.check_enforcement_mode(),
            "audit_logging": self.check_audit_logging(),
            "proof_pack_status": self.check_proof_pack_status(),
        }

        # Determine overall health
        critical_issues = [
            check for check in checks.values() if check.get("critical", False)
        ]
        warnings = [check for check in checks.values() if check["status"] == "warning"]

        if critical_issues:
            self.health_status = "critical"
            overall_status = "CRITICAL"
        elif warnings:
            self.health_status = "warning"
            overall_status = "WARNING"
        else:
            self.health_status = "healthy"
            overall_status = "HEALTHY"

        return {
            "timestamp": self.last_check.isoformat(),
            "overall_status": overall_status,
            "enforcement_mode": self.enforcement_mode,
            "checks": checks,
            "summary": {
                "total_checks": len(checks),
                "critical_issues": len(critical_issues),
                "warnings": len(warnings),
                "healthy": len([c for c in checks.values() if c["status"] == "ok"]),
            },
        }


def main():
    """Main function for CLI usage"""
    checker = PolicyHealthChecker()
    health = checker.get_health_status()

    print("Policy Health Status:")
    print("=" * 50)
    print(f"Overall Status: {health['overall_status']}")
    print(f"Enforcement Mode: {health['enforcement_mode']}")
    print(f"Timestamp: {health['timestamp']}")
    print()

    for check_name, check_result in health["checks"].items():
        status = check_result["status"].upper()
        message = check_result["message"]
        critical = " (CRITICAL)" if check_result.get("critical", False) else ""
        print(f"{check_name}: {status}{critical}")
        print(f"  {message}")
        print()

    summary = health["summary"]
    print("Summary:")
    print(f"  Total Checks: {summary['total_checks']}")
    print(f"  Critical Issues: {summary['critical_issues']}")
    print(f"  Warnings: {summary['warnings']}")
    print(f"  Healthy: {summary['healthy']}")

    # Exit with appropriate code
    if health["overall_status"] == "CRITICAL":
        sys.exit(1)
    elif health["overall_status"] == "WARNING":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
