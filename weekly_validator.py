# CoolBits.ai Weekly Validation Routine
# ====================================

import time
import subprocess
import requests
import json
from datetime import datetime


class WeeklyValidator:
    """Weekly validation routine for CoolBits.ai infrastructure."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "week": datetime.now().strftime("%Y-W%U"),
            "tests": {},
            "overall_status": "unknown",
        }
        self.base_url = "http://localhost:8501"  # Adjust as needed

    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test result."""
        self.results["tests"][test_name] = {
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        print(f"{'✅' if status == 'PASS' else '❌'} {test_name}: {status}")
        if details:
            print(f"   {details}")

    def test_ci_pipeline(self):
        """Test CI pipeline functionality."""
        print("\n🔧 Testing CI Pipeline...")

        try:
            # Test linting
            result = subprocess.run(
                ["python", "-m", "black", "--check", "."],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.log_result("CI_Linting", "PASS", "Code formatting is correct")
            else:
                self.log_result(
                    "CI_Linting", "FAIL", f"Formatting issues: {result.stdout[:100]}"
                )

            # Test type checking
            result = subprocess.run(
                ["python", "-m", "mypy", "."],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.log_result("CI_TypeCheck", "PASS", "Type checking passed")
            else:
                self.log_result(
                    "CI_TypeCheck", "FAIL", f"Type errors: {result.stderr[:100]}"
                )

            # Test unit tests
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                self.log_result("CI_UnitTests", "PASS", "All unit tests passed")
            else:
                self.log_result(
                    "CI_UnitTests", "FAIL", f"Test failures: {result.stdout[:100]}"
                )

        except subprocess.TimeoutExpired:
            self.log_result("CI_Pipeline", "TIMEOUT", "CI tests timed out")
        except Exception as e:
            self.log_result("CI_Pipeline", "ERROR", f"CI test failed: {e}")

    def test_canary_deployment(self):
        """Test canary deployment and rollback."""
        print("\n🚀 Testing Canary Deployment...")

        try:
            from canary_deployment import CanaryDeployment, DeploymentConfig

            # Create test configuration
            config = DeploymentConfig(
                staging_url="http://localhost:8501",
                production_url="http://localhost:8502",
            )

            canary = CanaryDeployment(config)

            # Test deployment methods exist
            if hasattr(canary, "run_canary_deployment") and hasattr(
                canary, "deploy_to_staging"
            ):
                self.log_result(
                    "Canary_Deployment", "PASS", "Canary deployment methods available"
                )
            else:
                self.log_result(
                    "Canary_Deployment", "FAIL", "Missing canary deployment methods"
                )

            # Test rollback manager
            from rollback_manager import RollbackManager, RollbackConfig

            rollback_config = RollbackConfig(production_url="http://localhost:8501")
            rollback_manager = RollbackManager(rollback_config)

            if hasattr(rollback_manager, "emergency_rollback") and hasattr(
                rollback_manager, "planned_rollback"
            ):
                self.log_result("Canary_Rollback", "PASS", "Rollback methods available")
            else:
                self.log_result("Canary_Rollback", "FAIL", "Missing rollback methods")

        except Exception as e:
            self.log_result("Canary_Deployment", "ERROR", f"Canary test failed: {e}")

    def test_rbac_hmac_security(self):
        """Test RBAC and HMAC security."""
        print("\n🔐 Testing RBAC/HMAC Security...")

        try:
            from rbac_manager import rbac_manager, Role, Permission

            # Test RBAC functionality
            test_user = rbac_manager.create_user(
                username=f"weekly_test_{int(time.time())}",
                email="weekly@test.com",
                roles=[Role.VIEWER],
            )

            # Test permissions
            has_admin = rbac_manager.has_permission(
                test_user.id, Permission.ADMIN_ACCESS
            )
            has_view = rbac_manager.has_permission(test_user.id, Permission.DATA_VIEW)

            if not has_admin and has_view:
                self.log_result(
                    "RBAC_Permissions", "PASS", "Role-based permissions working"
                )
            else:
                self.log_result(
                    "RBAC_Permissions", "FAIL", "Permission logic incorrect"
                )

            # Test HMAC
            method = "POST"
            path = "/api/test"
            body = "{}"

            signature_data = rbac_manager.generate_hmac_signature(method, path, body)
            is_valid = rbac_manager.verify_hmac_signature(
                method,
                path,
                body,
                signature_data["signature"],
                signature_data["timestamp"],
                signature_data["nonce"],
            )

            if is_valid:
                self.log_result(
                    "HMAC_Signatures",
                    "PASS",
                    "HMAC signature generation/verification working",
                )
            else:
                self.log_result(
                    "HMAC_Signatures", "FAIL", "HMAC signature verification failed"
                )

            # Test JWT
            token = rbac_manager.generate_jwt_token(test_user.id)
            payload = rbac_manager.verify_jwt_token(token)

            if payload and payload.get("user_id") == test_user.id:
                self.log_result(
                    "JWT_Tokens", "PASS", "JWT token generation/verification working"
                )
            else:
                self.log_result("JWT_Tokens", "FAIL", "JWT token verification failed")

        except Exception as e:
            self.log_result("RBAC_HMAC_Security", "ERROR", f"Security test failed: {e}")

    def test_hmac_key_management(self):
        """Test HMAC key management and rotation."""
        print("\n🔑 Testing HMAC Key Management...")

        try:
            from hmac_key_manager import HMACKeyManager

            key_manager = HMACKeyManager()

            # Test key generation
            new_key = key_manager.generate_key(
                name=f"weekly-test-{int(time.time())}",
                description="Weekly validation test key",
                expires_in_days=1,
            )

            if new_key and new_key.get("key_id"):
                self.log_result(
                    "HMAC_KeyGeneration", "PASS", f"Key generated: {new_key['key_id']}"
                )

                # Test key validation
                is_valid = key_manager.is_key_valid(new_key["key_id"])
                if is_valid:
                    self.log_result(
                        "HMAC_KeyValidation", "PASS", "Key validation working"
                    )
                else:
                    self.log_result(
                        "HMAC_KeyValidation", "FAIL", "Key validation failed"
                    )

                # Test key revocation
                revoked = key_manager.revoke_key(new_key["key_id"])
                if revoked:
                    self.log_result(
                        "HMAC_KeyRevocation", "PASS", "Key revocation working"
                    )
                else:
                    self.log_result(
                        "HMAC_KeyRevocation", "FAIL", "Key revocation failed"
                    )

                # Cleanup expired keys
                removed_count = key_manager.cleanup_expired_keys()
                self.log_result(
                    "HMAC_KeyCleanup",
                    "PASS",
                    f"Cleaned up {removed_count} expired keys",
                )

            else:
                self.log_result("HMAC_KeyGeneration", "FAIL", "Key generation failed")

        except Exception as e:
            self.log_result(
                "HMAC_KeyManagement", "ERROR", f"Key management test failed: {e}"
            )

    def test_uptime_monitoring(self):
        """Test uptime monitoring and alerting."""
        print("\n📊 Testing Uptime Monitoring...")

        try:
            # Test basic health endpoint
            response = requests.get(f"{self.base_url}/api/health", timeout=10)

            if response.status_code == 200:
                self.log_result(
                    "Uptime_HealthCheck",
                    "PASS",
                    f"Health endpoint responding: {response.status_code}",
                )

                # Test multiple health checks
                successful_checks = 0
                total_checks = 5

                for i in range(total_checks):
                    try:
                        resp = requests.get(f"{self.base_url}/api/health", timeout=5)
                        if resp.status_code == 200:
                            successful_checks += 1
                    except:
                        pass
                    time.sleep(1)

                uptime_percent = (successful_checks / total_checks) * 100

                if uptime_percent >= 80:  # 80% uptime threshold
                    self.log_result(
                        "Uptime_Reliability", "PASS", f"Uptime: {uptime_percent:.1f}%"
                    )
                else:
                    self.log_result(
                        "Uptime_Reliability",
                        "FAIL",
                        f"Low uptime: {uptime_percent:.1f}%",
                    )

            else:
                self.log_result(
                    "Uptime_HealthCheck",
                    "FAIL",
                    f"Health endpoint failed: {response.status_code}",
                )

            # Test metrics endpoint
            try:
                metrics_response = requests.get(
                    f"{self.base_url}/api/metrics", timeout=10
                )
                if metrics_response.status_code == 200:
                    self.log_result(
                        "Uptime_Metrics", "PASS", "Metrics endpoint responding"
                    )
                else:
                    self.log_result(
                        "Uptime_Metrics",
                        "FAIL",
                        f"Metrics endpoint failed: {metrics_response.status_code}",
                    )
            except:
                self.log_result(
                    "Uptime_Metrics", "FAIL", "Metrics endpoint unreachable"
                )

        except Exception as e:
            self.log_result(
                "Uptime_Monitoring", "ERROR", f"Uptime monitoring test failed: {e}"
            )

    def test_dashboard_api_connectivity(self):
        """Test dashboard API connectivity."""
        print("\n📈 Testing Dashboard API Connectivity...")

        endpoints = ["/api/health", "/api/metrics", "/api/status"]

        successful_endpoints = 0

        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    successful_endpoints += 1
                    print(f"   ✅ {endpoint}: {response.status_code}")
                else:
                    print(f"   ❌ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint}: {e}")

        if successful_endpoints == len(endpoints):
            self.log_result(
                "Dashboard_API_Connectivity",
                "PASS",
                f"All {len(endpoints)} endpoints responding",
            )
        else:
            self.log_result(
                "Dashboard_API_Connectivity",
                "FAIL",
                f"Only {successful_endpoints}/{len(endpoints)} endpoints responding",
            )

    def generate_report(self):
        """Generate weekly validation report."""
        print("\n📋 Generating Weekly Validation Report...")

        # Calculate overall status
        test_results = list(self.results["tests"].values())
        pass_count = sum(1 for test in test_results if test["status"] == "PASS")
        total_count = len(test_results)

        if pass_count == total_count:
            self.results["overall_status"] = "HEALTHY"
        elif pass_count >= total_count * 0.8:  # 80% pass rate
            self.results["overall_status"] = "WARNING"
        else:
            self.results["overall_status"] = "CRITICAL"

        # Save report
        report_file = (
            f"weekly_validation_report_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"📄 Report saved: {report_file}")

        # Print summary
        print("\n🎯 Weekly Validation Summary:")
        print(f"   Overall Status: {self.results['overall_status']}")
        print(f"   Tests Passed: {pass_count}/{total_count}")
        print(f"   Pass Rate: {(pass_count / total_count) * 100:.1f}%")

        return self.results

    def run_all_tests(self):
        """Run all weekly validation tests."""
        print("🚀 CoolBits.ai Weekly Validation Routine")
        print("=" * 50)
        print(f"📅 Week: {self.results['week']}")
        print(f"🕐 Started: {self.results['timestamp']}")

        # Run all tests
        self.test_ci_pipeline()
        self.test_canary_deployment()
        self.test_rbac_hmac_security()
        self.test_hmac_key_management()
        self.test_uptime_monitoring()
        self.test_dashboard_api_connectivity()

        # Generate report
        return self.generate_report()


def schedule_weekly_validation():
    """Schedule weekly validation to run automatically."""
    print("\n⏰ Setting up Weekly Validation Schedule...")

    # Create a simple scheduler script
    scheduler_script = '''
import schedule
import time
from weekly_validator import WeeklyValidator

def run_weekly_validation():
    """Run weekly validation routine."""
    validator = WeeklyValidator()
    validator.run_all_tests()

# Schedule weekly validation every Monday at 9 AM
schedule.every().monday.at("09:00").do(run_weekly_validation)

print("📅 Weekly validation scheduled for every Monday at 9:00 AM")
print("🔄 Starting scheduler...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
'''

    with open("weekly_scheduler.py", "w") as f:
        f.write(scheduler_script)

    print("✅ Weekly scheduler created: weekly_scheduler.py")
    print("📝 To run: python weekly_scheduler.py")
    print("💡 Consider setting up as a Windows service or cron job")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="CoolBits.ai Weekly Validation Routine"
    )
    parser.add_argument(
        "--schedule", action="store_true", help="Setup weekly scheduling"
    )
    parser.add_argument("--run", action="store_true", help="Run validation now")

    args = parser.parse_args()

    if args.schedule:
        schedule_weekly_validation()
    elif args.run:
        validator = WeeklyValidator()
        validator.run_all_tests()
    else:
        print("Usage:")
        print("  python weekly_validator.py --run      # Run validation now")
        print("  python weekly_validator.py --schedule # Setup weekly scheduling")
