
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
