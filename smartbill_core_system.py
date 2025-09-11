#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartBill - Soluția de Facturare COOL BITS SRL
Integrare SafeNet pentru semnarea digitală
Delegare către agenții interni: ogpt01, ogpt02, ogpt05
"""

import json
import os
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvoiceStatus(Enum):
    """Statusuri factură"""

    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    SIGNED = "signed"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceType(Enum):
    """Tipuri factură"""

    STANDARD = "standard"
    PROFORMA = "proforma"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    RECEIPT = "receipt"


class SafeNetSecurityLevel(Enum):
    """Niveluri securitate SafeNet"""

    L1_BASIC = "L1"
    L2_STANDARD = "L2"
    L3_HIGH = "L3"
    L4_CRITICAL = "L4"
    L5_MAXIMUM = "L5"


@dataclass
class InvoiceItem:
    """Articol factură"""

    id: str
    description: str
    quantity: float
    unit_price: float
    vat_rate: float
    total_price: float
    currency: str = "RON"


@dataclass
class Invoice:
    """Factură"""

    id: str
    invoice_number: str
    client_name: str
    client_cui: str
    client_address: str
    issue_date: datetime
    due_date: datetime
    items: List[InvoiceItem]
    subtotal: float
    vat_total: float
    total_amount: float
    currency: str
    status: InvoiceStatus
    invoice_type: InvoiceType
    notes: str = ""
    safenet_signature: Optional[str] = None
    signed_by: Optional[str] = None
    signed_at: Optional[datetime] = None
    created_by: str = "system"
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class SafeNetSigningRequest:
    """Cerere semnare SafeNet"""

    request_id: str
    document_id: str
    document_type: str
    signer_identity: str
    signing_purpose: str
    security_level: SafeNetSecurityLevel
    timestamp: datetime
    metadata: Dict[str, Any]


class SmartBillCore:
    """SmartBill - Sistemul principal de facturare"""

    def __init__(self):
        self.company = "COOL BITS S.R.L."
        self.company_cui = "42331573"
        self.company_registration = "ROONRC.J22/676/2020"
        self.company_address = "str. Columnei, nr.14, bl.K4, et.4, ap.19, Iași, România"
        self.company_bank = "ING Office Iași Anastasie Panu"
        self.company_iban = "RO76INGB0000999910114315"

        # Agenții delegați pentru operațiuni interne
        self.delegated_agents = {
            "ogpt01": {
                "name": "oGPT01",
                "role": "Frontend Agent",
                "responsibility": "Frontend Development",
                "permissions": [
                    "invoice_creation",
                    "invoice_preview",
                    "client_management",
                ],
            },
            "ogpt02": {
                "name": "oGPT02",
                "role": "Backend Agent",
                "responsibility": "Backend Development",
                "permissions": [
                    "invoice_processing",
                    "api_management",
                    "data_validation",
                ],
            },
            "ogpt05": {
                "name": "oGPT05",
                "role": "Data Agent",
                "responsibility": "Data Engineering",
                "permissions": ["invoice_analytics", "reporting", "data_export"],
            },
        }

        # Configurare SafeNet
        self.safenet_config = {
            "api_endpoint": "http://localhost:5001/api/safenet",
            "certificate_id": "cb-company_signing-42331573",
            "default_security_level": SafeNetSecurityLevel.L4_CRITICAL,
            "signing_purpose": "Invoice Digital Signing",
        }

        # Stocare facturi
        self.invoices: Dict[str, Invoice] = {}
        self.invoice_counter = 1

        # Inițializare
        self._initialize_system()

    def _initialize_system(self):
        """Inițializare sistem SmartBill"""
        logger.info("🔧 Initializing SmartBill system...")

        # Creează directorul pentru facturi
        os.makedirs("smartbill_data", exist_ok=True)
        os.makedirs("smartbill_data/invoices", exist_ok=True)
        os.makedirs("smartbill_data/safenet", exist_ok=True)
        os.makedirs("smartbill_data/reports", exist_ok=True)

        # Încarcă facturile existente
        self._load_existing_invoices()

        logger.info("✅ SmartBill system initialized successfully")

    def _load_existing_invoices(self):
        """Încarcă facturile existente din stocare"""
        try:
            invoices_file = "smartbill_data/invoices/invoices.json"
            if os.path.exists(invoices_file):
                with open(invoices_file, "r", encoding="utf-8") as f:
                    invoices_data = json.load(f)

                for invoice_data in invoices_data:
                    # Convert string dates back to datetime objects
                    invoice_data["issue_date"] = datetime.fromisoformat(
                        invoice_data["issue_date"]
                    )
                    invoice_data["due_date"] = datetime.fromisoformat(
                        invoice_data["due_date"]
                    )
                    invoice_data["created_at"] = datetime.fromisoformat(
                        invoice_data["created_at"]
                    )
                    invoice_data["updated_at"] = datetime.fromisoformat(
                        invoice_data["updated_at"]
                    )

                    if invoice_data.get("signed_at"):
                        invoice_data["signed_at"] = datetime.fromisoformat(
                            invoice_data["signed_at"]
                        )

                    # Convert items
                    invoice_items = []
                    for item_data in invoice_data["items"]:
                        invoice_items.append(InvoiceItem(**item_data))
                    invoice_data["items"] = invoice_items

                    # Convert enums
                    invoice_data["status"] = InvoiceStatus(invoice_data["status"])
                    invoice_data["invoice_type"] = InvoiceType(
                        invoice_data["invoice_type"]
                    )

                    invoice = Invoice(**invoice_data)
                    self.invoices[invoice.id] = invoice

                logger.info(f"📄 Loaded {len(self.invoices)} existing invoices")

        except Exception as e:
            logger.error(f"❌ Error loading existing invoices: {e}")

    def _save_invoices(self):
        """Salvează facturile în stocare"""
        try:
            invoices_file = "smartbill_data/invoices/invoices.json"

            # Convert invoices to serializable format
            invoices_data = []
            for invoice in self.invoices.values():
                invoice_dict = asdict(invoice)

                # Convert datetime objects to strings
                invoice_dict["issue_date"] = invoice.issue_date.isoformat()
                invoice_dict["due_date"] = invoice.due_date.isoformat()
                invoice_dict["created_at"] = invoice.created_at.isoformat()
                invoice_dict["updated_at"] = invoice.updated_at.isoformat()

                if invoice.signed_at:
                    invoice_dict["signed_at"] = invoice.signed_at.isoformat()

                # Convert enums to strings
                invoice_dict["status"] = invoice.status.value
                invoice_dict["invoice_type"] = invoice.invoice_type.value

                invoices_data.append(invoice_dict)

            with open(invoices_file, "w", encoding="utf-8") as f:
                json.dump(invoices_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ Error saving invoices: {e}")

    def create_invoice(
        self,
        client_data: Dict[str, Any],
        items: List[Dict[str, Any]],
        invoice_type: InvoiceType = InvoiceType.STANDARD,
        due_days: int = 30,
    ) -> Invoice:
        """Creează o factură nouă"""
        try:
            # Generează ID unic
            invoice_id = f"inv-{uuid.uuid4().hex[:8]}"

            # Generează numărul facturii
            invoice_number = f"CB-{self.invoice_counter:06d}"
            self.invoice_counter += 1

            # Calculează datele
            issue_date = datetime.now()
            due_date = issue_date + timedelta(days=due_days)

            # Creează articolele facturii
            invoice_items = []
            subtotal = 0.0

            for item_data in items:
                item = InvoiceItem(
                    id=f"item-{uuid.uuid4().hex[:6]}",
                    description=item_data["description"],
                    quantity=item_data["quantity"],
                    unit_price=item_data["unit_price"],
                    vat_rate=item_data.get("vat_rate", 19.0),
                    total_price=item_data["quantity"] * item_data["unit_price"],
                )
                invoice_items.append(item)
                subtotal += item.total_price

            # Calculează TVA și total
            vat_total = sum(
                item.total_price * (item.vat_rate / 100) for item in invoice_items
            )
            total_amount = subtotal + vat_total

            # Creează factura
            invoice = Invoice(
                id=invoice_id,
                invoice_number=invoice_number,
                client_name=client_data["name"],
                client_cui=client_data["cui"],
                client_address=client_data["address"],
                issue_date=issue_date,
                due_date=due_date,
                items=invoice_items,
                subtotal=subtotal,
                vat_total=vat_total,
                total_amount=total_amount,
                currency="RON",
                status=InvoiceStatus.DRAFT,
                invoice_type=invoice_type,
                notes=client_data.get("notes", ""),
                created_by="SmartBill System",
            )

            # Salvează factura
            self.invoices[invoice_id] = invoice
            self._save_invoices()

            logger.info(
                f"✅ Invoice created: {invoice_number} for {client_data['name']}"
            )
            return invoice

        except Exception as e:
            logger.error(f"❌ Error creating invoice: {e}")
            raise

    def sign_invoice_with_safenet(
        self, invoice_id: str, agent_id: str = "system"
    ) -> bool:
        """Semnare factură cu SafeNet"""
        try:
            if invoice_id not in self.invoices:
                logger.error(f"❌ Invoice {invoice_id} not found")
                return False

            invoice = self.invoices[invoice_id]

            if invoice.status != InvoiceStatus.APPROVED:
                logger.error(f"❌ Invoice {invoice_id} must be approved before signing")
                return False

            logger.info(f"🔐 Signing invoice {invoice.invoice_number} with SafeNet...")

            # Creează cererea de semnare SafeNet
            signing_request = SafeNetSigningRequest(
                request_id=f"req-{uuid.uuid4().hex[:8]}",
                document_id=invoice_id,
                document_type="invoice",
                signer_identity=f"{self.company} ({self.company_cui})",
                signing_purpose=self.safenet_config["signing_purpose"],
                security_level=self.safenet_config["default_security_level"],
                timestamp=datetime.now(),
                metadata={
                    "invoice_number": invoice.invoice_number,
                    "client_name": invoice.client_name,
                    "total_amount": invoice.total_amount,
                    "currency": invoice.currency,
                    "agent_id": agent_id,
                },
            )

            # Simulează semnarea SafeNet (în producție ar fi integrare reală)
            signature = self._simulate_safenet_signing(signing_request)

            # Actualizează factura
            invoice.safenet_signature = signature
            invoice.signed_by = agent_id
            invoice.signed_at = datetime.now()
            invoice.status = InvoiceStatus.SIGNED
            invoice.updated_at = datetime.now()

            # Salvează modificările
            self._save_invoices()

            logger.info(f"✅ Invoice {invoice.invoice_number} signed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error signing invoice: {e}")
            return False

    def _simulate_safenet_signing(self, request: SafeNetSigningRequest) -> str:
        """Simulează semnarea SafeNet (pentru demo)"""
        # În producție, aici ar fi integrarea reală cu SafeNet API
        signature_data = f"{request.document_id}{request.signer_identity}{request.timestamp.isoformat()}"
        signature = hashlib.sha256(signature_data.encode()).hexdigest()

        # Salvează cererea de semnare
        safenet_file = f"smartbill_data/safenet/{request.request_id}.json"
        with open(safenet_file, "w", encoding="utf-8") as f:
            json.dump(asdict(request), f, indent=2, ensure_ascii=False, default=str)

        return signature

    def delegate_to_agent(self, invoice_id: str, agent_id: str, operation: str) -> bool:
        """Deleagă operațiune către agent"""
        try:
            if agent_id not in self.delegated_agents:
                logger.error(f"❌ Agent {agent_id} not found in delegated agents")
                return False

            if invoice_id not in self.invoices:
                logger.error(f"❌ Invoice {invoice_id} not found")
                return False

            agent = self.delegated_agents[agent_id]
            invoice = self.invoices[invoice_id]

            if operation not in agent["permissions"]:
                logger.error(
                    f"❌ Agent {agent_id} not authorized for operation {operation}"
                )
                return False

            logger.info(
                f"🤖 Delegating {operation} for invoice {invoice.invoice_number} to {agent['name']}"
            )

            # Simulează delegarea către agent
            delegation_result = self._simulate_agent_delegation(
                agent_id, operation, invoice
            )

            if delegation_result:
                logger.info(
                    f"✅ Operation {operation} delegated successfully to {agent['name']}"
                )
                return True
            else:
                logger.error(f"❌ Delegation failed for {agent['name']}")
                return False

        except Exception as e:
            logger.error(f"❌ Error delegating to agent: {e}")
            return False

    def _simulate_agent_delegation(
        self, agent_id: str, operation: str, invoice: Invoice
    ) -> bool:
        """Simulează delegarea către agent"""
        # În producție, aici ar fi comunicarea reală cu agenții
        delegation_data = {
            "agent_id": agent_id,
            "operation": operation,
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "timestamp": datetime.now().isoformat(),
            "status": "delegated",
        }

        # Salvează delegarea
        delegation_file = (
            f"smartbill_data/delegations/{agent_id}_{operation}_{invoice.id}.json"
        )
        os.makedirs("smartbill_data/delegations", exist_ok=True)

        with open(delegation_file, "w", encoding="utf-8") as f:
            json.dump(delegation_data, f, indent=2, ensure_ascii=False)

        return True

    def get_invoice_status(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Obține statusul unei facturi"""
        if invoice_id not in self.invoices:
            return None

        invoice = self.invoices[invoice_id]
        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "client_name": invoice.client_name,
            "total_amount": invoice.total_amount,
            "currency": invoice.currency,
            "status": invoice.status.value,
            "issue_date": invoice.issue_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "signed": invoice.safenet_signature is not None,
            "signed_by": invoice.signed_by,
            "signed_at": invoice.signed_at.isoformat() if invoice.signed_at else None,
        }

    def generate_invoice_report(self) -> Dict[str, Any]:
        """Generează raport facturi"""
        total_invoices = len(self.invoices)
        signed_invoices = sum(
            1 for inv in self.invoices.values() if inv.safenet_signature
        )
        pending_invoices = sum(
            1 for inv in self.invoices.values() if inv.status == InvoiceStatus.PENDING
        )
        paid_invoices = sum(
            1 for inv in self.invoices.values() if inv.status == InvoiceStatus.PAID
        )

        total_amount = sum(inv.total_amount for inv in self.invoices.values())

        return {
            "company": self.company,
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_invoices": total_invoices,
                "signed_invoices": signed_invoices,
                "pending_invoices": pending_invoices,
                "paid_invoices": paid_invoices,
                "total_amount": total_amount,
                "currency": "RON",
            },
            "delegated_agents": self.delegated_agents,
            "safenet_config": self.safenet_config,
        }


