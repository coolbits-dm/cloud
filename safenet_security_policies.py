#!/usr/bin/env python3
"""
SafeNet Security Policies and Audit System - COOL BITS SRL
Comprehensive security policies and audit trails for SafeNet operations
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityPolicyLevel(Enum):
    """Security Policy Levels for COOL BITS SRL"""

    BASIC = "basic"  # Internal documents
    STANDARD = "standard"  # Business documents
    HIGH = "high"  # Legal documents
    CRITICAL = "critical"  # Financial documents
    MAXIMUM = "maximum"  # Executive documents


class AuditEventType(Enum):
    """Audit Event Types"""

    CERTIFICATE_CREATED = "certificate_created"
    CERTIFICATE_REVOKED = "certificate_revoked"
    DOCUMENT_SIGNED = "document_signed"
    SIGNATURE_VERIFIED = "signature_verified"
    POLICY_VIOLATION = "policy_violation"
    ACCESS_DENIED = "access_denied"
    SYSTEM_ERROR = "system_error"
    COMPLIANCE_CHECK = "compliance_check"


class ComplianceStatus(Enum):
    """Compliance Status"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_ATTENTION = "requires_attention"


@dataclass
class SecurityPolicy:
    """Security Policy Definition"""

    policy_id: str
    policy_name: str
    policy_level: SecurityPolicyLevel
    description: str
    rules: List[Dict[str, Any]]
    enforcement_level: str
    effective_date: datetime
    expiry_date: Optional[datetime]
    company_registration: str = "J22/676/27.02.2020"
    company_cui: str = "42331573"


@dataclass
class AuditEvent:
    """Audit Event Record"""

    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: str
    resource_id: str
    action: str
    result: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    compliance_status: ComplianceStatus


@dataclass
class ComplianceReport:
    """Compliance Report"""

    report_id: str
    report_date: datetime
    company_name: str
    company_cui: str
    overall_status: ComplianceStatus
    policy_compliance: Dict[str, ComplianceStatus]
    audit_summary: Dict[str, Any]
    recommendations: List[str]
    next_review_date: datetime


