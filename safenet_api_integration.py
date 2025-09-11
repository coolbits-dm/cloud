#!/usr/bin/env python3
"""
SafeNet API Integration Layer - COOL BITS SRL
REST API endpoints for SafeNet digital signing operations
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import tempfile
import uuid

from safenet_integration_architecture import (
    SafeNetIntegrationManager,
    SafeNetCertificateType,
    SafeNetSecurityLevel,
    SafeNetSigningRequest,
    SafeNetSigningResult,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global SafeNet manager instance
safenet_manager: Optional[SafeNetIntegrationManager] = None


def initialize_safenet_manager():
    """Initialize SafeNet manager with company configuration"""
    global safenet_manager

    try:
        # Load company configuration
        with open("coolbits_srl_complete_details.json", "r") as f:
            company_config = json.load(f)

        safenet_manager = SafeNetIntegrationManager(company_config)
        logger.info("SafeNet manager initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize SafeNet manager: {e}")
        raise


@app.route("/api/safenet/status", methods=["GET"])
def get_safenet_status():
    """Get SafeNet integration status"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        status = {
            "status": "active",
            "company_name": safenet_manager.company_name,
            "company_cui": safenet_manager.company_cui,
            "total_certificates": len(safenet_manager.certificate_registry),
            "total_signatures": len(safenet_manager.signing_history),
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting SafeNet status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/safenet/certificates", methods=["GET"])
def get_certificates():
    """Get all certificates"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        certificates = []
        for cert_id, cert in safenet_manager.certificate_registry.items():
            certificates.append(
                {
                    "certificate_id": cert_id,
                    "certificate_type": cert.certificate_type.value,
                    "security_level": cert.security_level.value,
                    "subject_name": cert.subject_name,
                    "valid_from": cert.valid_from.isoformat(),
                    "valid_to": cert.valid_to.isoformat(),
                    "is_active": cert.is_active,
                    "thumbprint": cert.thumbprint,
                }
            )

        return jsonify({"certificates": certificates})

    except Exception as e:
        logger.error(f"Error getting certificates: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/safenet/certificates", methods=["POST"])
def create_certificate():
    """Create new certificate"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        data = request.get_json()
        certificate_type = SafeNetCertificateType(data.get("certificate_type"))
        security_level = SafeNetSecurityLevel(data.get("security_level"))

        certificate = safenet_manager.generate_company_certificate(
            certificate_type, security_level
        )

        response = {
            "certificate_id": certificate.certificate_id,
            "certificate_type": certificate.certificate_type.value,
            "security_level": certificate.security_level.value,
            "subject_name": certificate.subject_name,
            "valid_from": certificate.valid_from.isoformat(),
            "valid_to": certificate.valid_to.isoformat(),
            "thumbprint": certificate.thumbprint,
            "status": "created",
        }

        return jsonify(response), 201

    except Exception as e:
        logger.error(f"Error creating certificate: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/safenet/certificates/<certificate_id>/status", methods=["GET"])
