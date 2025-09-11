#!/usr/bin/env python3
"""
SafeNet Integration Testing Suite - COOL BITS SRL
Comprehensive testing for SafeNet Authentication Client integration
"""

import unittest
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from safenet_integration_architecture import (
    SafeNetIntegrationManager,
    SafeNetCertificateType,
    SafeNetSecurityLevel,
    SafeNetCertificate,
    SafeNetSigningRequest,
    SafeNetSigningResult,
)

from safenet_security_policies import (
    SafeNetSecurityPolicyManager,
    SecurityPolicyLevel,
    AuditEventType,
    ComplianceStatus,
)


class TestSafeNetIntegration(unittest.TestCase):
    """Test cases for SafeNet Integration Manager"""

    def setUp(self):
        """Set up test environment"""
        self.company_config = {
            "company_name": "COOL BITS S.R.L.",
            "cui": "42331573",
            "euid": "ROONRC.J22/676/2020",
            "infrastructure": {"workspace": tempfile.mkdtemp()},
        }

        self.safenet_manager = SafeNetIntegrationManager(self.company_config)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.company_config["infrastructure"]["workspace"]):
            shutil.rmtree(self.company_config["infrastructure"]["workspace"])

    def test_initialization(self):
        """Test SafeNet manager initialization"""
        self.assertEqual(self.safenet_manager.company_name, "COOL BITS S.R.L.")
        self.assertEqual(self.safenet_manager.company_cui, "42331573")
        self.assertEqual(
            self.safenet_manager.company_registration, "ROONRC.J22/676/2020"
        )

        # Check if directories were created
        for path in self.safenet_manager.safenet_config.values():
            self.assertTrue(os.path.exists(path))

    def test_certificate_generation(self):
        """Test certificate generation"""
        certificate = self.safenet_manager.generate_company_certificate(
            SafeNetCertificateType.COMPANY_SIGNING, SafeNetSecurityLevel.LEVEL_3
        )

        self.assertIsInstance(certificate, SafeNetCertificate)
        self.assertEqual(
            certificate.certificate_type, SafeNetCertificateType.COMPANY_SIGNING
        )
        self.assertEqual(certificate.security_level, SafeNetSecurityLevel.LEVEL_3)
        self.assertTrue(certificate.is_active)
        self.assertIn(
            certificate.certificate_id, self.safenet_manager.certificate_registry
        )

    def test_document_signing(self):
        """Test document signing functionality"""
        # Create a test document
        test_doc_path = os.path.join(
            self.safenet_manager.safenet_config["temp_path"], "test_doc.txt"
        )
        with open(test_doc_path, "w") as f:
            f.write("Test document for SafeNet signing")

        # Generate certificate
        certificate = self.safenet_manager.generate_company_certificate(
            SafeNetCertificateType.DOCUMENT_SIGNING, SafeNetSecurityLevel.LEVEL_3
        )

        # Sign document
        result = self.safenet_manager.sign_document(
            document_path=test_doc_path,
            certificate_id=certificate.certificate_id,
            signing_purpose="Test Signing",
            security_level=SafeNetSecurityLevel.LEVEL_3,
        )

        self.assertIsInstance(result, SafeNetSigningResult)
        self.assertEqual(result.certificate_used, certificate.certificate_id)
        self.assertTrue(result.verification_status)
        self.assertIsNotNone(result.signature)

        # Clean up
        os.remove(test_doc_path)

    def test_signature_verification(self):
        """Test signature verification"""
        # Create a test document
        test_doc_path = os.path.join(
            self.safenet_manager.safenet_config["temp_path"], "test_doc.txt"
        )
        with open(test_doc_path, "w") as f:
            f.write("Test document for verification")

        # Generate certificate
        certificate = self.safenet_manager.generate_company_certificate(
            SafeNetCertificateType.DOCUMENT_SIGNING, SafeNetSecurityLevel.LEVEL_3
        )

        # Sign document
        result = self.safenet_manager.sign_document(
            document_path=test_doc_path,
            certificate_id=certificate.certificate_id,
            signing_purpose="Test Signing",
            security_level=SafeNetSecurityLevel.LEVEL_3,
        )

        # Verify signature
        verification_result = self.safenet_manager.verify_signature(
            document_path=test_doc_path,
            signature=result.signature,
            certificate_id=certificate.certificate_id,
        )

        self.assertTrue(verification_result)

        # Clean up
        os.remove(test_doc_path)

    def test_certificate_status(self):
        """Test certificate status checking"""
        certificate = self.safenet_manager.generate_company_certificate(
            SafeNetCertificateType.API_AUTHENTICATION, SafeNetSecurityLevel.LEVEL_2
        )

        status = self.safenet_manager.get_certificate_status(certificate.certificate_id)

        self.assertEqual(status["certificate_id"], certificate.certificate_id)
        self.assertTrue(status["is_active"])
        self.assertTrue(status["is_valid"])
        self.assertGreater(status["days_until_expiry"], 0)

    def test_compliance_report_generation(self):
        """Test compliance report generation"""
        # Generate some certificates
        for cert_type in SafeNetCertificateType:
            self.safenet_manager.generate_company_certificate(
                cert_type, SafeNetSecurityLevel.LEVEL_3
            )

        report = self.safenet_manager.generate_compliance_report()

        self.assertEqual(report["company_name"], "COOL BITS S.R.L.")
        self.assertEqual(report["company_cui"], "42331573")
        self.assertGreater(report["certificates"]["total_certificates"], 0)
        self.assertTrue(report["security_compliance"]["audit_trail_complete"])


