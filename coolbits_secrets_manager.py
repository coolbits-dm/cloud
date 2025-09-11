#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai Internal Secrets System
SC COOL BITS SRL - Secure key management system
"""

import json
import base64
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
import secrets
import string


class CoolBitsSecretsManager:
    """Internal Secrets Management System for CoolBits.ai"""

    def __init__(self):
        self.company = "SC COOL BITS SRL"
        self.ceo = "Andrei"
        self.ai_assistant = "Cursor AI Assistant"
        self.contract_date = "2025-09-06"

        # Secrets storage path
        self.secrets_path = Path(__file__).parent / "secrets"
        self.secrets_path.mkdir(exist_ok=True)

        # Master key for encryption
        self.master_key = self._generate_master_key()

        # Secrets database
        self.secrets_db = {
            "andy_agent": {
                "xai_key": "andy_xai_secret_key",
                "openai_key": "andy_openai_secret_key",
                "internal_token": "andy_internal_token",
                "rag_key": "andy_rag_secret_key",
            },
            "system_agents": {
                "frontend_agent": {
                    "ogpt_key": "ogpt01-frontend",
                    "ogrok_key": "ogrok01-frontend",
                },
                "backend_agent": {
                    "ogpt_key": "ogpt02-backend",
                    "ogrok_key": "ogrok02-backend",
                },
                "devops_agent": {
                    "ogpt_key": "ogpt03-devops",
                    "ogrok_key": "ogrok03-devops",
                },
                "testing_agent": {
                    "ogpt_key": "ogpt04-testing",
                    "ogrok_key": "ogrok04-testing",
                },
            },
            "system_keys": {
                "database_key": "coolbits_db_secret",
                "api_gateway_key": "api_gateway_secret",
                "websocket_key": "websocket_secret",
                "notification_key": "notification_secret",
            },
            "external_services": {
                "google_cloud": "gcloud_service_key",
                "vertex_ai": "vertex_ai_key",
                "bigquery": "bigquery_key",
                "cloud_storage": "cloud_storage_key",
            },
        }

        # Initialize secrets
        self._initialize_secrets()

    def _generate_master_key(self) -> str:
        """Generate master encryption key"""
        # Use system-specific data to generate consistent key
        system_data = f"{self.company}_{self.ceo}_{self.contract_date}"
        return hashlib.sha256(system_data.encode()).hexdigest()[:32]

    def _encrypt_secret(self, secret: str) -> str:
        """Encrypt a secret using master key"""
        # Simple XOR encryption with master key
        encrypted = ""
        for i, char in enumerate(secret):
            key_char = self.master_key[i % len(self.master_key)]
            encrypted += chr(ord(char) ^ ord(key_char))
        return base64.b64encode(encrypted.encode()).decode()

    def _decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt a secret using master key"""
        try:
            encrypted = base64.b64decode(encrypted_secret.encode()).decode()
            decrypted = ""
            for i, char in enumerate(encrypted):
                key_char = self.master_key[i % len(self.master_key)]
                decrypted += chr(ord(char) ^ ord(key_char))
            return decrypted
        except Exception:
            return encrypted_secret  # Return as-is if decryption fails

    def _initialize_secrets(self):
        """Initialize secrets database"""
        secrets_file = self.secrets_path / "secrets.json"

        if not secrets_file.exists():
            # Create encrypted secrets file
            encrypted_secrets = {}
            for category, secrets_dict in self.secrets_db.items():
                encrypted_secrets[category] = {}
                for key, value in secrets_dict.items():
                    if isinstance(value, dict):
                        encrypted_secrets[category][key] = {}
                        for sub_key, sub_value in value.items():
                            encrypted_secrets[category][key][sub_key] = (
                                self._encrypt_secret(sub_value)
                            )
                    else:
                        encrypted_secrets[category][key] = self._encrypt_secret(value)

            with open(secrets_file, "w") as f:
                json.dump(encrypted_secrets, f, indent=2)

            print("🔐 Secrets database initialized successfully")
        else:
            # Load existing secrets
            with open(secrets_file, "r") as f:
                encrypted_secrets = json.load(f)

            # Decrypt and load secrets
            for category, secrets_dict in encrypted_secrets.items():
                if category not in self.secrets_db:
                    self.secrets_db[category] = {}

                for key, value in secrets_dict.items():
                    if isinstance(value, dict):
                        if key not in self.secrets_db[category]:
                            self.secrets_db[category][key] = {}
                        for sub_key, sub_value in value.items():
                            self.secrets_db[category][key][sub_key] = (
                                self._decrypt_secret(sub_value)
                            )
                    else:
                        self.secrets_db[category][key] = self._decrypt_secret(value)

    def get_secret(
        self, category: str, key: str, sub_key: Optional[str] = None
    ) -> Optional[str]:
        """Get a secret from the database"""
        try:
            if category in self.secrets_db:
                if sub_key:
                    if (
                        key in self.secrets_db[category]
                        and sub_key in self.secrets_db[category][key]
                    ):
                        return self.secrets_db[category][key][sub_key]
                else:
                    if key in self.secrets_db[category]:
                        return self.secrets_db[category][key]
            return None
        except Exception as e:
            print(f"❌ Error getting secret: {e}")
            return None

    def set_secret(
        self, category: str, key: str, value: str, sub_key: Optional[str] = None
    ) -> bool:
        """Set a secret in the database"""
        try:
            if category not in self.secrets_db:
                self.secrets_db[category] = {}

            if sub_key:
                if key not in self.secrets_db[category]:
                    self.secrets_db[category][key] = {}
                self.secrets_db[category][key][sub_key] = value
            else:
                self.secrets_db[category][key] = value

            # Save encrypted secrets
            self._save_secrets()
            return True
        except Exception as e:
            print(f"❌ Error setting secret: {e}")
            return False

    def _save_secrets(self):
        """Save encrypted secrets to file"""
        try:
            secrets_file = self.secrets_path / "secrets.json"
            encrypted_secrets = {}

            for category, secrets_dict in self.secrets_db.items():
                encrypted_secrets[category] = {}
                for key, value in secrets_dict.items():
                    if isinstance(value, dict):
                        encrypted_secrets[category][key] = {}
                        for sub_key, sub_value in value.items():
                            encrypted_secrets[category][key][sub_key] = (
                                self._encrypt_secret(sub_value)
                            )
                    else:
                        encrypted_secrets[category][key] = self._encrypt_secret(value)

            with open(secrets_file, "w") as f:
                json.dump(encrypted_secrets, f, indent=2)

            print("🔐 Secrets saved successfully")
        except Exception as e:
            print(f"❌ Error saving secrets: {e}")

    def generate_new_key(self, length: int = 32) -> str:
        """Generate a new random key"""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def list_secrets(self) -> Dict[str, Any]:
        """List all secrets (without revealing values)"""
        secrets_list = {}
        for category, secrets_dict in self.secrets_db.items():
            secrets_list[category] = {}
            for key, value in secrets_dict.items():
                if isinstance(value, dict):
                    secrets_list[category][key] = list(value.keys())
                else:
                    secrets_list[category][key] = "***"
        return secrets_list

    def get_andy_keys(self) -> Dict[str, str]:
        """Get Andy's specific keys"""
        return {
            "xai_key": self.get_secret("andy_agent", "xai_key"),
            "openai_key": self.get_secret("andy_agent", "openai_key"),
            "internal_token": self.get_secret("andy_agent", "internal_token"),
            "rag_key": self.get_secret("andy_agent", "rag_key"),
        }

    def print_secrets_status(self):
        """Print secrets system status"""
        print("=" * 80)
        print("🔐 COOLBITS.AI INTERNAL SECRETS SYSTEM")
        print("🏢 SC COOL BITS SRL - Secure Key Management")
        print("=" * 80)
        print(f"👤 CEO: {self.ceo}")
        print(f"🤖 AI Assistant: {self.ai_assistant}")
        print(f"📅 Contract Date: {self.contract_date}")
        print("=" * 80)
        print("🔑 SECRETS CATEGORIES:")

        for category, secrets_dict in self.secrets_db.items():
            print(f"  • {category.replace('_', ' ').title()}:")
            for key, value in secrets_dict.items():
                if isinstance(value, dict):
                    print(f"    - {key}: {len(value)} sub-keys")
                else:
                    print(f"    - {key}: ***")

        print("=" * 80)
        print("🎯 ANDY'S KEYS STATUS:")
        andy_keys = self.get_andy_keys()
        for key_name, key_value in andy_keys.items():
            status = "✅ Set" if key_value else "❌ Not Set"
            print(f"  • {key_name}: {status}")

        print("=" * 80)
        print("🔐 SECURITY FEATURES:")
        print("  • Master key encryption")
        print("  • Base64 encoding")
        print("  • Local storage only")
        print("  • No external dependencies")
        print("  • Automatic key generation")
        print("=" * 80)


