#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartBill Complete System - COOL BITS SRL
Sistem complet de facturare cu integrare SafeNet și delegare agenți
"""

import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Funcția principală SmartBill"""
    print("=" * 80)
    print("🧾 SMARTBILL - SOLUȚIA DE FACTURARE COOL BITS SRL")
    print("=" * 80)
    print("🔐 Integrare SafeNet pentru semnarea digitală")
    print("🤖 Delegare către agenții interni: ogpt01, ogpt02, ogpt05")
    print("🔗 Integrare oCursor și GeminiCLI pentru workflow seamless")
    print("🌐 API Server cu autentificare SafeNet")
    print("=" * 80)

    # Afișează componentele sistemului
    print("📋 COMPONENTELE SMARTBILL:")
    print("=" * 80)

    components = {
        "1. SmartBill Core System": {
            "file": "smartbill_core_system.py",
            "description": "Sistemul principal de facturare cu gestionare facturi",
            "features": [
                "Creare facturi",
                "Gestionare clienți",
                "Calculare TVA",
                "Stocare persistentă",
            ],
        },
        "2. SafeNet Integration": {
            "file": "smartbill_safenet_integration.py",
            "description": "Integrare SafeNet pentru semnarea digitală",
            "features": [
                "Semnare digitală facturi",
                "Verificare semnături",
                "Gestionare certificate",
                "Audit trail",
            ],
        },
        "3. Agent Delegation": {
            "file": "smartbill_agent_delegation.py",
            "description": "Delegare operațiuni către agenții interni",
            "features": [
                "Delegare către ogpt01 (Frontend)",
                "Delegare către ogpt02 (Backend)",
                "Delegare către ogpt05 (Data)",
                "Monitorizare operațiuni",
            ],
        },
        "4. oCursor & GeminiCLI Integration": {
            "file": "smartbill_cursor_gemini_integration.py",
            "description": "Integrare seamless cu oCursor și GeminiCLI",
            "features": [
                "Workflow-uri integrate",
                "Operațiuni oCursor",
                "Operațiuni GeminiCLI",
                "Automatizare completă",
            ],
        },
        "5. API Server": {
            "file": "smartbill_api_server.py",
            "description": "API endpoints cu autentificare SafeNet",
            "features": [
                "REST API complet",
                "Autentificare SafeNet",
                "Endpoint-uri pentru toate operațiunile",
                "Documentație API",
            ],
        },
    }

    for component_name, component_info in components.items():
        print(f"\n{component_name}:")
        print(f"  📁 File: {component_info['file']}")
        print(f"  📝 Description: {component_info['description']}")
        print("  ⚡ Features:")
        for feature in component_info["features"]:
            print(f"    • {feature}")

    print("\n" + "=" * 80)
    print("🚀 DEMO SMARTBILL SYSTEM")
    print("=" * 80)

    # Demo sistemul
    try:
        # Import și inițializează componentele
        from smartbill_core_system import SmartBillCore
        from smartbill_safenet_integration import SmartBillSafeNetIntegration
        from smartbill_agent_delegation import SmartBillAgentDelegation
        from smartbill_cursor_gemini_integration import SmartBillCursorGeminiIntegration

        print("🔧 Initializing SmartBill components...")

        # Inițializează sistemul principal
        smartbill = SmartBillCore()
        print("✅ SmartBill Core System initialized")

        # Inițializează integrarea SafeNet
        safenet = SmartBillSafeNetIntegration()
        print("✅ SafeNet Integration initialized")

        # Inițializează delegarea agenților
        agents = SmartBillAgentDelegation()
        print("✅ Agent Delegation System initialized")

        # Inițializează integrarea oCursor & GeminiCLI
        integration = SmartBillCursorGeminiIntegration()
        print("✅ oCursor & GeminiCLI Integration initialized")

        print("\n📊 SYSTEM STATUS:")
        print("=" * 80)

        # Afișează statusul sistemului
        print(f"🏢 Company: {smartbill.company}")
        print(f"🆔 CUI: {smartbill.company_cui}")
        print(f"📄 Total Invoices: {len(smartbill.invoices)}")
        print(f"🤖 Available Agents: {len(agents.delegated_agents)}")
        print(f"🔄 Available Workflows: {len(integration.integrated_workflows)}")

        # Status SafeNet
        safenet_status = safenet.get_safenet_status()
        print(
            f"🔐 SafeNet Status: {'✅ Connected' if safenet_status['safenet_status']['connected'] else '❌ Not Connected'}"
        )

        # Status integrare
        integration_status = integration.get_integration_status()
        print(
            f"🎯 oCursor Status: {'✅ Active' if integration_status['cursor_status']['status'] == 'active' else '❌ Inactive'}"
        )
        print(
            f"🤖 GeminiCLI Status: {'✅ Active' if integration_status['gemini_status']['status'] == 'active' else '❌ Inactive'}"
        )

        print("\n🧪 DEMO OPERATIONS:")
        print("=" * 80)

        # Demo creare factură
        print("1. Creating demo invoice...")
        client_data = {
            "name": "Demo Client SRL",
            "cui": "12345678",
            "address": "Strada Demo, nr. 1, București",
            "notes": "Client pentru demonstrație",
        }

        items = [
            {
                "description": "Servicii de dezvoltare software",
                "quantity": 5,
                "unit_price": 1000.0,
                "vat_rate": 19.0,
            }
        ]

        invoice = smartbill.create_invoice(client_data, items)
        print(f"✅ Invoice created: {invoice.invoice_number}")

        # Demo delegare către agent
        print("2. Delegating to ogpt01...")
        result = agents.delegate_operation(invoice.id, "invoice_creation", "ogpt01")
        if result:
            print(f"✅ Delegation successful: {result['message']}")

        # Demo workflow integrat
        print("3. Executing integrated workflow...")
        workflow_result = integration.execute_integrated_workflow(
            "invoice_creation_workflow", {"invoice_number": invoice.invoice_number}
        )
        if workflow_result:
            print(f"✅ Workflow completed: {workflow_result['overall_status']}")

        print("\n📊 FINAL REPORTS:")
        print("=" * 80)

        # Generează rapoarte finale
        invoice_report = smartbill.generate_invoice_report()
        print(
            f"📄 Invoice Report: {invoice_report['summary']['total_invoices']} invoices"
        )

        delegation_report = agents.get_delegation_report()
        print(
            f"🤖 Delegation Report: {delegation_report['summary']['total_delegations']} delegations"
        )

        integration_report = integration.generate_integration_report()
        print(
            f"🔗 Integration Report: {integration_report['summary']['total_operations']} operations"
        )

        print("\n" + "=" * 80)
        print("🎯 SMARTBILL SYSTEM READY FOR PRODUCTION!")
        print("=" * 80)
        print("🌐 To start API server: python smartbill_api_server.py")
        print("📚 API Documentation: http://localhost:5002/api/smartbill/status")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("💡 Make sure all SmartBill components are properly installed")


if __name__ == "__main__":
    main()