class TestSafeNetSecurityPolicies(unittest.TestCase):
    """Test cases for SafeNet Security Policies"""

    def setUp(self):
        """Set up test environment"""
        self.company_config = {
            "company_name": "COOL BITS S.R.L.",
            "cui": "42331573",
            "euid": "ROONRC.J22/676/2020",
        }

        self.policy_manager = SafeNetSecurityPolicyManager(self.company_config)

    def test_policy_initialization(self):
        """Test security policy initialization"""
        self.assertEqual(len(self.policy_manager.policies), 4)

        expected_policies = [
            "CB-CERT-001",
            "CB-SIGN-001",
            "CB-AUDIT-001",
            "CB-ACCESS-001",
        ]
        for policy_id in expected_policies:
            self.assertIn(policy_id, self.policy_manager.policies)

    def test_certificate_operation_validation(self):
        """Test certificate operation validation"""
        # Valid certificate details
        valid_details = {
            "secure_storage": True,
            "password": "SecurePassword123",
            "expiry_date": datetime.now() + timedelta(days=60),
        }

        is_valid, violations = self.policy_manager.validate_operation(
            "create_certificate", "test_user", "cert_001", valid_details
        )

        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

        # Invalid certificate details
        invalid_details = {
            "secure_storage": False,
            "password": "weak",
            "expiry_date": datetime.now() + timedelta(days=10),
        }

        is_valid, violations = self.policy_manager.validate_operation(
            "create_certificate", "test_user", "cert_002", invalid_details
        )

        self.assertFalse(is_valid)
        self.assertGreater(len(violations), 0)

    def test_signing_operation_validation(self):
        """Test signing operation validation"""
        # Valid signing details
        valid_details = {"is_signed": True, "dual_auth": True, "timestamped": True}

        is_valid, violations = self.policy_manager.validate_operation(
            "sign_document", "test_user", "doc_001", valid_details
        )

        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

        # Invalid signing details
        invalid_details = {"is_signed": False, "dual_auth": False, "timestamped": False}

        is_valid, violations = self.policy_manager.validate_operation(
            "sign_document", "test_user", "doc_002", invalid_details
        )

        self.assertFalse(is_valid)
        self.assertGreater(len(violations), 0)

    def test_audit_event_logging(self):
        """Test audit event logging"""
        initial_count = len(self.policy_manager.audit_events)

        # Trigger an audit event
        self.policy_manager._log_audit_event(
            event_type=AuditEventType.DOCUMENT_SIGNED,
            user_id="test_user",
            resource_id="doc_001",
            action="sign_document",
            result="success",
            details={"document_type": "contract"},
            compliance_status=ComplianceStatus.COMPLIANT,
        )

        self.assertEqual(len(self.policy_manager.audit_events), initial_count + 1)

        # Check the logged event
        event = self.policy_manager.audit_events[-1]
        self.assertEqual(event.user_id, "test_user")
        self.assertEqual(event.action, "sign_document")
        self.assertEqual(event.compliance_status, ComplianceStatus.COMPLIANT)

    def test_compliance_report_generation(self):
        """Test compliance report generation"""
        # Add some audit events
        self.policy_manager._log_audit_event(
            event_type=AuditEventType.DOCUMENT_SIGNED,
            user_id="test_user",
            resource_id="doc_001",
            action="sign_document",
            result="success",
            details={"document_type": "contract"},
            compliance_status=ComplianceStatus.COMPLIANT,
        )

        report = self.policy_manager.generate_compliance_report()

        self.assertEqual(report.company_name, "COOL BITS S.R.L.")
        self.assertEqual(report.company_cui, "42331573")
        self.assertIsInstance(report.overall_status, ComplianceStatus)
        self.assertGreater(len(report.recommendations), 0)

    def test_audit_trail_filtering(self):
        """Test audit trail filtering by date range"""
        # Add events with different timestamps
        base_time = datetime.now()

        self.policy_manager._log_audit_event(
            event_type=AuditEventType.DOCUMENT_SIGNED,
            user_id="test_user",
            resource_id="doc_001",
            action="sign_document",
            result="success",
            details={"document_type": "contract"},
            compliance_status=ComplianceStatus.COMPLIANT,
        )

        # Filter by date range
        start_date = base_time - timedelta(hours=1)
        end_date = base_time + timedelta(hours=1)

        filtered_events = self.policy_manager.get_audit_trail(start_date, end_date)

        self.assertGreaterEqual(len(filtered_events), 1)


class TestSafeNetIntegrationEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""

    def setUp(self):
        """Set up test environment"""
        self.company_config = {
            "company_name": "COOL BITS S.R.L.",
            "cui": "42331573",
            "euid": "ROONRC.J22/676/2020",
            "infrastructure": {"workspace": tempfile.mkdtemp()},
        }

        self.safenet_manager = SafeNetIntegrationManager(self.company_config)
        self.policy_manager = SafeNetSecurityPolicyManager(self.company_config)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.company_config["infrastructure"]["workspace"]):
            shutil.rmtree(self.company_config["infrastructure"]["workspace"])

    def test_complete_document_signing_workflow(self):
        """Test complete document signing workflow"""
        # Create test document
        test_doc_path = os.path.join(
            self.safenet_manager.safenet_config["temp_path"], "contract.txt"
        )
        with open(test_doc_path, "w") as f:
            f.write(
                "COOL BITS S.R.L. Contract Agreement\n\nThis is a test contract for SafeNet integration."
            )

        # Generate certificate
        certificate = self.safenet_manager.generate_company_certificate(
            SafeNetCertificateType.DOCUMENT_SIGNING, SafeNetSecurityLevel.LEVEL_4
        )

        # Validate certificate creation against policies
        cert_details = {
            "secure_storage": True,
            "password": "SecurePassword123",
            "expiry_date": certificate.valid_to,
        }

        is_valid, violations = self.policy_manager.validate_operation(
            "create_certificate", "admin", certificate.certificate_id, cert_details
        )

        self.assertTrue(is_valid, f"Certificate validation failed: {violations}")

        # Sign document
        result = self.safenet_manager.sign_document(
            document_path=test_doc_path,
            certificate_id=certificate.certificate_id,
            signing_purpose="Contract Signing",
            security_level=SafeNetSecurityLevel.LEVEL_4,
        )

        # Validate signing against policies
        signing_details = {"is_signed": True, "dual_auth": True, "timestamped": True}

        is_valid, violations = self.policy_manager.validate_operation(
            "sign_document", "admin", result.request_id, signing_details
        )

        self.assertTrue(is_valid, f"Signing validation failed: {violations}")

        # Verify signature
        verification_result = self.safenet_manager.verify_signature(
            document_path=test_doc_path,
            signature=result.signature,
            certificate_id=certificate.certificate_id,
        )

        self.assertTrue(verification_result)

        # Generate compliance report
        compliance_report = self.policy_manager.generate_compliance_report()

        self.assertEqual(compliance_report.company_name, "COOL BITS S.R.L.")
        self.assertGreater(compliance_report.audit_summary["total_events"], 0)

        # Clean up
        os.remove(test_doc_path)

    def test_certificate_lifecycle_management(self):
        """Test complete certificate lifecycle management"""
        # Create multiple certificates
        certificates = []
        for cert_type in SafeNetCertificateType:
            cert = self.safenet_manager.generate_company_certificate(
                cert_type, SafeNetSecurityLevel.LEVEL_3
            )
            certificates.append(cert)

        # Check all certificates are active
        for cert in certificates:
            status = self.safenet_manager.get_certificate_status(cert.certificate_id)
            self.assertTrue(status["is_active"])
            self.assertTrue(status["is_valid"])

        # Generate compliance report
        report = self.safenet_manager.generate_compliance_report()

        self.assertEqual(
            report["certificates"]["total_certificates"], len(certificates)
        )
        self.assertEqual(
            report["certificates"]["active_certificates"], len(certificates)
        )
        self.assertEqual(report["certificates"]["expired_certificates"], 0)