def get_certificate_status(certificate_id: str):
    """Get certificate status"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        status = safenet_manager.get_certificate_status(certificate_id)

        if status.get("status") == "not_found":
            return jsonify({"error": "Certificate not found"}), 404

        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting certificate status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/safenet/sign", methods=["POST"])
def sign_document():
    """Sign document using SafeNet"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        # Check if file is uploaded
        if "document" not in request.files:
            return jsonify({"error": "No document file provided"}), 400

        file = request.files["document"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Get signing parameters
        certificate_id = request.form.get("certificate_id")
        signing_purpose = request.form.get("signing_purpose", "Business Document")
        security_level_str = request.form.get("security_level", "L3")

        if not certificate_id:
            return jsonify({"error": "Certificate ID required"}), 400

        try:
            security_level = SafeNetSecurityLevel(security_level_str)
        except ValueError:
            return jsonify({"error": "Invalid security level"}), 400

        # Save uploaded file temporarily
        temp_dir = safenet_manager.safenet_config["temp_path"]
        temp_filename = f"temp_{uuid.uuid4()}_{file.filename}"
        temp_path = os.path.join(temp_dir, temp_filename)

        file.save(temp_path)

        try:
            # Sign the document
            result = safenet_manager.sign_document(
                document_path=temp_path,
                certificate_id=certificate_id,
                signing_purpose=signing_purpose,
                security_level=security_level,
            )

            response = {
                "request_id": result.request_id,
                "signature": result.signature,
                "certificate_used": result.certificate_used,
                "signing_timestamp": result.signing_timestamp.isoformat(),
                "verification_status": result.verification_status,
                "document_hash": (
                    result.audit_trail[0]["document_hash"]
                    if result.audit_trail
                    else None
                ),
                "status": "signed",
            }

            return jsonify(response)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Error signing document: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/safenet/verify", methods=["POST"])
def verify_signature():
    """Verify document signature"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        data = request.get_json()
        document_path = data.get("document_path")
        signature = data.get("signature")
        certificate_id = data.get("certificate_id")

        if not all([document_path, signature, certificate_id]):
            return jsonify({"error": "Missing required parameters"}), 400

        verification_result = safenet_manager.verify_signature(
            document_path, signature, certificate_id
        )

        response = {
            "verification_result": verification_result,
            "document_path": document_path,
            "certificate_id": certificate_id,
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/safenet/signing-history", methods=["GET"])
def get_signing_history():
    """Get signing history"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        history = []
        for result in safenet_manager.signing_history:
            history.append(
                {
                    "request_id": result.request_id,
                    "certificate_used": result.certificate_used,
                    "signing_timestamp": result.signing_timestamp.isoformat(),
                    "verification_status": result.verification_status,
                    "audit_trail": result.audit_trail,
                }
            )

        return jsonify({"signing_history": history})

    except Exception as e:
        logger.error(f"Error getting signing history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/safenet/compliance-report", methods=["GET"])
def get_compliance_report():
    """Get compliance report"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        report = safenet_manager.generate_compliance_report()
        return jsonify(report)

    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/safenet/audit-trail", methods=["GET"])
def get_audit_trail():
    """Get audit trail"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        audit_file = os.path.join(
            safenet_manager.safenet_config["logs_path"], "audit_trail.json"
        )

        if not os.path.exists(audit_file):
            return jsonify({"audit_trail": []})

        with open(audit_file, "r") as f:
            audit_data = json.load(f)

        return jsonify({"audit_trail": audit_data})

    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/safenet/install", methods=["POST"])
def install_safenet():
    """Install SafeNet Authentication Client"""
    try:
        if not safenet_manager:
            return jsonify({"error": "SafeNet manager not initialized"}), 500

        success = safenet_manager.install_safenet_client()

        if success:
            return jsonify(
                {
                    "status": "installed",
                    "message": "SafeNet client installed successfully",
                }
            )
        else:
            return jsonify({"error": "Failed to install SafeNet client"}), 500

    except Exception as e:
        logger.error(f"Error installing SafeNet: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


def main():
    """Main function to run SafeNet API server"""
    print("🔐 SafeNet Authentication Client API Server")
    print("=" * 50)

    # Initialize SafeNet manager
    try:
        initialize_safenet_manager()
        print("✅ SafeNet manager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize SafeNet manager: {e}")
        return

    # Start Flask server
    print("🚀 Starting SafeNet API server...")
    print("📡 Available endpoints:")
    print("  GET  /api/safenet/status")
    print("  GET  /api/safenet/certificates")
    print("  POST /api/safenet/certificates")
    print("  GET  /api/safenet/certificates/<id>/status")
    print("  POST /api/safenet/sign")
    print("  POST /api/safenet/verify")
    print("  GET  /api/safenet/signing-history")
    print("  GET  /api/safenet/compliance-report")
    print("  GET  /api/safenet/audit-trail")
    print("  POST /api/safenet/install")

    app.run(host="0.0.0.0", port=5001, debug=True)


if __name__ == "__main__":
    main()
