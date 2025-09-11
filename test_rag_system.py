#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai RAG System Test Suite
CEO: Andrei - andrei@coolbits.ro
Managed by: oCursor (Local Development)

Test suite for RAG system with Vertex AI Vector Search integration.
"""

import sys
import json
import time
from datetime import datetime
from coolbits_rag_system import CoolBitsRAG


class RAGTestSuite:
    """Test suite for CoolBits.ai RAG system"""

    def __init__(self):
        self.rag = CoolBitsRAG()
        self.test_results = []

    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        print(f"\n🧪 Running test: {test_name}")
        print("-" * 50)

        start_time = time.time()
        try:
            result = test_func()
            end_time = time.time()

            test_result = {
                "name": test_name,
                "status": "PASS" if result.get("success", False) else "FAIL",
                "duration": end_time - start_time,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }

            if test_result["status"] == "PASS":
                print(f"✅ {test_name}: PASSED ({test_result['duration']:.2f}s)")
            else:
                print(f"❌ {test_name}: FAILED ({test_result['duration']:.2f}s)")
                if "error" in result:
                    print(f"   Error: {result['error']}")

            self.test_results.append(test_result)
            return test_result

        except Exception as e:
            end_time = time.time()
            test_result = {
                "name": test_name,
                "status": "ERROR",
                "duration": end_time - start_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

            print(f"💥 {test_name}: ERROR ({test_result['duration']:.2f}s)")
            print(f"   Exception: {e}")

            self.test_results.append(test_result)
            return test_result

    def test_connection(self):
        """Test connection to CoolBits.ai and Vertex AI"""
        return self.rag.test_connection()

    def test_organizational_search(self):
        """Test organizational knowledge search"""
        query = "What are the main departments in CoolBits.ai?"
        return self.rag.search_organizational_knowledge(query)

    def test_role_specific_search(self):
        """Test role-specific knowledge search"""
        query = "What are my responsibilities as CTO?"
        return self.rag.get_role_specific_knowledge("cto", query)

    def test_panel_specific_search(self):
        """Test panel-specific knowledge search"""
        query = "What features are available in the developer panel?"
        return self.rag.get_panel_specific_knowledge("dev", query)

    def test_ceo_god_mode(self):
        """Test CEO God Mode functionality"""
        user_context = {"role": "ceo", "panel": "andrei", "access_level": "GOD_MODE"}
        query = "Show me the complete system status"
        return self.rag.generate_rag_response(query, user_context)

    def test_business_panel(self):
        """Test Business Panel functionality"""
        user_context = {
            "role": "cmo",
            "panel": "business",
            "access_level": "MARKETING_LEAD",
        }
        query = "What marketing strategies should I implement?"
        return self.rag.generate_rag_response(query, user_context)

    def test_developer_panel(self):
        """Test Developer Panel functionality"""
        user_context = {
            "role": "backend",
            "panel": "dev",
            "access_level": "ENGINEERING",
        }
        query = "How do I integrate with the API?"
        return self.rag.generate_rag_response(query, user_context)

    def test_vector_search(self):
        """Test Vector Search functionality"""
        query = "artificial intelligence machine learning"
        return self.rag.find_neighbors(query, num_neighbors=5)

    def test_recommendations(self):
        """Test recommendation generation"""
        user_context = {
            "role": "pm",
            "panel": "business",
            "access_level": "PRODUCT_MANAGEMENT",
        }
        query = "What should I focus on next?"
        result = self.rag.generate_rag_response(query, user_context)

        if result.get("success") and "recommendations" in result:
            return {
                "success": True,
                "recommendations": result["recommendations"],
                "count": len(result["recommendations"]),
            }
        else:
            return {"success": False, "error": "Failed to generate recommendations"}

    def run_all_tests(self):
        """Run all tests in the suite"""
        print("🚀 CoolBits.ai RAG System Test Suite")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Define test cases
        test_cases = [
            ("Connection Test", self.test_connection),
            ("Organizational Search", self.test_organizational_search),
            ("Role-Specific Search", self.test_role_specific_search),
            ("Panel-Specific Search", self.test_panel_specific_search),
            ("CEO God Mode", self.test_ceo_god_mode),
            ("Business Panel", self.test_business_panel),
            ("Developer Panel", self.test_developer_panel),
            ("Vector Search", self.test_vector_search),
            ("Recommendations", self.test_recommendations),
        ]

        # Run all tests
        for test_name, test_func in test_cases:
            self.run_test(test_name, test_func)

        # Generate summary
        self.generate_summary()

        # Save results
        self.save_results()

    def generate_summary(self):
        """Generate test summary"""
        print("\n📊 Test Summary")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print(f"Errors: {error_tests} ({error_tests/total_tests*100:.1f}%)")

        total_duration = sum(r["duration"] for r in self.test_results)
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Average Duration: {total_duration/total_tests:.2f}s")

        # Show failed tests
        if failed_tests > 0 or error_tests > 0:
            print("\n❌ Failed/Error Tests:")
            for result in self.test_results:
                if result["status"] in ["FAIL", "ERROR"]:
                    print(f"  • {result['name']}: {result['status']}")
                    if "error" in result:
                        print(f"    Error: {result['error']}")

        # Overall status
        if failed_tests == 0 and error_tests == 0:
            print("\n🎉 All tests passed! RAG system is working correctly.")
        else:
            print(
                f"\n⚠️  {failed_tests + error_tests} test(s) failed. Please review the errors above."
            )

    def save_results(self):
        """Save test results to file"""
        results_file = (
            f"rag_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "test_suite": "CoolBits.ai RAG System",
                        "timestamp": datetime.now().isoformat(),
                        "results": self.test_results,
                        "summary": {
                            "total_tests": len(self.test_results),
                            "passed": len(
                                [r for r in self.test_results if r["status"] == "PASS"]
                            ),
                            "failed": len(
                                [r for r in self.test_results if r["status"] == "FAIL"]
                            ),
                            "errors": len(
                                [r for r in self.test_results if r["status"] == "ERROR"]
                            ),
                        },
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"\n💾 Test results saved to: {results_file}")

        except Exception as e:
            print(f"\n❌ Failed to save test results: {e}")


def main():
    """Main function"""
    try:
        test_suite = RAGTestSuite()
        test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
