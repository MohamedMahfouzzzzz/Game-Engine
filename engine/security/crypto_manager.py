"""AES encryption and decryption for game data."""

import os
import hashlib
import hmac
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


@dataclass
class CryptoConfig:
    """Configuration for encryption."""

    algorithm: str = "AES-256-CBC"
    key_length: int = 32  # 256 bits
    iv_length: int = 16   # 128 bits
    enable_integrity: bool = True
    enable_compression: bool = True


class CryptoManager:
    """Handles AES encryption and decryption of game data."""

    def __init__(self, config: Optional[CryptoConfig] = None):
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography library required for encryption support")

        self.config = config or CryptoConfig()
        self.backend = default_backend()

    def generate_key(self, password: Optional[str] = None) -> bytes:
        """Generate encryption key from password or random."""
        if password:
            # Derive key from password using PBKDF2
            key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                b'game_engine_salt',
                100000,
                dklen=self.config.key_length
            )
        else:
            # Generate random key
            key = os.urandom(self.config.key_length)

        return key

    def generate_iv(self) -> bytes:
        """Generate random initialization vector."""
        return os.urandom(self.config.iv_length)

    def encrypt(self, plaintext: bytes, key: bytes) -> Tuple[bytes, bytes, Optional[bytes]]:
        """
        Encrypt data using AES-256-CBC.

        Returns:
            (ciphertext, iv, hmac_tag)
        """
        if len(key) != self.config.key_length:
            raise ValueError(f"Key must be {self.config.key_length} bytes")

        # Generate IV
        iv = self.generate_iv()

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()

        # Pad plaintext to block size
        padded = self._pad(plaintext)

        # Encrypt
        ciphertext = encryptor.update(padded) + encryptor.finalize()

        # Calculate HMAC for integrity
        hmac_tag = None
        if self.config.enable_integrity:
            h = hmac.new(key, ciphertext, hashlib.sha256)
            hmac_tag = h.digest()

        return ciphertext, iv, hmac_tag

    def decrypt(self, ciphertext: bytes, key: bytes, iv: bytes,
                hmac_tag: Optional[bytes] = None) -> bytes:
        """
        Decrypt data using AES-256-CBC.

        Args:
            ciphertext: Encrypted data
            key: Encryption key
            iv: Initialization vector
            hmac_tag: HMAC tag for integrity verification

        Returns:
            Decrypted plaintext
        """
        if len(key) != self.config.key_length:
            raise ValueError(f"Key must be {self.config.key_length} bytes")

        # Verify integrity
        if self.config.enable_integrity and hmac_tag:
            h = hmac.new(key, ciphertext, hashlib.sha256)
            if not hmac.compare_digest(h.digest(), hmac_tag):
                raise ValueError("HMAC verification failed - data integrity compromised")

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()

        # Decrypt
        padded = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad plaintext
        plaintext = self._unpad(padded)

        return plaintext

    def encrypt_file(self, input_path: str, output_path: str, key: bytes) -> None:
        """Encrypt file in-place."""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        # Read file
        with open(input_path, 'rb') as f:
            plaintext = f.read()

        # Encrypt
        ciphertext, iv, hmac_tag = self.encrypt(plaintext, key)

        # Write encrypted file with header
        with open(output_path, 'wb') as f:
            # Write magic header
            f.write(b'GSENC')  # Game Studio Encrypted
            # Write IV
            f.write(iv)
            # Write HMAC tag if present
            if hmac_tag:
                f.write(len(hmac_tag).to_bytes(4, 'big'))
                f.write(hmac_tag)
            else:
                f.write((0).to_bytes(4, 'big'))
            # Write ciphertext
            f.write(ciphertext)

    def decrypt_file(self, input_path: str, output_path: str, key: bytes) -> None:
        """Decrypt file."""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        with open(input_path, 'rb') as f:
            # Read and verify magic header
            magic = f.read(5)
            if magic != b'GSENC':
                raise ValueError("Not a valid encrypted game file")

            # Read IV
            iv = f.read(self.config.iv_length)
            if len(iv) != self.config.iv_length:
                raise ValueError("Invalid IV in encrypted file")

            # Read HMAC tag if present
            hmac_length = int.from_bytes(f.read(4), 'big')
            hmac_tag = None
            if hmac_length > 0:
                hmac_tag = f.read(hmac_length)

            # Read ciphertext
            ciphertext = f.read()

        # Decrypt
        plaintext = self.decrypt(ciphertext, key, iv, hmac_tag)

        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(plaintext)

    def _pad(self, data: bytes) -> bytes:
        """PKCS7 padding."""
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding

    def _unpad(self, data: bytes) -> bytes:
        """Remove PKCS7 padding."""
        padding_length = data[-1]
        return data[:-padding_length]
