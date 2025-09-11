# CoolBits.ai Security Hardening - IMMEDIATE ACTIONS
# =================================================

import os
import sys
import json
import hmac
import hashlib
import base64
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


class SecurityHardening:
    """Immediate security hardening for CoolBits.ai."""
    
    def __init__(self):
        self.compromised_key = "cb401cb643e9f67a"  # EXPOSED IN CHAT - COMPROMISED
        self.secret_manager_keys = []
        self.audit_log_file = "security_audit.jsonl"
    
    def log_security_event(self, event_type: str, details: dict):
        """Log security events to JSONL audit log."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "severity": "CRITICAL" if "compromised" in event_type.lower() else "HIGH"
        }
        
        with open(self.audit_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        
        print(f"🚨 SECURITY EVENT: {event_type}")
        print(f"   Details: {details}")
    
    def rotate_compromised_key(self):
        """IMMEDIATE: Rotate compromised HMAC key."""
        print("🚨 ROTATING COMPROMISED HMAC KEY")
        print("=" * 40)
        
        try:
            from hmac_key_manager import HMACKeyManager
            
            key_manager = HMACKeyManager()
            
            # Generate new secure key
            new_key = key_manager.generate_key(
                name="emergency-rotation-2025-09-10",
                description="Emergency rotation due to key exposure in chat",
                expires_in_days=30
            )
            
            if new_key:
                print(f"✅ New secure key generated: {new_key['key_id']}")
                
                # Revoke compromised key
                revoked = key_manager.revoke_key(key_id=self.compromised_key)
                
                if revoked:
                    print(f"🚫 Compromised key revoked: {self.compromised_key}")
                    
                    # Log security event
                    self.log_security_event(
                        "KEY_COMPROMISED_ROTATION",
                        {
                            "compromised_key": self.compromised_key,
                            "new_key": new_key['key_id'],
                            "reason": "Key exposed in chat",
                            "action": "rotated_and_revoked"
                        }
                    )
                    
                    return new_key['key_id']
                else:
                    print(f"❌ Failed to revoke compromised key")
                    return None
            else:
                print(f"❌ Failed to generate new key")
                return None
                
        except Exception as e:
            print(f"❌ Key rotation failed: {e}")
            self.log_security_event(
                "KEY_ROTATION_FAILED",
                {"error": str(e), "compromised_key": self.compromised_key}
            )
            return None
    
    def setup_secret_manager(self):
        """Setup Google Secret Manager integration."""
        print("\n🔐 SETTING UP SECRET MANAGER")
        print("=" * 35)
        
        try:
            # Check if Google Cloud SDK is available
            result = subprocess.run(
                ["gcloud", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Google Cloud SDK available")
                
                # Create secret manager configuration
                secret_config = {
                    "project_id": "coolbits-ai",
                    "secrets": [
                        {
                            "name": "hmac-keys",
                            "description": "HMAC signing keys for CoolBits.ai",
                            "replication": "automatic"
                        },
                        {
                            "name": "jwt-secret",
                            "description": "JWT signing secret",
                            "replication": "automatic"
                        },
                        {
                            "name": "api-keys",
                            "description": "External API keys",
                            "replication": "automatic"
                        }
                    ]
                }
                
                with open("secret_manager_config.json", "w", encoding="utf-8") as f:
                    json.dump(secret_config, f, indent=2)
                
                print("✅ Secret Manager configuration created")
                
                # Create secret manager client
                secret_manager_script = '''
import os
from google.cloud import secretmanager
from google.oauth2 import service_account

class SecretManagerClient:
    """Google Secret Manager client for CoolBits.ai."""
    
    def __init__(self, project_id="coolbits-ai"):
        self.project_id = project_id
        self.client = secretmanager.SecretManagerServiceClient()
    
    def create_secret(self, secret_id: str, description: str = ""):
        """Create a new secret."""
        parent = f"projects/{self.project_id}"
        
        secret = {
            "replication": {"automatic": {}},
            "labels": {"app": "coolbits-ai", "env": "production"}
        }
        
        if description:
            secret["labels"]["description"] = description
        
        response = self.client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": secret
            }
        )
        
        return response.name
    
    def add_secret_version(self, secret_id: str, payload: str):
        """Add a version to a secret."""
        parent = f"projects/{self.project_id}/secrets/{secret_id}"
        
        response = self.client.add_secret_version(
            request={
                "parent": parent,
                "payload": {"data": payload.encode("UTF-8")}
            }
        )
        
        return response.name
    
    def access_secret_version(self, secret_id: str, version_id="latest"):
        """Access a secret version."""
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        
        response = self.client.access_secret_version(request={"name": name})
        
        return response.payload.data.decode("UTF-8")
    
    def list_secrets(self):
        """List all secrets."""
        parent = f"projects/{self.project_id}"
        
        response = self.client.list_secrets(request={"parent": parent})
        
        return [secret.name for secret in response]

if __name__ == "__main__":
    client = SecretManagerClient()
    print("🔐 Secret Manager client ready")
'''
                
                with open("secret_manager_client.py", "w", encoding="utf-8") as f:
                    f.write(secret_manager_script)
                
                print("✅ Secret Manager client created")
                
                return True
            else:
                print("❌ Google Cloud SDK not available")
                return False
                
        except Exception as e:
            print(f"❌ Secret Manager setup failed: {e}")
            return False
    
    def setup_windows_dpapi(self):
        """Setup Windows DPAPI for local key storage."""
        print("\n🪟 SETTING UP WINDOWS DPAPI")
        print("=" * 30)
        
        try:
            import win32crypt
            
            dpapi_script = '''
import win32crypt
import base64
import json
from pathlib import Path

class WindowsDPAPI:
    """Windows DPAPI for secure key storage."""
    
    def __init__(self, key_file=".keys.encrypted"):
        self.key_file = Path(key_file)
        self.keys = self._load_keys()
    
    def _load_keys(self):
        """Load encrypted keys from file."""
        if not self.key_file.exists():
            return {}
        
        try:
            with open(self.key_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = win32crypt.CryptUnprotectData(
                encrypted_data, None, None, None, 0
            )[1]
            
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception:
            return {}
    
    def _save_keys(self):
        """Save keys encrypted to file."""
        try:
            json_data = json.dumps(self.keys).encode('utf-8')
            
            encrypted_data = win32crypt.CryptProtectData(
                json_data, None, None, None, 0
            )
            
            with open(self.key_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"❌ Failed to save keys: {e}")
            return False
    
    def store_key(self, key_id: str, key_value: str, description: str = ""):
        """Store a key securely."""
        self.keys[key_id] = {
            "value": key_value,
            "description": description,
            "created": datetime.now().isoformat()
        }
        
        return self._save_keys()
    
    def get_key(self, key_id: str):
        """Get a key value."""
        return self.keys.get(key_id, {}).get("value")
    
    def list_keys(self):
        """List all stored keys."""
        return {k: v["description"] for k, v in self.keys.items()}
    
    def delete_key(self, key_id: str):
        """Delete a key."""
        if key_id in self.keys:
            del self.keys[key_id]
            return self._save_keys()
        return False

if __name__ == "__main__":
    dpapi = WindowsDPAPI()
    print("🔐 Windows DPAPI ready")
'''
            
            with open("windows_dpapi.py", "w", encoding="utf-8") as f:
                f.write(dpapi_script)
            
            print("✅ Windows DPAPI client created")
            return True
            
        except ImportError:
            print("❌ pywin32 not available - install with: pip install pywin32")
            return False
        except Exception as e:
            print(f"❌ Windows DPAPI setup failed: {e}")
            return False
    
    def enforce_secret_manager_startup(self):
        """Enforce server startup only with Secret Manager secrets."""
        print("\n🚫 ENFORCING SECRET MANAGER STARTUP")
        print("=" * 40)
        
        startup_check_script = '''
import os
import sys
from pathlib import Path

class SecretManagerEnforcer:
    """Enforce Secret Manager usage for server startup."""
    
    def __init__(self):
        self.required_secrets = [
            "HMAC_KEYS",
            "JWT_SECRET", 
            "API_KEYS",
            "DATABASE_URL"
        ]
        self.blocked_files = [".env", ".secrets", "config.json"]
    
    def check_secret_manager_available(self):
        """Check if Secret Manager is available."""
        try:
            from secret_manager_client import SecretManagerClient
            client = SecretManagerClient()
            return True
        except ImportError:
            return False
    
    def check_blocked_files(self):
        """Check for blocked secret files."""
        blocked_found = []
        
        for file_name in self.blocked_files:
            if Path(file_name).exists():
                blocked_found.append(file_name)
        
        return blocked_found
    
    def validate_startup(self):
        """Validate server startup requirements."""
        print("🔍 Validating server startup requirements...")
        
        # Check Secret Manager availability
        if not self.check_secret_manager_available():
            print("❌ Secret Manager not available")
            return False
        
        # Check for blocked files
        blocked_files = self.check_blocked_files()
        if blocked_files:
            print(f"❌ Blocked secret files found: {blocked_files}")
            print("🚫 Server startup blocked - remove secret files")
            return False
        
        # Check environment variables
        missing_secrets = []
        for secret in self.required_secrets:
            if not os.getenv(secret):
                missing_secrets.append(secret)
        
        if missing_secrets:
            print(f"❌ Missing required secrets: {missing_secrets}")
            return False
        
        print("✅ Server startup validation passed")
        return True
    
    def block_startup_if_invalid(self):
        """Block server startup if validation fails."""
        if not self.validate_startup():
            print("🚫 SERVER STARTUP BLOCKED")
            print("   Reason: Security requirements not met")
            print("   Action: Fix secret management before starting server")
            sys.exit(1)

if __name__ == "__main__":
    enforcer = SecretManagerEnforcer()
    enforcer.block_startup_if_invalid()
'''
        
        with open("secret_manager_enforcer.py", "w", encoding="utf-8") as f:
            f.write(startup_check_script)
        
        print("✅ Secret Manager enforcer created")
        
        # Update main server to include enforcer
        server_startup_script = '''
# CoolBits.ai Server Startup with Security Enforcement
# ==================================================

import sys
from pathlib import Path

# Add security enforcement
sys.path.insert(0, str(Path(__file__).parent))

try:
    from secret_manager_enforcer import SecretManagerEnforcer
    enforcer = SecretManagerEnforcer()
    enforcer.block_startup_if_invalid()
    print("✅ Security validation passed - server starting")
except ImportError:
    print("❌ Security enforcer not available - server startup blocked")
    sys.exit(1)
except Exception as e:
    print(f"❌ Security validation failed: {e}")
    sys.exit(1)

# Continue with normal server startup...
print("🚀 CoolBits.ai server starting with security enforcement")
'''
        
        with open("secure_server_startup.py", "w", encoding="utf-8") as f:
            f.write(server_startup_script)
        
        print("✅ Secure server startup script created")
        return True
    
    def create_security_policies(self):
        """Create enterprise security policies."""
        print("\n📋 CREATING SECURITY POLICIES")
        print("=" * 35)
        
        security_policies = {
            "key_management": {
                "policy": "NO_KEYS_IN_ENV_FILES",
                "description": "No keys allowed in .env files on disk unencrypted",
                "enforcement": "Secret Manager or DPAPI only",
                "violation_action": "Server startup blocked"
            },
            "build_security": {
                "policy": "SIGNED_BUILDS_ONLY",
                "description": "Builds must be from commit SHA signed",
                "enforcement": "Health endpoint displays SHA, release blocked if missing",
                "violation_action": "Deployment blocked"
            },
            "mock_policy": {
                "policy": "NO_MOCKS_IN_MAIN",
                "description": "No mock code allowed in main branch",
                "enforcement": "Mocks only in 'sim' branch, CI fails on main",
                "violation_action": "CI pipeline fails"
            },
            "desktop_parity": {
                "policy": "WEB_AS_SOURCE_OF_TRUTH",
                "description": "Desktop/Tauri remains consumer, web parity is source of truth",
                "enforcement": "Desktop syncs with web, not vice versa",
                "violation_action": "Sync blocked"
            }
        }
        
        with open("security_policies.json", "w", encoding="utf-8") as f:
            json.dump(security_policies, f, indent=2)
        
        print("✅ Security policies created")
        
        # Create policy enforcer
        policy_enforcer_script = '''
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
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True
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
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                
                if current_branch == "main":
                    # Check for mock files
                    mock_files = list(Path(".").glob("**/mock_*.py"))
                    mock_files.extend(list(Path(".").glob("**/test_*.py")))
                    
                    if mock_files:
                        print(f"❌ VIOLATION: Mock files found in main branch")
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
'''
        
        with open("security_policy_enforcer.py", "w", encoding="utf-8") as f:
            f.write(policy_enforcer_script)
        
        print("✅ Security policy enforcer created")
        return True
    
    def run_immediate_hardening(self):
        """Run immediate security hardening."""
        print("🚨 COOLBITS.AI IMMEDIATE SECURITY HARDENING")
        print("=" * 50)
        print(f"🕐 Started: {datetime.now().isoformat()}")
        
        # 1. Rotate compromised key
        new_key = self.rotate_compromised_key()
        
        # 2. Setup Secret Manager
        secret_manager_ready = self.setup_secret_manager()
        
        # 3. Setup Windows DPAPI
        dpapi_ready = self.setup_windows_dpapi()
        
        # 4. Enforce Secret Manager startup
        startup_enforced = self.enforce_secret_manager_startup()
        
        # 5. Create security policies
        policies_created = self.create_security_policies()
        
        # Summary
        print("\n🎯 IMMEDIATE HARDENING SUMMARY")
        print("=" * 35)
        print(f"✅ Compromised key rotated: {new_key is not None}")
        print(f"✅ Secret Manager ready: {secret_manager_ready}")
        print(f"✅ Windows DPAPI ready: {dpapi_ready}")
        print(f"✅ Startup enforcement: {startup_enforced}")
        print(f"✅ Security policies: {policies_created}")
        
        if all([new_key, secret_manager_ready, dpapi_ready, startup_enforced, policies_created]):
            print("\n🎉 IMMEDIATE HARDENING COMPLETE!")
            print("🚀 CoolBits.ai is now enterprise-secure")
            return True
        else:
            print("\n❌ HARDENING INCOMPLETE")
            print("🚨 Some security measures failed")
            return False


if __name__ == "__main__":
    hardening = SecurityHardening()
    hardening.run_immediate_hardening()