class SafeNetSecurityPolicyManager:
    """SafeNet Security Policy Manager for COOL BITS SRL"""

    def __init__(self, company_config: Dict[str, Any]):
        self.company_name = company_config["company_name"]
        self.company_cui = company_config["cui"]
        self.company_registration = company_config["euid"]

        # Policy storage
        self.policies: Dict[str, SecurityPolicy] = {}
        self.audit_events: List[AuditEvent] = []

        # Initialize default policies
        self._initialize_default_policies()

        logger.info(
            f"SafeNet Security Policy Manager initialized for {self.company_name}"
        )

    def _initialize_default_policies(self):
        """Initialize default security policies for COOL BITS SRL"""

        # Policy 1: Certificate Management Policy
        cert_policy = SecurityPolicy(
            policy_id="CB-CERT-001",
            policy_name="Certificate Management Policy",
            policy_level=SecurityPolicyLevel.HIGH,
            description="Policy for managing digital certificates and keys",
            rules=[
                {
                    "rule_id": "CERT-001-001",
                    "description": "All certificates must be stored in secure hardware",
                    "enforcement": "mandatory",
                    "violation_action": "revoke_certificate",
                },
                {
                    "rule_id": "CERT-001-002",
                    "description": "Certificate passwords must be at least 12 characters",
                    "enforcement": "mandatory",
                    "violation_action": "reject_certificate",
                },
                {
                    "rule_id": "CERT-001-003",
                    "description": "Certificates must be renewed 30 days before expiry",
                    "enforcement": "mandatory",
                    "violation_action": "send_alert",
                },
            ],
            enforcement_level="high",
            effective_date=datetime.now(),
            expiry_date=None,
        )

        # Policy 2: Digital Signing Policy
        signing_policy = SecurityPolicy(
            policy_id="CB-SIGN-001",
            policy_name="Digital Signing Policy",
            policy_level=SecurityPolicyLevel.CRITICAL,
            description="Policy for digital document signing procedures",
            rules=[
                {
                    "rule_id": "SIGN-001-001",
                    "description": "All business documents must be digitally signed",
                    "enforcement": "mandatory",
                    "violation_action": "reject_document",
                },
                {
                    "rule_id": "SIGN-001-002",
                    "description": "Signing requires dual authentication",
                    "enforcement": "mandatory",
                    "violation_action": "deny_access",
                },
                {
                    "rule_id": "SIGN-001-003",
                    "description": "All signatures must be timestamped",
                    "enforcement": "mandatory",
                    "violation_action": "reject_signature",
                },
            ],
            enforcement_level="critical",
            effective_date=datetime.now(),
            expiry_date=None,
        )

        # Policy 3: Audit Trail Policy
        audit_policy = SecurityPolicy(
            policy_id="CB-AUDIT-001",
            policy_name="Audit Trail Policy",
            policy_level=SecurityPolicyLevel.HIGH,
            description="Policy for maintaining comprehensive audit trails",
            rules=[
                {
                    "rule_id": "AUDIT-001-001",
                    "description": "All operations must be logged with timestamps",
                    "enforcement": "mandatory",
                    "violation_action": "system_alert",
                },
                {
                    "rule_id": "AUDIT-001-002",
                    "description": "Audit logs must be retained for 7 years",
                    "enforcement": "mandatory",
                    "violation_action": "compliance_violation",
                },
                {
                    "rule_id": "AUDIT-001-003",
                    "description": "Audit logs must be tamper-proof",
                    "enforcement": "mandatory",
                    "violation_action": "security_incident",
                },
            ],
            enforcement_level="high",
            effective_date=datetime.now(),
            expiry_date=None,
        )

        # Policy 4: Access Control Policy
        access_policy = SecurityPolicy(
            policy_id="CB-ACCESS-001",
            policy_name="Access Control Policy",
            policy_level=SecurityPolicyLevel.HIGH,
            description="Policy for controlling access to SafeNet resources",
            rules=[
                {
                    "rule_id": "ACCESS-001-001",
                    "description": "Role-based access control must be implemented",
                    "enforcement": "mandatory",
                    "violation_action": "deny_access",
                },
                {
                    "rule_id": "ACCESS-001-002",
                    "description": "Multi-factor authentication required for admin access",
                    "enforcement": "mandatory",
                    "violation_action": "lock_account",
                },
                {
                    "rule_id": "ACCESS-001-003",
                    "description": "Session timeouts must be configured",
                    "enforcement": "mandatory",
                    "violation_action": "terminate_session",
                },
            ],
            enforcement_level="high",
            effective_date=datetime.now(),
            expiry_date=None,
        )

        # Store policies
        self.policies[cert_policy.policy_id] = cert_policy
        self.policies[signing_policy.policy_id] = signing_policy
        self.policies[audit_policy.policy_id] = audit_policy
        self.policies[access_policy.policy_id] = access_policy

        logger.info(f"Initialized {len(self.policies)} default security policies")

    def create_policy(self, policy: SecurityPolicy) -> bool:
        """Create new security policy"""
        try:
            self.policies[policy.policy_id] = policy

            # Log policy creation
            self._log_audit_event(
                event_type=AuditEventType.POLICY_VIOLATION,
                user_id="system",
                resource_id=policy.policy_id,
                action="create_policy",
                result="success",
                details={"policy_name": policy.policy_name},
                compliance_status=ComplianceStatus.COMPLIANT,
            )

            logger.info(f"Created policy: {policy.policy_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create policy: {e}")
            return False

    def validate_operation(
        self, operation: str, user_id: str, resource_id: str, details: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate operation against security policies"""
        violations = []

        try:
            # Check certificate management policies
            if operation in [
                "create_certificate",
                "revoke_certificate",
                "renew_certificate",
            ]:
                violations.extend(
                    self._validate_certificate_operation(operation, details)
                )

            # Check signing policies
            elif operation in ["sign_document", "verify_signature"]:
                violations.extend(self._validate_signing_operation(operation, details))

            # Check access policies
            elif operation in ["access_resource", "modify_settings"]:
                violations.extend(
                    self._validate_access_operation(operation, user_id, details)
                )

            # Log validation result
            compliance_status = (
                ComplianceStatus.COMPLIANT
                if not violations
                else ComplianceStatus.NON_COMPLIANT
            )

            self._log_audit_event(
                event_type=AuditEventType.COMPLIANCE_CHECK,
                user_id=user_id,
                resource_id=resource_id,
                action=f"validate_{operation}",
                result="success" if not violations else "violation",
                details={"violations": violations, "operation": operation},
                compliance_status=compliance_status,
            )

            return len(violations) == 0, violations

        except Exception as e:
            logger.error(f"Failed to validate operation: {e}")
            return False, [f"Validation error: {str(e)}"]

    def _validate_certificate_operation(
        self, operation: str, details: Dict[str, Any]
    ) -> List[str]:
        """Validate certificate operations against policies"""
        violations = []

        # Check certificate management policy
        cert_policy = self.policies.get("CB-CERT-001")
        if not cert_policy:
            return ["Certificate management policy not found"]

        for rule in cert_policy.rules:
            if rule["rule_id"] == "CERT-001-001":
                # Check if certificate is stored securely
                if not details.get("secure_storage", False):
                    violations.append("Certificate must be stored in secure hardware")

            elif rule["rule_id"] == "CERT-001-002":
                # Check password strength
                password = details.get("password", "")
                if len(password) < 12:
                    violations.append(
                        "Certificate password must be at least 12 characters"
                    )

            elif rule["rule_id"] == "CERT-001-003":
                # Check renewal timing
                expiry_date = details.get("expiry_date")
                if expiry_date:
                    days_until_expiry = (expiry_date - datetime.now()).days
                    if days_until_expiry < 30:
                        violations.append(
                            "Certificate must be renewed 30 days before expiry"
                        )

        return violations

    def _validate_signing_operation(
        self, operation: str, details: Dict[str, Any]
    ) -> List[str]:
        """Validate signing operations against policies"""
        violations = []

        # Check digital signing policy
        signing_policy = self.policies.get("CB-SIGN-001")
        if not signing_policy:
            return ["Digital signing policy not found"]

        for rule in signing_policy.rules:
            if rule["rule_id"] == "SIGN-001-001":
                # Check if document is signed
                if not details.get("is_signed", False):
                    violations.append("All business documents must be digitally signed")

            elif rule["rule_id"] == "SIGN-001-002":
                # Check dual authentication
                if not details.get("dual_auth", False):
                    violations.append("Signing requires dual authentication")

            elif rule["rule_id"] == "SIGN-001-003":
                # Check timestamping
                if not details.get("timestamped", False):
                    violations.append("All signatures must be timestamped")

        return violations

    def _validate_access_operation(
        self, operation: str, user_id: str, details: Dict[str, Any]
    ) -> List[str]:
        """Validate access operations against policies"""
        violations = []

        # Check access control policy
        access_policy = self.policies.get("CB-ACCESS-001")
        if not access_policy:
            return ["Access control policy not found"]

        for rule in access_policy.rules:
            if rule["rule_id"] == "ACCESS-001-001":
                # Check role-based access
                if not details.get("role_based_access", False):
                    violations.append("Role-based access control must be implemented")

            elif rule["rule_id"] == "ACCESS-001-002":
                # Check multi-factor authentication
                if not details.get("mfa_enabled", False):
                    violations.append(
                        "Multi-factor authentication required for admin access"
                    )

            elif rule["rule_id"] == "ACCESS-001-003":
                # Check session timeout
                if not details.get("session_timeout", False):
                    violations.append("Session timeouts must be configured")

        return violations

    def _log_audit_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        resource_id: str,
        action: str,
        result: str,
        details: Dict[str, Any],
        compliance_status: ComplianceStatus,
        ip_address: str = "127.0.0.1",
        user_agent: str = "SafeNet-System",
    ):
        """Log audit event"""
        event = AuditEvent(
            event_id=f"audit-{int(datetime.now().timestamp())}",
            event_type=event_type,
            timestamp=datetime.now(),
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            result=result,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            compliance_status=compliance_status,
        )

        self.audit_events.append(event)

        # Log to file
        self._save_audit_event(event)

        logger.info(f"Audit event logged: {event.event_id} - {event.action}")

    def _save_audit_event(self, event: AuditEvent):
        """Save audit event to file"""
        try:
            audit_file = "safenet_audit_log.json"

            # Load existing audit data
            if os.path.exists(audit_file):
                with open(audit_file, "r") as f:
                    audit_data = json.load(f)
            else:
                audit_data = []

            # Add new event
            audit_data.append(asdict(event))

            # Save updated audit data
            with open(audit_file, "w") as f:
                json.dump(audit_data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save audit event: {e}")

    def generate_compliance_report(self) -> ComplianceReport:
        """Generate comprehensive compliance report"""
        try:
            # Calculate overall compliance status
            total_events = len(self.audit_events)
            compliant_events = sum(
                1
                for event in self.audit_events
                if event.compliance_status == ComplianceStatus.COMPLIANT
            )

            overall_status = ComplianceStatus.COMPLIANT
            if total_events > 0:
                compliance_rate = compliant_events / total_events
                if compliance_rate < 0.95:
                    overall_status = ComplianceStatus.NON_COMPLIANT
                elif compliance_rate < 0.98:
                    overall_status = ComplianceStatus.REQUIRES_ATTENTION

            # Policy compliance status
            policy_compliance = {}
            for policy_id, policy in self.policies.items():
                policy_compliance[policy_id] = ComplianceStatus.COMPLIANT

            # Audit summary
            audit_summary = {
                "total_events": total_events,
                "compliant_events": compliant_events,
                "non_compliant_events": total_events - compliant_events,
                "compliance_rate": (
                    compliant_events / total_events if total_events > 0 else 1.0
                ),
                "last_audit": (
                    max(event.timestamp for event in self.audit_events).isoformat()
                    if self.audit_events
                    else None
                ),
            }

            # Generate recommendations
            recommendations = []
            if overall_status != ComplianceStatus.COMPLIANT:
                recommendations.append("Review and address policy violations")
                recommendations.append("Implement additional security controls")
                recommendations.append("Conduct security awareness training")

            recommendations.append("Schedule regular compliance reviews")
            recommendations.append("Update security policies as needed")

            report = ComplianceReport(
                report_id=f"compliance-{int(datetime.now().timestamp())}",
                report_date=datetime.now(),
                company_name=self.company_name,
                company_cui=self.company_cui,
                overall_status=overall_status,
                policy_compliance=policy_compliance,
                audit_summary=audit_summary,
                recommendations=recommendations,
                next_review_date=datetime.now() + timedelta(days=30),
            )

            return report

        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise

    def get_audit_trail(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[AuditEvent]:
        """Get audit trail for specified date range"""
        try:
            filtered_events = self.audit_events

            if start_date:
                filtered_events = [
                    e for e in filtered_events if e.timestamp >= start_date
                ]

            if end_date:
                filtered_events = [
                    e for e in filtered_events if e.timestamp <= end_date
                ]

            return filtered_events

        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            return []

    def export_compliance_data(self, output_file: str) -> bool:
        """Export compliance data to file"""
        try:
            compliance_data = {
                "company_info": {
                    "name": self.company_name,
                    "cui": self.company_cui,
                    "registration": self.company_registration,
                },
                "policies": {
                    pid: asdict(policy) for pid, policy in self.policies.items()
                },
                "audit_events": [asdict(event) for event in self.audit_events],
                "compliance_report": asdict(self.generate_compliance_report()),
                "export_timestamp": datetime.now().isoformat(),
            }

            with open(output_file, "w") as f:
                json.dump(compliance_data, f, indent=2, default=str)

            logger.info(f"Compliance data exported to: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to export compliance data: {e}")
            return False


def main():
    """Main function to demonstrate SafeNet security policies"""

    # Load company configuration
    with open("coolbits_srl_complete_details.json", "r") as f:
        company_config = json.load(f)

    # Initialize Security Policy Manager
    policy_manager = SafeNetSecurityPolicyManager(company_config)

    print("🔐 SafeNet Security Policy Manager")
    print("=" * 50)
    print(f"Company: {policy_manager.company_name}")
    print(f"CUI: {policy_manager.company_cui}")
    print(f"Registration: {policy_manager.company_registration}")

    # Display policies
    print(f"\n📋 Security Policies ({len(policy_manager.policies)}):")
    for policy_id, policy in policy_manager.policies.items():
        print(f"  {policy_id}: {policy.policy_name}")
        print(f"    Level: {policy.policy_level.value}")
        print(f"    Rules: {len(policy.rules)}")

    # Test policy validation
    print(f"\n🔍 Testing Policy Validation:")

    # Test certificate operation
    cert_details = {
        "secure_storage": True,
        "password": "SecurePassword123",
        "expiry_date": datetime.now() + timedelta(days=60),
    }

    is_valid, violations = policy_manager.validate_operation(
        "create_certificate", "test_user", "cert_001", cert_details
    )

    print(f"  Certificate Creation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if violations:
        for violation in violations:
            print(f"    - {violation}")

    # Test signing operation
    signing_details = {"is_signed": True, "dual_auth": True, "timestamped": True}

    is_valid, violations = policy_manager.validate_operation(
        "sign_document", "test_user", "doc_001", signing_details
    )

    print(f"  Document Signing: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if violations:
        for violation in violations:
            print(f"    - {violation}")

    # Generate compliance report
    print(f"\n📊 Compliance Report:")
    compliance_report = policy_manager.generate_compliance_report()
    print(f"  Overall Status: {compliance_report.overall_status.value}")
    print(f"  Total Events: {compliance_report.audit_summary['total_events']}")
    print(
        f"  Compliance Rate: {compliance_report.audit_summary['compliance_rate']:.2%}"
    )
    print(f"  Next Review: {compliance_report.next_review_date.strftime('%Y-%m-%d')}")

    # Export compliance data
    export_file = "safenet_compliance_export.json"
    if policy_manager.export_compliance_data(export_file):
        print(f"\n💾 Compliance data exported to: {export_file}")


if __name__ == "__main__":
    main()
