"""Encrypted file format for save data."""

import json
from pathlib import Path
from typing import Optional, Any, Dict
import zlib

from engine.security import CryptoManager, KeyManager


class EncryptedFormat:
    """Handles reading/writing encrypted game data."""

    MAGIC_HEADER = b'GSAVE'  # Game Studio Save
    VERSION = 1

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.crypto = CryptoManager()
        self.key_manager = KeyManager(str(project_path))

    def save(self, data: Dict[str, Any], slot: int, encrypt: bool = True) -> Path:
        """Save encrypted game data to slot."""
        save_path = self.project_path / ".recovery" / f"save_slot_{slot}.gds"
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize data to JSON
        json_data = json.dumps(data, indent=2).encode('utf-8')

        # Compress
        compressed = zlib.compress(json_data, level=9)

        if encrypt:
            # Get encryption key for slot
            key = self.key_manager.generate_save_key(slot)

            # Encrypt
            ciphertext, iv, hmac_tag = self.crypto.encrypt(compressed, key)

            # Write encrypted file
            with open(save_path, 'wb') as f:
                f.write(self.MAGIC_HEADER)
                f.write(self.VERSION.to_bytes(1, 'big'))
                f.write(b'\x01')  # Encrypted flag
                f.write(iv)
                if hmac_tag:
                    f.write(len(hmac_tag).to_bytes(2, 'big'))
                    f.write(hmac_tag)
                else:
                    f.write((0).to_bytes(2, 'big'))
                f.write(ciphertext)
        else:
            # Write compressed (unencrypted)
            with open(save_path, 'wb') as f:
                f.write(self.MAGIC_HEADER)
                f.write(self.VERSION.to_bytes(1, 'big'))
                f.write(b'\x00')  # Not encrypted flag
                f.write(b'\x00' * 16)  # Dummy IV
                f.write((0).to_bytes(2, 'big'))  # No HMAC
                f.write(compressed)

        return save_path

    def load(self, slot: int, decrypt: bool = True) -> Dict[str, Any]:
        """Load encrypted game data from slot."""
        save_path = self.project_path / ".recovery" / f"save_slot_{slot}.gds"

        if not save_path.exists():
            raise FileNotFoundError(f"Save slot {slot} not found")

        with open(save_path, 'rb') as f:
            # Read header
            magic = f.read(5)
            if magic != self.MAGIC_HEADER:
                raise ValueError("Not a valid game save file")

            version = int.from_bytes(f.read(1), 'big')
            if version != self.VERSION:
                raise ValueError(f"Unsupported save version: {version}")

            is_encrypted = f.read(1)[0] == 1

            # Read IV
            iv = f.read(16)

            # Read HMAC tag
            hmac_length = int.from_bytes(f.read(2), 'big')
            hmac_tag = None
            if hmac_length > 0:
                hmac_tag = f.read(hmac_length)

            # Read ciphertext/compressed data
            data = f.read()

        # Decrypt if needed
        if is_encrypted and decrypt:
            key = self.key_manager.generate_save_key(slot)
            try:
                compressed = self.crypto.decrypt(data, key, iv, hmac_tag)
            except ValueError as e:
                raise ValueError(f"Failed to decrypt save slot {slot}: {e}")
        else:
            compressed = data

        # Decompress
        try:
            json_data = zlib.decompress(compressed)
        except zlib.error as e:
            raise ValueError(f"Failed to decompress save data: {e}")

        # Deserialize JSON
        try:
            return json.loads(json_data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"Failed to parse save data: {e}")

    def delete_slot(self, slot: int) -> None:
        """Delete save slot."""
        save_path = self.project_path / ".recovery" / f"save_slot_{slot}.gds"
        if save_path.exists():
            save_path.unlink()

    def list_slots(self) -> list[int]:
        """List all available save slots."""
        recovery_path = self.project_path / ".recovery"
        if not recovery_path.exists():
            return []

        slots = []
        for file in recovery_path.glob("save_slot_*.gds"):
            try:
                slot_num = int(file.stem.split('_')[-1])
                slots.append(slot_num)
            except ValueError:
                pass

        return sorted(slots)

    def get_slot_metadata(self, slot: int) -> Dict[str, Any]:
        """Get metadata for save slot without decrypting."""
        save_path = self.project_path / ".recovery" / f"save_slot_{slot}.gds"

        if not save_path.exists():
            return {}

        try:
            stat = save_path.stat()
            return {
                'size': stat.st_size,
                'created': stat.st_mtime,
                'exists': True
            }
        except OSError:
            return {'exists': False}
