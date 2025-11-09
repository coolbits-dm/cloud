import win32crypt
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
            with open(self.key_file, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = win32crypt.CryptUnprotectData(
                encrypted_data, None, None, None, 0
            )[1]

            return json.loads(decrypted_data.decode("utf-8"))
        except Exception:
            return {}

    def _save_keys(self):
        """Save keys encrypted to file."""
        try:
            json_data = json.dumps(self.keys).encode("utf-8")

            encrypted_data = win32crypt.CryptProtectData(json_data, None, None, None, 0)

            with open(self.key_file, "wb") as f:
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
            "created": datetime.now().isoformat(),
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
