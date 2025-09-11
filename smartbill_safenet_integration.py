#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartBill SafeNet Integration - COOL BITS SRL
Integrare completă cu SafeNet pentru semnarea digitală a facturilor
"""

import json
import os
import requests
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartBillSafeNetIntegration:
    """Integrare SmartBill cu SafeNet pentru semnarea digitală"""

    def __init__(self):
        self.company = "COOL BITS S.R.L."
        self.company_cui = "42331573"
        self.company_registration = "ROONRC.J22/676/2020"

        # Configurare SafeNet
        self.safenet_config = {
            "api_endpoint": "http://localhost:5001/api/safenet",
            "certificate_id": "cb-company_signing-42331573",
            "default_security_level": "L4",
            "signing_purpose": "Invoice Digital Signing",
            "company_info": {
                "name": self.company,
                "cui": self.company_cui,
                "registration": self.company_registration,
                "address": "str. Columnei, nr.14, bl.K4, et.4, ap.19, Iași, România",
            },
        }

        # Status SafeNet
        self.safenet_status = {
            "connected": False,
            "certificates_available": False,
            "last_check": None,
            "error_message": None,
        }

        # Inițializare
        self._initialize_safenet_connection()

    def _initialize_safenet_connection(self):
        """Inițializează conexiunea cu SafeNet"""
        try:
            logger.info("🔐 Initializing SafeNet connection...")

            # Verifică statusul SafeNet API
            status_response = self._check_safenet_status()

            if status_response and status_response.get("status") == "active":
                self.safenet_status["connected"] = True
                self.safenet_status["last_check"] = datetime.now()
                logger.info("✅ SafeNet connection established")

                # Verifică certificatele disponibile
                certificates = self._get_available_certificates()
                if certificates:
                    self.safenet_status["certificates_available"] = True
                    logger.info(f"✅ Found {len(certificates)} available certificates")
                else:
                    logger.warning("⚠️ No certificates available")

            else:
                self.safenet_status["connected"] = False
                self.safenet_status["error_message"] = "SafeNet API not available"
                logger.error("❌ SafeNet API not available")

        except Exception as e:
            self.safenet_status["connected"] = False
            self.safenet_status["error_message"] = str(e)
            logger.error(f"❌ Error initializing SafeNet: {e}")

    def _check_safenet_status(self) -> Optional[Dict[str, Any]]:
        """Verifică statusul SafeNet API"""
        try:
            response = requests.get(
                f"{self.safenet_config['api_endpoint']}/status", timeout=5
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"SafeNet API returned status {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to SafeNet API: {e}")
            return None

    def _get_available_certificates(self) -> List[Dict[str, Any]]:
        """Obține certificatele disponibile"""
        try:
            response = requests.get(
                f"{self.safenet_config['api_endpoint']}/certificates", timeout=5
            )

            if response.status_code == 200:
                return response.json().get("certificates", [])
            else:
                logger.error(f"Error getting certificates: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting certificates: {e}")
            return []

    def sign_invoice_document(
        self, invoice_data: Dict[str, Any], security_level: str = "L4"
    ) -> Optional[Dict[str, Any]]:
        """Semnare document factură cu SafeNet"""
        try:
            if not self.safenet_status["connected"]:
                logger.error("❌ SafeNet not connected")
                return None

            logger.info(
                f"🔐 Signing invoice {invoice_data.get('invoice_number')} with SafeNet..."
            )

            # Pregătește documentul pentru semnare
            document_content = self._prepare_invoice_for_signing(invoice_data)

            # Creează cererea de semnare
            signing_request = {
                "certificate_id": self.safenet_config["certificate_id"],
                "document_content": document_content,
                "signing_purpose": self.safenet_config["signing_purpose"],
                "security_level": security_level,
                "metadata": {
                    "invoice_number": invoice_data.get("invoice_number"),
                    "client_name": invoice_data.get("client_name"),
                    "total_amount": invoice_data.get("total_amount"),
                    "currency": invoice_data.get("currency", "RON"),
                    "company_info": self.safenet_config["company_info"],
                },
            }

            # Trimite cererea către SafeNet API
            response = requests.post(
                f"{self.safenet_config['api_endpoint']}/sign",
                json=signing_request,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()

                # Salvează rezultatul semnării
                self._save_signing_result(invoice_data["id"], result)

                logger.info(
                    f"✅ Invoice {invoice_data.get('invoice_number')} signed successfully"
                )
                return result
            else:
                logger.error(f"❌ Signing failed: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Error signing invoice: {e}")
            return None

    def _prepare_invoice_for_signing(self, invoice_data: Dict[str, Any]) -> str:
        """Pregătește factura pentru semnare"""
        # Creează conținutul documentului pentru semnare
        document_content = f"""
INVOICE DOCUMENT - COOL BITS S.R.L.
=====================================

Invoice Number: {invoice_data.get('invoice_number')}
Issue Date: {invoice_data.get('issue_date')}
Due Date: {invoice_data.get('due_date')}

CLIENT INFORMATION:
-------------------
Name: {invoice_data.get('client_name')}
CUI: {invoice_data.get('client_cui')}
Address: {invoice_data.get('client_address')}

COMPANY INFORMATION:
--------------------
Name: {self.company}
CUI: {self.company_cui}
Registration: {self.company_registration}
Address: {self.safenet_config['company_info']['address']}