# Initialize Secrets Manager
secrets_manager = CoolBitsSecretsManager()


# Main functions
def get_secret(category: str, key: str, sub_key: Optional[str] = None) -> Optional[str]:
    """🔐 Get a secret from the database"""
    return secrets_manager.get_secret(category, key, sub_key)


def set_secret(
    category: str, key: str, value: str, sub_key: Optional[str] = None
) -> bool:
    """🔐 Set a secret in the database"""
    return secrets_manager.set_secret(category, key, value, sub_key)


def get_andy_keys() -> Dict[str, str]:
    """🤖 Get Andy's specific keys"""
    return secrets_manager.get_andy_keys()


def generate_new_key(length: int = 32) -> str:
    """🔑 Generate a new random key"""
    return secrets_manager.generate_new_key(length)


def secrets_status():
    """🔐 Show secrets system status"""
    secrets_manager.print_secrets_status()


if __name__ == "__main__":
    print("=" * 80)
    print("🔐 COOLBITS.AI INTERNAL SECRETS SYSTEM")
    print("🏢 SC COOL BITS SRL - Secure Key Management")
    print("=" * 80)
    print(f"👤 CEO: {secrets_manager.ceo}")
    print(f"🤖 AI Assistant: {secrets_manager.ai_assistant}")
    print(f"📅 Contract Date: {secrets_manager.contract_date}")
    print("=" * 80)
    print("🚀 Available Commands:")
    print("  • get_secret(category, key, sub_key) - Get a secret")
    print("  • set_secret(category, key, value, sub_key) - Set a secret")
    print("  • get_andy_keys() - Get Andy's keys")
    print("  • generate_new_key(length) - Generate new key")
    print("  • secrets_status() - Show secrets status")
    print("=" * 80)
