# CoolBits.ai RBAC (Role-Based Access Control) System
# ==================================================

import os
import sys
import json
import hmac
import hashlib
import time
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import secrets
import base64


class Role(Enum):
    """User roles in the system."""

    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    VIEWER = "viewer"
    GUEST = "guest"


class Permission(Enum):
    """System permissions."""

    # Admin permissions
    ADMIN_ACCESS = "admin_access"
    SYSTEM_CONFIG = "system_config"
    USER_MANAGEMENT = "user_management"

    # Developer permissions
    CODE_DEPLOY = "code_deploy"
    API_ACCESS = "api_access"
    DEBUG_MODE = "debug_mode"

    # User permissions
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    PROFILE_UPDATE = "profile_update"

    # Viewer permissions
    DATA_VIEW = "data_view"
    REPORTS_VIEW = "reports_view"

    # Guest permissions
    BASIC_ACCESS = "basic_access"


@dataclass
class User:
    """User model with RBAC information."""

    id: str
    username: str
    email: str
    roles: List[Role]
    permissions: List[Permission]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class HMACConfig:
    """HMAC configuration for secure API access."""

    secret_key: str
    algorithm: str = "sha256"
    timestamp_tolerance: int = 300  # 5 minutes
    nonce_length: int = 16


class RBACManager:
    """Role-Based Access Control Manager."""

    def __init__(self, config_file: str = "rbac_config.json"):
        self.config_file = config_file
        self.users: Dict[str, User] = {}
        self.role_permissions: Dict[Role, Set[Permission]] = {}
        self.hmac_config: Optional[HMACConfig] = None

        self._initialize_role_permissions()
        self._load_config()

    def _initialize_role_permissions(self):
        """Initialize default role-permission mappings."""
        self.role_permissions = {
            Role.ADMIN: {
                Permission.ADMIN_ACCESS,
                Permission.SYSTEM_CONFIG,
                Permission.USER_MANAGEMENT,
                Permission.CODE_DEPLOY,
                Permission.API_ACCESS,
                Permission.DEBUG_MODE,
                Permission.DATA_READ,
                Permission.DATA_WRITE,
                Permission.PROFILE_UPDATE,
                Permission.DATA_VIEW,
                Permission.REPORTS_VIEW,
                Permission.BASIC_ACCESS,
            },
            Role.DEVELOPER: {
                Permission.CODE_DEPLOY,
                Permission.API_ACCESS,
                Permission.DEBUG_MODE,
                Permission.DATA_READ,
                Permission.DATA_WRITE,
                Permission.PROFILE_UPDATE,
                Permission.DATA_VIEW,
                Permission.REPORTS_VIEW,
                Permission.BASIC_ACCESS,
            },
            Role.USER: {
                Permission.DATA_READ,
                Permission.DATA_WRITE,
                Permission.PROFILE_UPDATE,
                Permission.DATA_VIEW,
                Permission.REPORTS_VIEW,
                Permission.BASIC_ACCESS,
            },
            Role.VIEWER: {
                Permission.DATA_VIEW,
                Permission.REPORTS_VIEW,
                Permission.BASIC_ACCESS,
            },
            Role.GUEST: {Permission.BASIC_ACCESS},
        }

    def _load_config(self):
        """Load RBAC configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)

                # Load users
                for user_data in config.get("users", []):
                    user = User(
                        id=user_data["id"],
                        username=user_data["username"],
                        email=user_data["email"],
                        roles=[Role(role) for role in user_data["roles"]],
                        permissions=[
                            Permission(perm) for perm in user_data["permissions"]
                        ],
                        created_at=datetime.fromisoformat(user_data["created_at"]),
                        last_login=(
                            datetime.fromisoformat(user_data["last_login"])
                            if user_data.get("last_login")
                            else None
                        ),
                        is_active=user_data.get("is_active", True),
                        metadata=user_data.get("metadata", {}),
                    )
                    self.users[user.id] = user

                # Load HMAC config
                hmac_data = config.get("hmac_config")
                if hmac_data:
                    self.hmac_config = HMACConfig(
                        secret_key=hmac_data["secret_key"],
                        algorithm=hmac_data.get("algorithm", "sha256"),
                        timestamp_tolerance=hmac_data.get("timestamp_tolerance", 300),
                        nonce_length=hmac_data.get("nonce_length", 16),
                    )

            except Exception as e:
                print(f"Error loading RBAC config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Create default RBAC configuration."""
        # Generate HMAC secret key
        secret_key = secrets.token_urlsafe(32)
        self.hmac_config = HMACConfig(secret_key=secret_key)

        # Create default admin user
        admin_user = User(
            id="admin-001",
            username="admin",
            email="admin@coolbits.ai",
            roles=[Role.ADMIN],
            permissions=list(self.role_permissions[Role.ADMIN]),
            created_at=datetime.now(),
        )
        self.users[admin_user.id] = admin_user

        self._save_config()

    def _save_config(self):
        """Save RBAC configuration to file."""
        config = {
            "users": [],
            "hmac_config": {
                "secret_key": self.hmac_config.secret_key,
                "algorithm": self.hmac_config.algorithm,
                "timestamp_tolerance": self.hmac_config.timestamp_tolerance,
                "nonce_length": self.hmac_config.nonce_length,
            },
        }

        for user in self.users.values():
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": [role.value for role in user.roles],
                "permissions": [perm.value for perm in user.permissions],
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": user.is_active,
                "metadata": user.metadata,
            }
            config["users"].append(user_data)

        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def create_user(
        self,
        username: str,
        email: str,
        roles: List[Role],
        custom_permissions: Optional[List[Permission]] = None,
    ) -> User:
        """Create a new user."""
        user_id = f"user-{len(self.users) + 1:03d}"

        # Collect permissions from roles
        permissions = set()
        for role in roles:
            permissions.update(self.role_permissions.get(role, set()))

        # Add custom permissions
        if custom_permissions:
            permissions.update(custom_permissions)

        user = User(
            id=user_id,
            username=username,
            email=email,
            roles=roles,
            permissions=list(permissions),
            created_at=datetime.now(),
        )

        self.users[user_id] = user
        self._save_config()

        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission."""
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return False

        return permission in user.permissions

    def has_role(self, user_id: str, role: Role) -> bool:
        """Check if user has specific role."""
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return False

        return role in user.roles

    def update_user_roles(self, user_id: str, roles: List[Role]):
        """Update user roles and recalculate permissions."""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        user.roles = roles

        # Recalculate permissions
        permissions = set()
        for role in roles:
            permissions.update(self.role_permissions.get(role, set()))

        user.permissions = list(permissions)
        self._save_config()

    def generate_hmac_signature(
        self, method: str, path: str, body: str = "", timestamp: Optional[int] = None
    ) -> Dict[str, str]:
        """Generate HMAC signature for API request."""
        if not self.hmac_config:
            raise ValueError("HMAC configuration not found")

        if timestamp is None:
            timestamp = int(time.time())

        # Generate nonce
        nonce = secrets.token_urlsafe(self.hmac_config.nonce_length)

        # Create message to sign
        message = f"{method.upper()}\n{path}\n{body}\n{timestamp}\n{nonce}"

        # Generate signature
        signature = hmac.new(
            self.hmac_config.secret_key.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        return {
            "signature": signature,
            "timestamp": str(timestamp),
            "nonce": nonce,
            "algorithm": self.hmac_config.algorithm,
        }

    def verify_hmac_signature(
        self,
        method: str,
        path: str,
        body: str,
        signature: str,
        timestamp: str,
        nonce: str,
    ) -> bool:
        """Verify HMAC signature."""
        if not self.hmac_config:
            return False

        try:
            timestamp_int = int(timestamp)
            current_time = int(time.time())

            # Check timestamp tolerance
            if abs(current_time - timestamp_int) > self.hmac_config.timestamp_tolerance:
                return False

            # Recreate message
            message = f"{method.upper()}\n{path}\n{body}\n{timestamp}\n{nonce}"

            # Generate expected signature
            expected_signature = hmac.new(
                self.hmac_config.secret_key.encode(), message.encode(), hashlib.sha256
            ).hexdigest()

            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)

        except (ValueError, TypeError):
            return False

    def generate_jwt_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Generate JWT token for user."""
        user = self.get_user(user_id)
        if not user or not user.is_active:
            raise ValueError(f"User {user_id} not found or inactive")

        payload = {
            "user_id": user_id,
            "username": user.username,
            "roles": [role.value for role in user.roles],
            "permissions": [perm.value for perm in user.permissions],
            "iat": int(time.time()),
            "exp": int(time.time()) + expires_in,
        }

        return jwt.encode(payload, self.hmac_config.secret_key, algorithm="HS256")

    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token, self.hmac_config.secret_key, algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def list_users(self) -> List[User]:
        """List all users."""
        return list(self.users.values())

    def deactivate_user(self, user_id: str):
        """Deactivate user."""
        user = self.get_user(user_id)
        if user:
            user.is_active = False
            self._save_config()

    def activate_user(self, user_id: str):
        """Activate user."""
        user = self.get_user(user_id)
        if user:
            user.is_active = True
            self._save_config()


