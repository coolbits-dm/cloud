# CoolBits.ai RBAC Middleware for Web Applications
# ================================================

import time
from typing import Dict, Optional, Callable
from functools import wraps
from flask import Flask, request, jsonify, g
from streamlit import session_state
import streamlit as st

# Import our RBAC manager
from rbac_manager import (
    rbac_manager,
    Role,
    Permission,
)


class RBACMiddleware:
    """RBAC middleware for Flask applications."""

    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize Flask app with RBAC middleware."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)

        # Add RBAC helper methods to app context
        app.rbac = self

    def before_request(self):
        """Process request before handling."""
        # Extract authentication information
        auth_header = request.headers.get("Authorization")
        hmac_signature = request.headers.get("X-HMAC-Signature")
        hmac_timestamp = request.headers.get("X-HMAC-Timestamp")
        hmac_nonce = request.headers.get("X-HMAC-Nonce")

        # Initialize user context
        g.user_id = None
        g.user_roles = []
        g.user_permissions = []
        g.is_authenticated = False

        # Try JWT authentication first
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            payload = rbac_manager.verify_jwt_token(token)
            if payload:
                g.user_id = payload.get("user_id")
                g.user_roles = payload.get("roles", [])
                g.user_permissions = payload.get("permissions", [])
                g.is_authenticated = True

        # Try HMAC authentication for sensitive endpoints
        if not g.is_authenticated and hmac_signature:
            if self._verify_hmac_request():
                # HMAC authentication successful
                g.is_authenticated = True
                g.user_id = "hmac-user"  # Special user for HMAC auth
                g.user_roles = [Role.ADMIN.value]  # HMAC users get admin privileges
                g.user_permissions = [perm.value for perm in Permission]

    def after_request(self, response):
        """Process response after handling."""
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response

    def _verify_hmac_request(self) -> bool:
        """Verify HMAC signature for request."""
        signature = request.headers.get("X-HMAC-Signature")
        timestamp = request.headers.get("X-HMAC-Timestamp")
        nonce = request.headers.get("X-HMAC-Nonce")

        if not all([signature, timestamp, nonce]):
            return False

        # Get request body
        body = request.get_data(as_text=True) if request.is_json else ""

        return rbac_manager.verify_hmac_signature(
            request.method, request.path, body, signature, timestamp, nonce
        )

    def require_auth(self, f: Callable) -> Callable:
        """Decorator to require authentication."""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.is_authenticated:
                return jsonify({"error": "Authentication required"}), 401
            return f(*args, **kwargs)

        return decorated_function

    def require_permission(self, permission: Permission):
        """Decorator to require specific permission."""

        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not g.is_authenticated:
                    return jsonify({"error": "Authentication required"}), 401

                if permission.value not in g.user_permissions:
                    return (
                        jsonify({"error": f"Permission {permission.value} required"}),
                        403,
                    )

                return f(*args, **kwargs)

            return decorated_function

        return decorator

    def require_role(self, role: Role):
        """Decorator to require specific role."""

        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not g.is_authenticated:
                    return jsonify({"error": "Authentication required"}), 401

                if role.value not in g.user_roles:
                    return jsonify({"error": f"Role {role.value} required"}), 403

                return f(*args, **kwargs)

            return decorated_function

        return decorator

    def require_hmac(self, f: Callable) -> Callable:
        """Decorator to require HMAC authentication for sensitive operations."""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.is_authenticated or g.user_id != "hmac-user":
                return jsonify({"error": "HMAC authentication required"}), 401

            return f(*args, **kwargs)

        return decorated_function


class StreamlitRBAC:
    """RBAC integration for Streamlit applications."""

    def __init__(self):
        self.session_key = "rbac_user"

    def login(self, username: str, password: str) -> bool:
        """Login user to Streamlit session."""
        user = rbac_manager.get_user_by_username(username)
        if not user or not user.is_active:
            return False

        # In a real application, you'd verify the password here
        # For now, we'll just check if user exists

        # Store user info in session
        session_state[self.session_key] = {
            "user_id": user.id,
            "username": user.username,
            "roles": [role.value for role in user.roles],
            "permissions": [perm.value for perm in user.permissions],
            "login_time": time.time(),
        }

        # Update last login
        user.last_login = time.time()
        rbac_manager._save_config()

        return True

    def logout(self):
        """Logout user from Streamlit session."""
        if self.session_key in session_state:
            del session_state[self.session_key]

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.session_key in session_state

    def get_current_user(self) -> Optional[Dict]:
        """Get current user information."""
        return session_state.get(self.session_key)

    def has_permission(self, permission: Permission) -> bool:
        """Check if current user has permission."""
        user = self.get_current_user()
        if not user:
            return False

        return permission.value in user.get("permissions", [])

    def has_role(self, role: Role) -> bool:
        """Check if current user has role."""
        user = self.get_current_user()
        if not user:
            return False

        return role.value in user.get("roles", [])

    def require_auth(self, f: Callable) -> Callable:
        """Decorator to require authentication in Streamlit."""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                st.error("Authentication required")
                st.stop()
            return f(*args, **kwargs)

        return decorated_function

    def require_permission(self, permission: Permission):
        """Decorator to require permission in Streamlit."""

        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.is_authenticated():
                    st.error("Authentication required")
                    st.stop()

                if not self.has_permission(permission):
                    st.error(f"Permission {permission.value} required")
                    st.stop()

                return f(*args, **kwargs)

            return decorated_function

        return decorator

    def require_role(self, role: Role):
        """Decorator to require role in Streamlit."""

        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.is_authenticated():
                    st.error("Authentication required")
                    st.stop()

                if not self.has_role(role):
                    st.error(f"Role {role.value} required")
                    st.stop()

                return f(*args, **kwargs)

            return decorated_function

        return decorator


