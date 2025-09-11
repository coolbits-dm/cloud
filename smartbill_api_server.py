#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartBill API Server - COOL BITS SRL
API endpoints pentru SmartBill cu autentificare SafeNet
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Import SmartBill modules
from smartbill_core_system import SmartBillCore, InvoiceStatus, InvoiceType
from smartbill_safenet_integration import SmartBillSafeNetIntegration
from smartbill_agent_delegation import SmartBillAgentDelegation
from smartbill_cursor_gemini_integration import SmartBillCursorGeminiIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global instances
smartbill_core: Optional[SmartBillCore] = None
safenet_integration: Optional[SmartBillSafeNetIntegration] = None
agent_delegation: Optional[SmartBillAgentDelegation] = None
cursor_gemini_integration: Optional[SmartBillCursorGeminiIntegration] = None


def initialize_smartbill_system():
    """Initialize SmartBill system components"""
    global smartbill_core, safenet_integration, agent_delegation, cursor_gemini_integration

    try:
        logger.info("🚀 Initializing SmartBill API Server...")

        # Initialize core components
        smartbill_core = SmartBillCore()
        safenet_integration = SmartBillSafeNetIntegration()
        agent_delegation = SmartBillAgentDelegation()
        cursor_gemini_integration = SmartBillCursorGeminiIntegration()

        logger.info("✅ SmartBill API Server initialized successfully")

    except Exception as e:
        logger.error(f"❌ Error initializing SmartBill system: {e}")
        raise


# API Routes


