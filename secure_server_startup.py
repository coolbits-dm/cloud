
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