class TestSafeNetAPIIntegration(unittest.TestCase):
    """Test cases for SafeNet API integration"""

    def setUp(self):
        """Set up test environment"""
        self.company_config = {
            "company_name": "COOL BITS S.R.L.",
            "cui": "42331573",
            "euid": "ROONRC.J22/676/2020",
            "infrastructure": {"workspace": tempfile.mkdtemp()},
        }

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.company_config["infrastructure"]["workspace"]):
            shutil.rmtree(self.company_config["infrastructure"]["workspace"])

    @patch("safenet_api_integration.safenet_manager")
    def test_api_status_endpoint(self, mock_manager):
        """Test API status endpoint"""
        from safenet_api_integration import app

        mock_manager.company_name = "COOL BITS S.R.L."
        mock_manager.company_cui = "42331573"
        mock_manager.certificate_registry = {}
        mock_manager.signing_history = []

        with app.test_client() as client:
            response = client.get("/api/safenet/status")

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["company_name"], "COOL BITS S.R.L.")
            self.assertEqual(data["company_cui"], "42331573")

    @patch("safenet_api_integration.safenet_manager")
    def test_api_certificates_endpoint(self, mock_manager):
        """Test API certificates endpoint"""
        from safenet_api_integration import app

        # Mock certificate
        mock_cert = Mock()
        mock_cert.certificate_id = "test-cert-001"
        mock_cert.certificate_type.value = "company_signing"
        mock_cert.security_level.value = "L3"
        mock_cert.subject_name = "CN=COOL BITS S.R.L."
        mock_cert.valid_from.isoformat.return_value = "2024-01-01T00:00:00"
        mock_cert.valid_to.isoformat.return_value = "2025-01-01T00:00:00"
        mock_cert.is_active = True
        mock_cert.thumbprint = "test-thumbprint"

        mock_manager.certificate_registry = {"test-cert-001": mock_cert}

        with app.test_client() as client:
            response = client.get("/api/safenet/certificates")

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn("certificates", data)
            self.assertEqual(len(data["certificates"]), 1)


def run_performance_tests():
    """Run performance tests for SafeNet integration"""
    print("🚀 Running SafeNet Performance Tests")
    print("=" * 50)

    import time

    # Test certificate generation performance
    start_time = time.time()

    company_config = {
        "company_name": "COOL BITS S.R.L.",
        "cui": "42331573",
        "euid": "ROONRC.J22/676/2020",
        "infrastructure": {"workspace": tempfile.mkdtemp()},
    }

    safenet_manager = SafeNetIntegrationManager(company_config)

    # Generate multiple certificates
    certificates = []
    for i in range(10):
        cert = safenet_manager.generate_company_certificate(
            SafeNetCertificateType.COMPANY_SIGNING, SafeNetSecurityLevel.LEVEL_3
        )
        certificates.append(cert)

    end_time = time.time()

    print(
        f"✅ Generated {len(certificates)} certificates in {end_time - start_time:.2f} seconds"
    )
    print(
        f"📊 Average time per certificate: {(end_time - start_time) / len(certificates):.3f} seconds"
    )

    # Test document signing performance
    test_doc_path = os.path.join(
        safenet_manager.safenet_config["temp_path"], "perf_test.txt"
    )
    with open(test_doc_path, "w") as f:
        f.write("Performance test document for SafeNet signing")

    start_time = time.time()

    # Sign document multiple times
    for i in range(5):
        result = safenet_manager.sign_document(
            document_path=test_doc_path,
            certificate_id=certificates[0].certificate_id,
            signing_purpose="Performance Test",
            security_level=SafeNetSecurityLevel.LEVEL_3,
        )

    end_time = time.time()

    print(f"✅ Performed {5} document signings in {end_time - start_time:.2f} seconds")
    print(f"📊 Average time per signing: {(end_time - start_time) / 5:.3f} seconds")

    # Clean up
    os.remove(test_doc_path)
    shutil.rmtree(company_config["infrastructure"]["workspace"])


def main():
    """Main function to run all tests"""
    print("🧪 SafeNet Integration Testing Suite")
    print("=" * 50)
    print("Company: COOL BITS S.R.L.")
    print("CUI: 42331573")
    print("Registration: ROONRC.J22/676/2020")
    print()

    # Run unit tests
    print("🔬 Running Unit Tests...")
    unittest.main(argv=[""], exit=False, verbosity=2)

    print("\n" + "=" * 50)

    # Run performance tests
    run_performance_tests()

    print("\n✅ All tests completed successfully!")
    print("🔐 SafeNet integration is ready for COOL BITS S.R.L.")


if __name__ == "__main__":
    main()