@app.route("/api/smartbill/status", methods=["GET"])
def get_smartbill_status():
    """Get SmartBill system status"""
    try:
        status = {
            "company": "COOL BITS S.R.L.",
            "system": "SmartBill",
            "version": "1.0.0",
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "core_system": "active",
                "safenet_integration": (
                    safenet_integration.get_safenet_status()
                    if safenet_integration
                    else "inactive"
                ),
                "agent_delegation": "active",
                "cursor_gemini_integration": (
                    cursor_gemini_integration.get_integration_status()
                    if cursor_gemini_integration
                    else "inactive"
                ),
            },
        }

        return jsonify(status), 200

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/invoices", methods=["GET"])
def get_invoices():
    """Get all invoices"""
    try:
        if not smartbill_core:
            return jsonify({"error": "SmartBill core not initialized"}), 500

        invoices = []
        for invoice in smartbill_core.invoices.values():
            invoice_data = {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "client_name": invoice.client_name,
                "client_cui": invoice.client_cui,
                "total_amount": invoice.total_amount,
                "currency": invoice.currency,
                "status": invoice.status.value,
                "issue_date": invoice.issue_date.isoformat(),
                "due_date": invoice.due_date.isoformat(),
                "signed": invoice.safenet_signature is not None,
                "signed_by": invoice.signed_by,
                "signed_at": (
                    invoice.signed_at.isoformat() if invoice.signed_at else None
                ),
            }
            invoices.append(invoice_data)

        return (
            jsonify(
                {
                    "invoices": invoices,
                    "total_count": len(invoices),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting invoices: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/invoices", methods=["POST"])
def create_invoice():
    """Create new invoice"""
    try:
        if not smartbill_core:
            return jsonify({"error": "SmartBill core not initialized"}), 500

        data = request.get_json()

        # Validate required fields
        required_fields = ["client_data", "items"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create invoice
        invoice = smartbill_core.create_invoice(
            data["client_data"],
            data["items"],
            InvoiceType(data.get("invoice_type", "standard")),
            data.get("due_days", 30),
        )

        # Convert to response format
        invoice_response = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "client_name": invoice.client_name,
            "client_cui": invoice.client_cui,
            "total_amount": invoice.total_amount,
            "currency": invoice.currency,
            "status": invoice.status.value,
            "issue_date": invoice.issue_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "items": [
                {
                    "id": item.id,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "vat_rate": item.vat_rate,
                    "total_price": item.total_price,
                }
                for item in invoice.items
            ],
        }

        return (
            jsonify(
                {"message": "Invoice created successfully", "invoice": invoice_response}
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/invoices/<invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    """Get specific invoice"""
    try:
        if not smartbill_core:
            return jsonify({"error": "SmartBill core not initialized"}), 500

        invoice_status = smartbill_core.get_invoice_status(invoice_id)

        if not invoice_status:
            return jsonify({"error": "Invoice not found"}), 404

        return jsonify(invoice_status), 200

    except Exception as e:
        logger.error(f"Error getting invoice: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/invoices/<invoice_id>/sign", methods=["POST"])
def sign_invoice(invoice_id):
    """Sign invoice with SafeNet"""
    try:
        if not smartbill_core or not safenet_integration:
            return jsonify({"error": "SmartBill system not initialized"}), 500

        data = request.get_json() or {}
        agent_id = data.get("agent_id", "system")

        # Sign invoice
        success = smartbill_core.sign_invoice_with_safenet(invoice_id, agent_id)

        if success:
            # Get updated invoice status
            invoice_status = smartbill_core.get_invoice_status(invoice_id)

            return (
                jsonify(
                    {
                        "message": "Invoice signed successfully",
                        "invoice_status": invoice_status,
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "Failed to sign invoice"}), 500

    except Exception as e:
        logger.error(f"Error signing invoice: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/invoices/<invoice_id>/delegate", methods=["POST"])
def delegate_invoice_operation(invoice_id):
    """Delegate invoice operation to agent"""
    try:
        if not agent_delegation:
            return jsonify({"error": "Agent delegation not initialized"}), 500

        data = request.get_json()

        # Validate required fields
        required_fields = ["operation", "agent_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Delegate operation
        result = agent_delegation.delegate_operation(
            invoice_id,
            data["operation"],
            data["agent_id"],
            data.get("priority", "normal"),
        )

        if result:
            return (
                jsonify(
                    {"message": "Operation delegated successfully", "result": result}
                ),
                200,
            )
        else:
            return jsonify({"error": "Failed to delegate operation"}), 500

    except Exception as e:
        logger.error(f"Error delegating operation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/workflows", methods=["POST"])
def execute_workflow():
    """Execute integrated workflow"""
    try:
        if not cursor_gemini_integration:
            return jsonify({"error": "Cursor/Gemini integration not initialized"}), 500

        data = request.get_json()

        # Validate required fields
        required_fields = ["workflow_name", "invoice_data"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Execute workflow
        result = cursor_gemini_integration.execute_integrated_workflow(
            data["workflow_name"], data["invoice_data"]
        )

        if result:
            return (
                jsonify(
                    {
                        "message": "Workflow executed successfully",
                        "workflow_result": result,
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "Failed to execute workflow"}), 500

    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/agents", methods=["GET"])
def get_agents():
    """Get available agents"""
    try:
        if not agent_delegation:
            return jsonify({"error": "Agent delegation not initialized"}), 500

        agents = {}
        for agent_id, agent_info in agent_delegation.delegated_agents.items():
            agent_status = agent_delegation.get_agent_status(agent_id)
            agents[agent_id] = {"info": agent_info, "status": agent_status}

        return (
            jsonify(
                {
                    "agents": agents,
                    "total_count": len(agents),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/operations", methods=["GET"])
def get_available_operations():
    """Get available operations"""
    try:
        if not agent_delegation:
            return jsonify({"error": "Agent delegation not initialized"}), 500

        return (
            jsonify(
                {
                    "operations": agent_delegation.available_operations,
                    "total_count": len(agent_delegation.available_operations),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting operations: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/workflows", methods=["GET"])
def get_available_workflows():
    """Get available workflows"""
    try:
        if not cursor_gemini_integration:
            return jsonify({"error": "Cursor/Gemini integration not initialized"}), 500

        return (
            jsonify(
                {
                    "workflows": cursor_gemini_integration.integrated_workflows,
                    "total_count": len(cursor_gemini_integration.integrated_workflows),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/reports/invoice", methods=["GET"])
def get_invoice_report():
    """Get invoice report"""
    try:
        if not smartbill_core:
            return jsonify({"error": "SmartBill core not initialized"}), 500

        report = smartbill_core.generate_invoice_report()
        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Error generating invoice report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/reports/delegation", methods=["GET"])
def get_delegation_report():
    """Get delegation report"""
    try:
        if not agent_delegation:
            return jsonify({"error": "Agent delegation not initialized"}), 500

        report = agent_delegation.get_delegation_report()
        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Error generating delegation report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/reports/integration", methods=["GET"])
def get_integration_report():
    """Get integration report"""
    try:
        if not cursor_gemini_integration:
            return jsonify({"error": "Cursor/Gemini integration not initialized"}), 500

        report = cursor_gemini_integration.generate_integration_report()
        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Error generating integration report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/safenet/status", methods=["GET"])
def get_safenet_status():
    """Get SafeNet status"""
    try:
        if not safenet_integration:
            return jsonify({"error": "SafeNet integration not initialized"}), 500

        status = safenet_integration.get_safenet_status()
        return jsonify(status), 200

    except Exception as e:
        logger.error(f"Error getting SafeNet status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/smartbill/safenet/report", methods=["GET"])
def get_safenet_report():
    """Get SafeNet report"""
    try:
        if not safenet_integration:
            return jsonify({"error": "SafeNet integration not initialized"}), 500

        report = safenet_integration.generate_safenet_report()
        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Error generating SafeNet report: {e}")
        return jsonify({"error": str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


def main():
    """Main function to run the API server"""
    print("=" * 80)
    print("🚀 SMARTBILL API SERVER - COOL BITS SRL")
    print("=" * 80)
    print("🔐 Integrare SafeNet pentru semnarea digitală")
    print("🤖 Delegare către agenții interni: ogpt01, ogpt02, ogpt05")
    print("🔗 Integrare oCursor și GeminiCLI")
    print("=" * 80)

    # Initialize SmartBill system
    initialize_smartbill_system()

    # Start API server
    print("🌐 Starting SmartBill API Server...")
    print("📍 Server will be available at: http://localhost:5002")
    print("📚 API Documentation: http://localhost:5002/api/smartbill/status")
    print("=" * 80)

    app.run(host="0.0.0.0", port=5002, debug=True)


if __name__ == "__main__":
    main()
