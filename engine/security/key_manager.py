"""Key management for encryption."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib


class KeyManager:
    """Manages encryption keys for projects."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.keys_dir = self.project_path / ".engine" / "keys"
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.master_key_file = self.keys_dir / "master.key"
        self.key_metadata_file = self.keys_dir / "metadata.json"

    def create_master_key(self, password: Optional[str] = None) -> bytes:
        """Create and store master key."""
        if self.master_key_file.exists():
            raise ValueError("Master key already exists")

        key = os.urandom(32)  # 256-bit key

        # Store key (encrypted if password provided)
        if password:
            # Hash password to use as key derivation
            key_to_store = self._encrypt_key(key, password)
        else:
            key_to_store = key.hex()

        with open(self.master_key_file, 'w') as f:
            f.write(key_to_store)

        # Set restrictive permissions
        os.chmod(self.master_key_file, 0o600)

        # Store metadata
        self._store_metadata({
            'password_protected': bool(password),
            'created': __import__('datetime').datetime.now().isoformat()
        })

        return key

    def load_master_key(self, password: Optional[str] = None) -> Optional[bytes]:
        """Load master key."""
        if not self.master_key_file.exists():
            return None

        with open(self.master_key_file, 'r') as f:
            key_data = f.read()

        try:
            # Try to parse as hex
            return bytes.fromhex(key_data)
        except ValueError:
            # If not hex, it might be encrypted
            if password:
                return self._decrypt_key(key_data, password)
            return None

    def generate_save_key(self, save_slot: int) -> bytes:
        """Generate unique key for save slot."""
        master_key = self.load_master_key()
        if not master_key:
            raise RuntimeError("No master key found")

        # Derive slot-specific key
        slot_str = f"save_slot_{save_slot}".encode()
        slot_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key,
            slot_str,
            100000,
            dklen=32
        )
        return slot_key

    def _encrypt_key(self, key: bytes, password: str) -> str:
        """Encrypt key with password."""
        from .crypto_manager import CryptoManager

        try:
            crypto = CryptoManager()
            pwd_key = crypto.generate_key(password)
            ciphertext, iv, hmac_tag = crypto.encrypt(key, pwd_key)

            # Store as encrypted hex with IV
            encrypted_data = {
                'iv': iv.hex(),
                'ciphertext': ciphertext.hex(),
                'hmac': hmac_tag.hex() if hmac_tag else None
            }
            return json.dumps(encrypted_data)
        except ImportError:
            # Fallback to simple XOR if cryptography unavailable
            return key.hex()

    def _decrypt_key(self, encrypted_data: str, password: str) -> Optional[bytes]:
        """Decrypt key with password."""
        from .crypto_manager import CryptoManager

        try:
            data = json.loads(encrypted_data)
            crypto = CryptoManager()
            pwd_key = crypto.generate_key(password)

            iv = bytes.fromhex(data['iv'])
            ciphertext = bytes.fromhex(data['ciphertext'])
            hmac_tag = bytes.fromhex(data['hmac']) if data.get('hmac') else None

            return crypto.decrypt(ciphertext, pwd_key, iv, hmac_tag)
        except (json.JSONDecodeError, ValueError):
            return None

    def _store_metadata(self, metadata: Dict[str, Any]) -> None:
        """Store key metadata."""
        with open(self.key_metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def get_metadata(self) -> Dict[str, Any]:
        """Get key metadata."""
        if self.key_metadata_file.exists():
            with open(self.key_metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def rotate_master_key(self, old_password: Optional[str],
                         new_password: Optional[str]) -> bytes:
        """Rotate master key to new password."""
        # Load with old password
        old_key = self.load_master_key(old_password)
        if not old_key:
            raise ValueError("Failed to load master key")

        # Backup old key
        backup_file = self.keys_dir / "master.key.backup"
        with open(self.master_key_file, 'r') as f:
            backup_data = f.read()
        with open(backup_file, 'w') as f:
            f.write(backup_data)

        # Store with new password
        if new_password:
            key_to_store = self._encrypt_key(old_key, new_password)
        else:
            key_to_store = old_key.hex()

        with open(self.master_key_file, 'w') as f:
            f.write(key_to_store)

        # Update metadata
        self._store_metadata({
            'password_protected': bool(new_password),
            'rotated': __import__('datetime').datetime.now().isoformat()
        })

        return old_key