# Global RBAC manager instance
rbac_manager = RBACManager()


def require_permission(permission: Permission):
    """Decorator to require specific permission."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be integrated with your web framework
            # For now, it's a placeholder
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: Role):
    """Decorator to require specific role."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be integrated with your web framework
            # For now, it's a placeholder
            return func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    # Example usage
    print("🔐 CoolBits.ai RBAC System")
    print("=========================")

    # Create some test users
    developer = rbac_manager.create_user(
        username="developer", email="dev@coolbits.ai", roles=[Role.DEVELOPER]
    )

    viewer = rbac_manager.create_user(
        username="viewer", email="viewer@coolbits.ai", roles=[Role.VIEWER]
    )

    print(f"✅ Created {len(rbac_manager.list_users())} users")

    # Test permissions
    print(
        f"Developer has API access: {rbac_manager.has_permission(developer.id, Permission.API_ACCESS)}"
    )
    print(
        f"Viewer has API access: {rbac_manager.has_permission(viewer.id, Permission.API_ACCESS)}"
    )

    # Generate HMAC signature
    signature_data = rbac_manager.generate_hmac_signature(
        "POST", "/api/sensitive", '{"data": "test"}'
    )
    print(f"HMAC signature generated: {signature_data['signature'][:16]}...")

    # Generate JWT token
    token = rbac_manager.generate_jwt_token(developer.id)
    print(f"JWT token generated: {token[:50]}...")

    print("✅ RBAC system initialized successfully!")
