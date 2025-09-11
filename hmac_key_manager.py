# CoolBits.ai HMAC Key Generation and Management
# ==============================================

import os
import sys
import json
import secrets
import base64
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import argparse


class HMACKeyManager:
    """Manages HMAC keys for secure API access."""

    def __init__(self, config_file: str = "hmac_keys.json"):
        self.config_file = config_file
        self.keys: Dict[str, Dict] = {}
        self._load_keys()

    def _load_keys(self):
        """Load HMAC keys from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.keys = data.get("keys", {})
            except Exception as e:
                print(f"Error loading HMAC keys: {e}")
                self.keys = {}

    def _save_keys(self):
        """Save HMAC keys to file."""
        data = {"keys": self.keys, "last_updated": datetime.now().isoformat()}

        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2)

    def generate_key(
        self, name: str, description: str = "", expires_in_days: Optional[int] = None
    ) -> Dict[str, str]:
        """Generate a new HMAC key."""
        # Generate random key
        key_bytes = secrets.token_bytes(32)  # 256-bit key
        key_b64 = base64.b64encode(key_bytes).decode("utf-8")

        # Generate key ID
        key_id = hashlib.sha256(key_bytes).hexdigest()[:16]

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()

        # Store key information
        key_info = {
            "name": name,
            "description": description,
            "key_id": key_id,
            "key_b64": key_b64,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "is_active": True,
            "usage_count": 0,
            "last_used": None,
        }

        self.keys[key_id] = key_info
        self._save_keys()

        return {"key_id": key_id, "key_b64": key_b64, "expires_at": expires_at}

    def get_key(self, key_id: str) -> Optional[Dict]:
        """Get key information by ID."""
        return self.keys.get(key_id)

    def list_keys(self) -> List[Dict]:
        """List all keys."""
        return list(self.keys.values())

    def revoke_key(self, key_id: str) -> bool:
        """Revoke a key."""
        if key_id in self.keys:
            self.keys[key_id]["is_active"] = False
            self.keys[key_id]["revoked_at"] = datetime.now().isoformat()
            self._save_keys()
            return True
        return False

    def activate_key(self, key_id: str) -> bool:
        """Activate a key."""
        if key_id in self.keys:
            self.keys[key_id]["is_active"] = True
            if "revoked_at" in self.keys[key_id]:
                del self.keys[key_id]["revoked_at"]
            self._save_keys()
            return True
        return False

    def update_key_usage(self, key_id: str):
        """Update key usage statistics."""
        if key_id in self.keys:
            self.keys[key_id]["usage_count"] += 1
            self.keys[key_id]["last_used"] = datetime.now().isoformat()
            self._save_keys()

    def is_key_valid(self, key_id: str) -> bool:
        """Check if key is valid and not expired."""
        if key_id not in self.keys:
            return False

        key_info = self.keys[key_id]

        # Check if active
        if not key_info.get("is_active", False):
            return False

        # Check expiration
        expires_at = key_info.get("expires_at")
        if expires_at:
            try:
                expires_date = datetime.fromisoformat(expires_at)
                if datetime.now() > expires_date:
                    return False
            except ValueError:
                pass

        return True

    def cleanup_expired_keys(self) -> int:
        """Remove expired keys."""
        expired_keys = []
        current_time = datetime.now()

        for key_id, key_info in self.keys.items():
            expires_at = key_info.get("expires_at")
            if expires_at:
                try:
                    expires_date = datetime.fromisoformat(expires_at)
                    if current_time > expires_date:
                        expired_keys.append(key_id)
                except ValueError:
                    pass

        for key_id in expired_keys:
            del self.keys[key_id]

        if expired_keys:
            self._save_keys()

        return len(expired_keys)

    def generate_client_config(self, key_id: str) -> Dict[str, str]:
        """Generate client configuration for HMAC usage."""
        key_info = self.get_key(key_id)
        if not key_info or not self.is_key_valid(key_id):
            raise ValueError(f"Invalid key ID: {key_id}")

        return {
            "key_id": key_id,
            "key_b64": key_info["key_b64"],
            "algorithm": "sha256",
            "timestamp_tolerance": 300,
            "nonce_length": 16,
            "example_usage": {
                "method": "POST",
                "path": "/api/sensitive/data",
                "body": '{"data": "example"}',
                "headers": {
                    "X-HMAC-Signature": "<generated_signature>",
                    "X-HMAC-Timestamp": "<current_timestamp>",
                    "X-HMAC-Nonce": "<random_nonce>",
                },
            },
        }


def generate_hmac_signature(
    key_b64: str,
    method: str,
    path: str,
    body: str = "",
    timestamp: Optional[int] = None,
) -> Dict[str, str]:
    """Generate HMAC signature for a request."""
    import hmac
    import time
    import secrets

    if timestamp is None:
        timestamp = int(time.time())

    # Generate nonce
    nonce = secrets.token_urlsafe(16)

    # Decode key
    key_bytes = base64.b64decode(key_b64)

    # Create message to sign
    message = f"{method.upper()}\n{path}\n{body}\n{timestamp}\n{nonce}"

    # Generate signature
    signature = hmac.new(key_bytes, message.encode(), hashlib.sha256).hexdigest()

    return {
        "signature": signature,
        "timestamp": str(timestamp),
        "nonce": nonce,
        "algorithm": "sha256",
    }


def main():
    """Main CLI for HMAC key management."""
    parser = argparse.ArgumentParser(description="CoolBits.ai HMAC Key Manager")
    parser.add_argument(
        "--config", default="hmac_keys.json", help="HMAC keys config file"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate key command
    generate_parser = subparsers.add_parser("generate", help="Generate new HMAC key")
    generate_parser.add_argument("--name", required=True, help="Key name")
    generate_parser.add_argument("--description", default="", help="Key description")
    generate_parser.add_argument(
        "--expires-days", type=int, help="Key expiration in days"
    )

    # List keys command
    list_parser = subparsers.add_parser("list", help="List all keys")

    # Revoke key command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke a key")
    revoke_parser.add_argument("--key-id", required=True, help="Key ID to revoke")

    # Activate key command
    activate_parser = subparsers.add_parser("activate", help="Activate a key")
    activate_parser.add_argument("--key-id", required=True, help="Key ID to activate")

    # Generate client config command
    config_parser = subparsers.add_parser(
        "client-config", help="Generate client config"
    )
    config_parser.add_argument(
        "--key-id", required=True, help="Key ID for client config"
    )

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup expired keys")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize key manager
    key_manager = HMACKeyManager(args.config)

    try:
        if args.command == "generate":
            result = key_manager.generate_key(
                name=args.name,
                description=args.description,
                expires_in_days=args.expires_days,
            )

            print("🔑 New HMAC Key Generated")
            print("=========================")
            print(f"Key ID: {result['key_id']}")
            print(f"Key (Base64): {result['key_b64']}")
            if result["expires_at"]:
                print(f"Expires: {result['expires_at']}")
            print("\n⚠️  IMPORTANT: Store this key securely!")
            print("⚠️  The key will not be shown again!")

        elif args.command == "list":
            keys = key_manager.list_keys()

            print("🔑 HMAC Keys")
            print("============")
            for key in keys:
                status = "✅ Active" if key["is_active"] else "❌ Inactive"
                expires = (
                    f" (expires: {key['expires_at']})" if key["expires_at"] else ""
                )
                print(f"{key['key_id']} - {key['name']} - {status}{expires}")
                print(f"  Description: {key['description']}")
                print(f"  Created: {key['created_at']}")
                print(f"  Usage: {key['usage_count']} times")
                if key["last_used"]:
                    print(f"  Last used: {key['last_used']}")
                print()

        elif args.command == "revoke":
            if key_manager.revoke_key(args.key_id):
                print(f"✅ Key {args.key_id} revoked successfully")
            else:
                print(f"❌ Key {args.key_id} not found")

        elif args.command == "activate":
            if key_manager.activate_key(args.key_id):
                print(f"✅ Key {args.key_id} activated successfully")
            else:
                print(f"❌ Key {args.key_id} not found")

        elif args.command == "client-config":
            try:
                config = key_manager.generate_client_config(args.key_id)

                print("🔧 Client Configuration")
                print("=======================")
                print(json.dumps(config, indent=2))

            except ValueError as e:
                print(f"❌ {e}")

        elif args.command == "cleanup":
            removed_count = key_manager.cleanup_expired_keys()
            print(f"🧹 Cleaned up {removed_count} expired keys")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