# Global instances
streamlit_rbac = StreamlitRBAC()


def create_protected_endpoints(app: Flask, rbac_middleware: RBACMiddleware):
    """Create protected API endpoints."""

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        """Login endpoint."""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = rbac_manager.get_user_by_username(username)
        if not user or not user.is_active:
            return jsonify({"error": "Invalid credentials"}), 401

        # In a real application, verify password hash
        # For now, we'll just check if user exists

        # Generate JWT token
        token = rbac_manager.generate_jwt_token(user.id)

        return jsonify(
            {
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "roles": [role.value for role in user.roles],
                    "permissions": [perm.value for perm in user.permissions],
                },
            }
        )

    @app.route("/api/auth/logout", methods=["POST"])
    @rbac_middleware.require_auth
    def logout():
        """Logout endpoint."""
        # In a real application, you'd invalidate the token
        return jsonify({"message": "Logged out successfully"})

    @app.route("/api/users", methods=["GET"])
    @rbac_middleware.require_permission(Permission.USER_MANAGEMENT)
    def list_users():
        """List all users (admin only)."""
        users = rbac_manager.list_users()
        return jsonify(
            {
                "users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "roles": [role.value for role in user.roles],
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat(),
                    }
                    for user in users
                ]
            }
        )

    @app.route("/api/users", methods=["POST"])
    @rbac_middleware.require_permission(Permission.USER_MANAGEMENT)
    def create_user():
        """Create new user (admin only)."""
        data = request.get_json()

        try:
            roles = [Role(role) for role in data.get("roles", [])]
            user = rbac_manager.create_user(
                username=data["username"], email=data["email"], roles=roles
            )

            return (
                jsonify(
                    {
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "roles": [role.value for role in user.roles],
                            "permissions": [perm.value for perm in user.permissions],
                        }
                    }
                ),
                201,
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/sensitive/data", methods=["POST"])
    @rbac_middleware.require_hmac
    def sensitive_data():
        """Sensitive data endpoint requiring HMAC authentication."""
        data = request.get_json()

        return jsonify(
            {
                "message": "Sensitive operation completed",
                "data": data,
                "timestamp": time.time(),
            }
        )

    @app.route("/api/system/config", methods=["GET", "POST"])
    @rbac_middleware.require_permission(Permission.SYSTEM_CONFIG)
    def system_config():
        """System configuration endpoint."""
        if request.method == "GET":
            return jsonify(
                {
                    "config": {
                        "rbac_enabled": True,
                        "hmac_enabled": True,
                        "users_count": len(rbac_manager.list_users()),
                    }
                }
            )
        else:
            # POST - update config
            data = request.get_json()
            return jsonify({"message": "Configuration updated"})

    @app.route("/api/deploy", methods=["POST"])
    @rbac_middleware.require_permission(Permission.CODE_DEPLOY)
    def deploy():
        """Deployment endpoint (developer/admin only)."""
        data = request.get_json()

        return jsonify(
            {
                "message": "Deployment initiated",
                "deployment_id": f"deploy-{int(time.time())}",
                "initiated_by": g.user_id,
            }
        )


if __name__ == "__main__":
    # Example Flask app with RBAC
    app = Flask(__name__)
    rbac_middleware = RBACMiddleware(app)

    # Create protected endpoints
    create_protected_endpoints(app, rbac_middleware)

    # Basic health endpoint (no auth required)
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "rbac_enabled": True})

    print("🔐 CoolBits.ai RBAC Middleware")
    print("===============================")
    print("✅ RBAC middleware initialized")
    print("✅ Protected endpoints created")
    print("✅ HMAC authentication enabled")
    print("✅ JWT token authentication enabled")
    print("🚀 Ready to serve protected API endpoints!")

    # Run the app
    app.run(debug=True, port=5000)
