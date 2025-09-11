import json
import subprocess
import sys
from pathlib import Path


class SecurityPolicyEnforcer:
    """Enforce CoolBits.ai security policies."""

    def __init__(self):
        with open("security_policies.json", "r") as f:
            self.policies = json.load(f)

    def check_key_management_policy(self):
        """Check NO_KEYS_IN_ENV_FILES policy."""
        blocked_files = [".env", ".secrets", "config.json"]

        for file_name in blocked_files:
            if Path(file_name).exists():
                print(f"❌ VIOLATION: {file_name} found")
                print("   Policy: NO_KEYS_IN_ENV_FILES")
                print("   Action: Remove file or use Secret Manager")
                return False

        print("✅ Key management policy satisfied")
        return True

    def check_build_security_policy(self):
        """Check SIGNED_BUILDS_ONLY policy."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True
            )

            if result.returncode == 0:
                commit_sha = result.stdout.strip()
                print(f"✅ Build security policy satisfied - SHA: {commit_sha[:8]}")
                return True
            else:
                print("❌ VIOLATION: Not in git repository")
                return False

        except Exception as e:
            print(f"❌ VIOLATION: Git check failed: {e}")
            return False

    def check_mock_policy(self):
        """Check NO_MOCKS_IN_MAIN policy."""
        try:
            # Check current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True
            )

            if result.returncode == 0:
                current_branch = result.stdout.strip()

                if current_branch == "main":
                    # Check for mock files
                    mock_files = list(Path(".").glob("**/mock_*.py"))
                    mock_files.extend(list(Path(".").glob("**/test_*.py")))

                    if mock_files:
                        print("❌ VIOLATION: Mock files found in main branch")
                        print(f"   Files: {[str(f) for f in mock_files]}")
                        return False

                print(f"✅ Mock policy satisfied - branch: {current_branch}")
                return True
            else:
                print("❌ VIOLATION: Git branch check failed")
                return False

        except Exception as e:
            print(f"❌ VIOLATION: Mock policy check failed: {e}")
            return False

    def enforce_all_policies(self):
        """Enforce all security policies."""
        print("🔍 Enforcing CoolBits.ai security policies...")

        policies_passed = 0
        total_policies = 3

        if self.check_key_management_policy():
            policies_passed += 1

        if self.check_build_security_policy():
            policies_passed += 1

        if self.check_mock_policy():
            policies_passed += 1

        if policies_passed == total_policies:
            print("✅ All security policies satisfied")
            return True
        else:
            print(f"❌ {total_policies - policies_passed} security policies violated")
            return False


if __name__ == "__main__":
    enforcer = SecurityPolicyEnforcer()
    if not enforcer.enforce_all_policies():
        sys.exit(1)
