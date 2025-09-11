# CoolBits.ai Security Configuration
# ==================================

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SecurityConfig:
    """Security configuration for CoolBits.ai."""

    # RBAC Configuration
    rbac_enabled: bool = True
    rbac_config_file: str = "rbac_config.json"

    # HMAC Configuration
    hmac_enabled: bool = True
    hmac_keys_file: str = "hmac_keys.json"
    hmac_algorithm: str = "sha256"
    hmac_timestamp_tolerance: int = 300  # 5 minutes

    # JWT Configuration
    jwt_enabled: bool = True
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expires_in: int = 3600  # 1 hour

    # Rate Limiting
    rate_limiting_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 10

    # CORS Configuration
    cors_enabled: bool = True
    cors_origins: List[str] = None
    cors_methods: List[str] = None
    cors_headers: List[str] = None

    # Security Headers
    security_headers_enabled: bool = True
    content_security_policy: str = "default-src 'self'"
    strict_transport_security: str = "max-age=31536000; includeSubDomains"

    # Session Security
    session_secure: bool = True
    session_httponly: bool = True
    session_samesite: str = "Strict"
    session_timeout: int = 1800  # 30 minutes

    # Password Policy
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    password_max_age_days: int = 90

    # Audit Logging
    audit_logging_enabled: bool = True
    audit_log_file: str = "logs/security_audit.log"
    audit_log_level: str = "INFO"

    # IP Whitelisting
    ip_whitelist_enabled: bool = False
    ip_whitelist: List[str] = None

    # API Key Management
    api_key_rotation_days: int = 30
    api_key_max_usage_per_day: int = 1000

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:8501", "https://coolbits.ai"]

        if self.cors_methods is None:
            self.cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

        if self.cors_headers is None:
            self.cors_headers = [
                "Content-Type",
                "Authorization",
                "X-HMAC-Signature",
                "X-HMAC-Timestamp",
                "X-HMAC-Nonce",
            ]

        if self.ip_whitelist is None:
            self.ip_whitelist = []

        if not self.jwt_secret_key:
            import secrets

            self.jwt_secret_key = secrets.token_urlsafe(32)


class SecurityManager:
    """Manages security configuration and policies."""

    def __init__(self, config_file: str = "security_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> SecurityConfig:
        """Load security configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    return SecurityConfig(**data)
            except Exception as e:
                print(f"Error loading security config: {e}")
                return SecurityConfig()
        else:
            config = SecurityConfig()
            self._save_config(config)
            return config

    def _save_config(self, config: SecurityConfig):
        """Save security configuration to file."""
        with open(self.config_file, "w") as f:
            json.dump(asdict(config), f, indent=2)

    def update_config(self, **kwargs):
        """Update security configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        self._save_config(self.config)

    def get_config(self) -> SecurityConfig:
        """Get current security configuration."""
        return self.config

    def validate_password(self, password: str) -> Dict[str, bool]:
        """Validate password against security policy."""
        result = {"valid": True, "errors": []}

        if len(password) < self.config.password_min_length:
            result["valid"] = False
            result["errors"].append(
                f"Password must be at least {self.config.password_min_length} characters"
            )

        if self.config.password_require_uppercase and not any(
            c.isupper() for c in password
        ):
            result["valid"] = False
            result["errors"].append(
                "Password must contain at least one uppercase letter"
            )

        if self.config.password_require_lowercase and not any(
            c.islower() for c in password
        ):
            result["valid"] = False
            result["errors"].append(
                "Password must contain at least one lowercase letter"
            )

        if self.config.password_require_numbers and not any(
            c.isdigit() for c in password
        ):
            result["valid"] = False
            result["errors"].append("Password must contain at least one number")

        if self.config.password_require_symbols and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            result["valid"] = False
            result["errors"].append(
                "Password must contain at least one special character"
            )

        return result

    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed."""
        if not self.config.ip_whitelist_enabled:
            return True

        return ip_address in self.config.ip_whitelist

    def log_security_event(self, event_type: str, user_id: str, details: Dict):
        """Log security event."""
        if not self.config.audit_logging_enabled:
            return

        import logging
        from datetime import datetime

        # Create audit logger
        logger = logging.getLogger("security_audit")
        logger.setLevel(getattr(logging, self.config.audit_log_level))

        # Create file handler if not exists
        if not logger.handlers:
            os.makedirs(os.path.dirname(self.config.audit_log_file), exist_ok=True)
            handler = logging.FileHandler(self.config.audit_log_file)
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # Log event
        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }

        logger.info(json.dumps(log_data))

    def generate_security_report(self) -> Dict:
        """Generate security status report."""
        return {
            "rbac_status": "enabled" if self.config.rbac_enabled else "disabled",
            "hmac_status": "enabled" if self.config.hmac_enabled else "disabled",
            "jwt_status": "enabled" if self.config.jwt_enabled else "disabled",
            "rate_limiting_status": (
                "enabled" if self.config.rate_limiting_enabled else "disabled"
            ),
            "cors_status": "enabled" if self.config.cors_enabled else "disabled",
            "security_headers_status": (
                "enabled" if self.config.security_headers_enabled else "disabled"
            ),
            "audit_logging_status": (
                "enabled" if self.config.audit_logging_enabled else "disabled"
            ),
            "ip_whitelist_status": (
                "enabled" if self.config.ip_whitelist_enabled else "disabled"
            ),
            "password_policy": {
                "min_length": self.config.password_min_length,
                "require_uppercase": self.config.password_require_uppercase,
                "require_lowercase": self.config.password_require_lowercase,
                "require_numbers": self.config.password_require_numbers,
                "require_symbols": self.config.password_require_symbols,
                "max_age_days": self.config.password_max_age_days,
            },
            "session_security": {
                "secure": self.config.session_secure,
                "httponly": self.config.session_httponly,
                "samesite": self.config.session_samesite,
                "timeout": self.config.session_timeout,
            },
        }


# Global security manager instance
security_manager = SecurityManager()


def get_security_config() -> SecurityConfig:
    """Get global security configuration."""
    return security_manager.get_config()


def validate_password(password: str) -> Dict[str, bool]:
    """Validate password against security policy."""
    return security_manager.validate_password(password)


def log_security_event(event_type: str, user_id: str, details: Dict):
    """Log security event."""
    security_manager.log_security_event(event_type, user_id, details)


def generate_security_report() -> Dict:
    """Generate security status report."""
    return security_manager.generate_security_report()


if __name__ == "__main__":
    print("🔒 CoolBits.ai Security Configuration")
    print("=====================================")

    # Initialize security manager
    sm = SecurityManager()

    # Generate security report
    report = sm.generate_security_report()

    print("📊 Security Status Report:")
    print(json.dumps(report, indent=2))

    # Test password validation
    test_passwords = ["weak", "StrongPassword123!", "NoNumbersOrSymbols", "12345678"]

    print("\n🔐 Password Validation Tests:")
    for password in test_passwords:
        result = sm.validate_password(password)
        status = "✅ Valid" if result["valid"] else "❌ Invalid"
        print(f"{password}: {status}")
        if not result["valid"]:
            for error in result["errors"]:
                print(f"  - {error}")

    print("\n✅ Security configuration initialized successfully!")
