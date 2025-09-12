# Authentication module for M20.1
import os
import secrets
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from urllib.parse import urlencode, parse_qs
import requests
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

# Environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
MAGIC_LINK_SECRET = os.getenv("MAGIC_LINK_SECRET", secrets.token_urlsafe(32))
SESSION_SECRET = os.getenv("SESSION_SECRET", secrets.token_urlsafe(32))

# OIDC Configuration
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid_configuration"
GOOGLE_SCOPES = ["openid", "email", "profile"]

class AuthManager:
    """Authentication manager with OIDC and Magic Link support"""
    
    def __init__(self):
        self.google_config = None
        self._load_google_config()
    
    def _load_google_config(self):
        """Load Google OIDC configuration"""
        try:
            response = requests.get(GOOGLE_DISCOVERY_URL, timeout=10)
            if response.status_code == 200:
                self.google_config = response.json()
                logger.info("Google OIDC configuration loaded")
            else:
                logger.warning("Failed to load Google OIDC configuration")
        except Exception as e:
            logger.error(f"Error loading Google OIDC config: {e}")
    
    def generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        return code_verifier, code_challenge
    
    def get_google_auth_url(self, state: str, code_challenge: str) -> str:
        """Generate Google OAuth URL"""
        if not self.google_config:
            raise ValueError("Google OIDC configuration not loaded")
        
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback"),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        auth_url = self.google_config["authorization_endpoint"]
        return f"{auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, code_verifier: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        if not self.google_config:
            raise ValueError("Google OIDC configuration not loaded")
        
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback"),
            "code_verifier": code_verifier
        }
        
        response = requests.post(
            self.google_config["token_endpoint"],
            data=token_data,
            timeout=10
        )
        
        if response.status_code != 200:
            raise ValueError(f"Token exchange failed: {response.text}")
        
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Google"""
        if not self.google_config:
            raise ValueError("Google OIDC configuration not loaded")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            self.google_config["userinfo_endpoint"],
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            raise ValueError(f"User info request failed: {response.text}")
        
        return response.json()
    
    def generate_magic_link(self, email: str, org_id: str = None) -> str:
        """Generate magic link for email authentication"""
        # Create token with expiration
        payload = {
            "email": email,
            "org_id": org_id,
            "exp": int(time.time()) + 3600,  # 1 hour
            "type": "magic_link"
        }
        
        token = jwt.encode(payload, MAGIC_LINK_SECRET, algorithm="HS256")
        
        # Create magic link
        base_url = os.getenv("MAGIC_LINK_BASE_URL", "http://localhost:3000")
        magic_link = f"{base_url}/auth/magic?token={token}"
        
        return magic_link
    
    def verify_magic_link(self, token: str) -> Dict[str, Any]:
        """Verify magic link token"""
        try:
            payload = jwt.decode(token, MAGIC_LINK_SECRET, algorithms=["HS256"])
            if payload.get("type") != "magic_link":
                raise ValueError("Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Magic link expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid magic link token")
    
    def create_session_token(self, user_id: str, org_id: str, role: str) -> str:
        """Create session JWT token"""
        payload = {
            "user_id": user_id,
            "org_id": org_id,
            "role": role,
            "exp": int(time.time()) + 86400,  # 24 hours
            "type": "session"
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    
    def verify_session_token(self, token: str) -> Dict[str, Any]:
        """Verify session JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if payload.get("type") != "session":
                raise ValueError("Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Session expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid session token")
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token"""
        return hmac.new(
            SESSION_SECRET.encode(),
            session_id.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_csrf_token(self, session_id: str, csrf_token: str) -> bool:
        """Verify CSRF token"""
        expected_token = self.generate_csrf_token(session_id)
        return hmac.compare_digest(expected_token, csrf_token)

# Global auth manager
auth_manager = AuthManager()

def get_google_auth_url(state: str, code_challenge: str) -> str:
    """Get Google OAuth URL"""
    return auth_manager.get_google_auth_url(state, code_challenge)

def exchange_code_for_token(code: str, code_verifier: str) -> Dict[str, Any]:
    """Exchange authorization code for tokens"""
    return auth_manager.exchange_code_for_token(code, code_verifier)

def get_user_info(access_token: str) -> Dict[str, Any]:
    """Get user info from Google"""
    return auth_manager.get_user_info(access_token)

def generate_magic_link(email: str, org_id: str = None) -> str:
    """Generate magic link"""
    return auth_manager.generate_magic_link(email, org_id)

def verify_magic_link(token: str) -> Dict[str, Any]:
    """Verify magic link token"""
    return auth_manager.verify_magic_link(token)

def create_session_token(user_id: str, org_id: str, role: str) -> str:
    """Create session token"""
    return auth_manager.create_session_token(user_id, org_id, role)

def verify_session_token(token: str) -> Dict[str, Any]:
    """Verify session token"""
    return auth_manager.verify_session_token(token)

def generate_csrf_token(session_id: str) -> str:
    """Generate CSRF token"""
    return auth_manager.generate_csrf_token(session_id)

def verify_csrf_token(session_id: str, csrf_token: str) -> bool:
    """Verify CSRF token"""
    return auth_manager.verify_csrf_token(session_id, csrf_token)

def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge"""
    return auth_manager.generate_pkce_pair()