INVOICE DETAILS:
----------------
Subtotal: {invoice_data.get('subtotal')} {invoice_data.get('currency', 'RON')}
VAT Total: {invoice_data.get('vat_total')} {invoice_data.get('currency', 'RON')}
Total Amount: {invoice_data.get('total_amount')} {invoice_data.get('currency', 'RON')}

ITEMS:
-------
"""

        # Adaugă articolele
        for item in invoice_data.get("items", []):
            document_content += f"""
- {item.get('description')}
  Quantity: {item.get('quantity')}
  Unit Price: {item.get('unit_price')} {invoice_data.get('currency', 'RON')}
  VAT Rate: {item.get('vat_rate')}%
  Total: {item.get('total_price')} {invoice_data.get('currency', 'RON')}
"""

        document_content += f"""
=====================================
Document Hash: {self._calculate_document_hash(document_content)}
Signing Purpose: {self.safenet_config['signing_purpose']}
Security Level: L4 (Critical)
Timestamp: {datetime.now().isoformat()}
=====================================
"""

        return document_content

    def _calculate_document_hash(self, content: str) -> str:
        """Calculează hash-ul documentului"""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _save_signing_result(self, invoice_id: str, signing_result: Dict[str, Any]):
        """Salvează rezultatul semnării"""
        try:
            os.makedirs("smartbill_data/safenet/signatures", exist_ok=True)

            signature_file = (
                f"smartbill_data/safenet/signatures/{invoice_id}_signature.json"
            )

            signature_data = {
                "invoice_id": invoice_id,
                "signing_result": signing_result,
                "timestamp": datetime.now().isoformat(),
                "company": self.company,
                "certificate_id": self.safenet_config["certificate_id"],
            }

            with open(signature_file, "w", encoding="utf-8") as f:
                json.dump(signature_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error saving signing result: {e}")

    def verify_invoice_signature(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Verifică semnătura unei facturi"""
        try:
            if not self.safenet_status["connected"]:
                logger.error("❌ SafeNet not connected")
                return None

            # Încarcă rezultatul semnării
            signature_file = (
                f"smartbill_data/safenet/signatures/{invoice_id}_signature.json"
            )

            if not os.path.exists(signature_file):
                logger.error(f"❌ Signature file not found for invoice {invoice_id}")
                return None

            with open(signature_file, "r", encoding="utf-8") as f:
                signature_data = json.load(f)

            signing_result = signature_data["signing_result"]

            # Trimite cererea de verificare către SafeNet API
            verify_request = {
                "signature": signing_result.get("signature"),
                "document_hash": signing_result.get("document_hash"),
                "certificate_id": signing_result.get("certificate_id"),
            }

            response = requests.post(
                f"{self.safenet_config['api_endpoint']}/verify",
                json=verify_request,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    f"✅ Signature verification completed for invoice {invoice_id}"
                )
                return result
            else:
                logger.error(f"❌ Verification failed: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Error verifying signature: {e}")
            return None

    def get_safenet_status(self) -> Dict[str, Any]:
        """Obține statusul SafeNet"""
        return {
            "safenet_status": self.safenet_status,
            "safenet_config": self.safenet_config,
            "company_info": self.safenet_config["company_info"],
        }

    def generate_safenet_report(self) -> Dict[str, Any]:
        """Generează raport SafeNet"""
        try:
            # Numără semnăturile
            signatures_dir = "smartbill_data/safenet/signatures"
            signature_count = 0

            if os.path.exists(signatures_dir):
                signature_count = len(
                    [f for f in os.listdir(signatures_dir) if f.endswith(".json")]
                )

            return {
                "company": self.company,
                "report_date": datetime.now().isoformat(),
                "safenet_status": self.safenet_status,
                "summary": {
                    "total_signatures": signature_count,
                    "certificate_id": self.safenet_config["certificate_id"],
                    "default_security_level": self.safenet_config[
                        "default_security_level"
                    ],
                    "api_endpoint": self.safenet_config["api_endpoint"],
                },
                "certificates": self._get_available_certificates(),
            }

        except Exception as e:
            logger.error(f"Error generating SafeNet report: {e}")
            return {}


def main():
    """Funcția principală pentru testare"""
    print("=" * 80)
    print("🔐 SMARTBILL SAFENET INTEGRATION - COOL BITS SRL")
    print("=" * 80)

    # Inițializează integrarea SafeNet
    safenet_integration = SmartBillSafeNetIntegration()

    # Afișează statusul SafeNet
    status = safenet_integration.get_safenet_status()
    print(
        f"🔐 SafeNet Status: {'✅ Connected' if status['safenet_status']['connected'] else '❌ Not Connected'}"
    )
    print(
        f"📜 Certificates: {'✅ Available' if status['safenet_status']['certificates_available'] else '❌ Not Available'}"
    )

    if status["safenet_status"]["error_message"]:
        print(f"⚠️ Error: {status['safenet_status']['error_message']}")

    # Generează raport SafeNet
    report = safenet_integration.generate_safenet_report()
    print(f"📊 SafeNet Report: {report['summary']['total_signatures']} signatures")

    print("=" * 80)
    print("🎯 SmartBill SafeNet Integration ready!")
    print("=" * 80)


if __name__ == "__main__":
    main()