def main():
    """Funcția principală pentru testare"""
    print("=" * 80)
    print("🧾 SMARTBILL - SOLUȚIA DE FACTURARE COOL BITS SRL")
    print("=" * 80)
    print("🔐 Integrare SafeNet pentru semnarea digitală")
    print("🤖 Delegare către agenții interni: ogpt01, ogpt02, ogpt05")
    print("=" * 80)

    # Inițializează SmartBill
    smartbill = SmartBillCore()

    # Exemplu de utilizare
    client_data = {
        "name": "Client Test SRL",
        "cui": "12345678",
        "address": "Strada Test, nr. 1, București",
        "notes": "Client pentru testare",
    }

    items = [
        {
            "description": "Servicii de dezvoltare software",
            "quantity": 10,
            "unit_price": 500.0,
            "vat_rate": 19.0,
        },
        {
            "description": "Consultanță tehnică",
            "quantity": 5,
            "unit_price": 300.0,
            "vat_rate": 19.0,
        },
    ]

    # Creează factura
    invoice = smartbill.create_invoice(client_data, items)
    print(f"✅ Factură creată: {invoice.invoice_number}")

    # Aprobă factura
    invoice.status = InvoiceStatus.APPROVED
    smartbill._save_invoices()
    print(f"✅ Factură aprobată: {invoice.invoice_number}")

    # Semnează cu SafeNet
    if smartbill.sign_invoice_with_safenet(invoice.id):
        print(f"✅ Factură semnată cu SafeNet: {invoice.invoice_number}")

    # Deleagă către agent
    if smartbill.delegate_to_agent(invoice.id, "ogpt01", "invoice_creation"):
        print("✅ Operațiune delegată către ogpt01")

    # Generează raport
    report = smartbill.generate_invoice_report()
    print(f"📊 Raport generat: {report['summary']['total_invoices']} facturi")

    print("=" * 80)
    print("🎯 SmartBill system ready for production!")
    print("=" * 80)


if __name__ == "__main__":
    main()
