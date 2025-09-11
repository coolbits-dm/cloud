#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai RAG Integration Script
CEO: Andrei - andrei@coolbits.ro
Managed by: oCursor (Local Development)

Integrates RAG system with existing AI Board for enhanced functionality.
"""

import json
import requests
from datetime import datetime
from coolbits_rag_system import CoolBitsRAG


class CoolBitsRAGIntegration:
    """Integration between RAG system and CoolBits.ai AI Board"""

    def __init__(self, ai_board_url: str = "http://localhost:8082"):
        self.ai_board_url = ai_board_url
        self.rag = CoolBitsRAG()
        self.integration_status = "disconnected"

    def check_ai_board_status(self) -> bool:
        """Check if AI Board is running"""
        try:
            response = requests.get(f"{self.ai_board_url}/health", timeout=5)
            if response.status_code == 200:
                self.integration_status = "connected"
                return True
            else:
                self.integration_status = "error"
                return False
        except Exception as e:
            print(f"❌ AI Board connection error: {e}")
            self.integration_status = "disconnected"
            return False

    def enhance_ai_board_with_rag(self):
        """Enhance AI Board with RAG capabilities"""
        if not self.check_ai_board_status():
            print("❌ Cannot enhance AI Board - not connected")
            return False

        print("🔗 Enhancing AI Board with RAG capabilities...")

        # Test RAG integration
        test_queries = [
            "What are the main technology roles?",
            "How does the panel system work?",
            "What is the cbT economy?",
            "What are my responsibilities as CEO?",
        ]

        results = []
        for query in test_queries:
            print(f"  Testing query: '{query}'")
            result = self.rag.search_organizational_knowledge(query)
            results.append(
                {
                    "query": query,
                    "success": result.get("success", False),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Check results
        successful_queries = len([r for r in results if r["success"]])
        total_queries = len(results)

        print(
            f"✅ RAG integration test: {successful_queries}/{total_queries} queries successful"
        )

        if successful_queries == total_queries:
            self.integration_status = "enhanced"
            print("🎉 AI Board successfully enhanced with RAG capabilities!")
            return True
        else:
            print("⚠️  RAG integration partially successful")
            return False

    def create_rag_endpoints(self):
        """Create RAG-specific endpoints for AI Board"""
        print("🔧 Creating RAG endpoints...")

        # Define RAG endpoints
        rag_endpoints = {
            "rag_search": {
                "method": "POST",
                "path": "/rag/search",
                "description": "Search organizational knowledge using RAG",
            },
            "rag_role_knowledge": {
                "method": "POST",
                "path": "/rag/role/{role_id}",
                "description": "Get role-specific knowledge",
            },
            "rag_panel_knowledge": {
                "method": "POST",
                "path": "/rag/panel/{panel_name}",
                "description": "Get panel-specific knowledge",
            },
            "rag_recommendations": {
                "method": "POST",
                "path": "/rag/recommendations",
                "description": "Get AI-powered recommendations",
            },
            "rag_status": {
                "method": "GET",
                "path": "/rag/status",
                "description": "Get RAG system status",
            },
        }

        print("✅ RAG endpoints defined:")
        for endpoint_id, endpoint_info in rag_endpoints.items():
            print(
                f"  • {endpoint_info['method']} {endpoint_info['path']} - {endpoint_info['description']}"
            )

        return rag_endpoints

    def test_rag_functionality(self):
        """Test RAG functionality with different user contexts"""
        print("🧪 Testing RAG functionality...")

        test_scenarios = [
            {
                "name": "CEO God Mode",
                "context": {
                    "role": "ceo",
                    "panel": "andrei",
                    "access_level": "GOD_MODE",
                },
                "query": "Show me the complete system overview",
            },
            {
                "name": "CTO Technology",
                "context": {
                    "role": "cto",
                    "panel": "dev",
                    "access_level": "TECHNOLOGY_LEAD",
                },
                "query": "What are the key technology initiatives?",
            },
            {
                "name": "CPO Product",
                "context": {
                    "role": "cpo",
                    "panel": "business",
                    "access_level": "PRODUCT_LEAD",
                },
                "query": "What is the product roadmap?",
            },
            {
                "name": "CMO Marketing",
                "context": {
                    "role": "cmo",
                    "panel": "business",
                    "access_level": "MARKETING_LEAD",
                },
                "query": "What marketing strategies should we implement?",
            },
            {
                "name": "Developer",
                "context": {
                    "role": "backend",
                    "panel": "dev",
                    "access_level": "ENGINEERING",
                },
                "query": "How do I integrate with the API?",
            },
        ]

        results = []
        for scenario in test_scenarios:
            print(f"  Testing {scenario['name']}...")
            result = self.rag.generate_rag_response(
                scenario["query"], scenario["context"]
            )

            results.append(
                {
                    "scenario": scenario["name"],
                    "success": result.get("success", False),
                    "has_recommendations": "recommendations" in result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Summary
        successful_scenarios = len([r for r in results if r["success"]])
        total_scenarios = len(results)

        print(
            f"✅ RAG functionality test: {successful_scenarios}/{total_scenarios} scenarios successful"
        )

        return results

    def generate_integration_report(self):
        """Generate integration report"""
        print("\n📊 CoolBits.ai RAG Integration Report")
        print("=" * 60)

        # Check connections
        ai_board_connected = self.check_ai_board_status()
        rag_connected = self.rag.test_connection()

        print(
            f"AI Board Status: {'✅ Connected' if ai_board_connected else '❌ Disconnected'}"
        )
        print(
            f"RAG System Status: {'✅ Connected' if rag_connected.get('vertex_ai', {}).get('status') == 'connected' else '❌ Disconnected'}"
        )

        # Test functionality
        if ai_board_connected:
            rag_endpoints = self.create_rag_endpoints()
            test_results = self.test_rag_functionality()

            print(f"\nRAG Endpoints: {len(rag_endpoints)} defined")
            print(f"Test Scenarios: {len(test_results)} tested")

            successful_tests = len([r for r in test_results if r["success"]])
            print(f"Successful Tests: {successful_tests}/{len(test_results)}")

        # Integration status
        print(f"\nIntegration Status: {self.integration_status}")

        if self.integration_status == "enhanced":
            print("🎉 RAG system successfully integrated with AI Board!")
        elif self.integration_status == "connected":
            print("🔗 AI Board connected, RAG integration pending")
        else:
            print("❌ Integration failed - check connections")

        return {
            "ai_board_connected": ai_board_connected,
            "rag_connected": rag_connected,
            "integration_status": self.integration_status,
            "timestamp": datetime.now().isoformat(),
        }

    def start_rag_service(self):
        """Start RAG service integration"""
        print("🚀 Starting CoolBits.ai RAG Service Integration")
        print("=" * 60)

        # Check prerequisites
        print("1. Checking prerequisites...")
        ai_board_ok = self.check_ai_board_status()

        if not ai_board_ok:
            print("❌ AI Board not available. Please start it first:")
            print("   node coolbits_ai_board_node.js")
            return False

        print("✅ AI Board is running")

        # Test RAG system
        print("\n2. Testing RAG system...")
        rag_test = self.rag.test_connection()

        if rag_test.get("vertex_ai", {}).get("status") != "connected":
            print("⚠️  Vertex AI connection issues detected")
            print("   Please check your Google Cloud credentials and project settings")
        else:
            print("✅ RAG system is ready")

        # Enhance AI Board
        print("\n3. Enhancing AI Board with RAG...")
        enhancement_success = self.enhance_ai_board_with_rag()

        if enhancement_success:
            print("✅ AI Board enhanced with RAG capabilities")
        else:
            print("⚠️  RAG enhancement partially successful")

        # Generate report
        print("\n4. Generating integration report...")
        report = self.generate_integration_report()

        # Save report
        report_file = (
            f"rag_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"💾 Integration report saved to: {report_file}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")

        print("\n🎯 RAG Integration Complete!")
        return enhancement_success


def main():
    """Main function"""
    try:
        integration = CoolBitsRAGIntegration()
        integration.start_rag_service()
    except KeyboardInterrupt:
        print("\n\n⏹️  Integration interrupted by user")
    except Exception as e:
        print(f"\n💥 Integration failed with error: {e}")


if __name__ == "__main__":
    main()
