# /**************************************************************************/
# /*  secure_config.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Secure configuration management with credential encryption.

Features:
- System keychain integration
- Environment variable fallback
- Encrypted local storage
- Secret rotation support
- Audit logging
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar, Generic, Callable
from functools import wraps

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from engine.core.errors import SecurityError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class SecretBackend(ABC):
    """Abstract base for secret storage backends."""
    
    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve secret by key."""
        pass
    
    @abstractmethod
    def set_secret(self, key: str, value: str) -> bool:
        """Store secret."""
        pass
    
    @abstractmethod
    def delete_secret(self, key: str) -> bool:
        """Delete secret."""
        pass


class KeyringBackend(SecretBackend):
    """System keychain backend."""
    
    SERVICE_NAME = "GameEngineStudio"
    
    def __init__(self) -> None:
        if not KEYRING_AVAILABLE:
            raise RuntimeError("keyring module not available")
    
    def get_secret(self, key: str) -> Optional[str]:
        try:
            return keyring.get_password(self.SERVICE_NAME, key)
        except Exception as e:
            logger.warning(f"Keyring get failed: {e}")
            return None
    
    def set_secret(self, key: str, value: str) -> bool:
        try:
            keyring.set_password(self.SERVICE_NAME, key, value)
            return True
        except Exception as e:
            logger.error(f"Keyring set failed: {e}")
            return False
    
    def delete_secret(self, key: str) -> bool:
        try:
            keyring.delete_password(self.SERVICE_NAME, key)
            return True
        except Exception:
            return False


class EnvironmentBackend(SecretBackend):
    """Environment variable backend."""
    
    PREFIX = "GE_"
    
    def get_secret(self, key: str) -> Optional[str]:
        env_key = f"{self.PREFIX}{key.upper()}"
        return os.environ.get(env_key)
    
    def set_secret(self, key: str, value: str) -> bool:
        # Environment is read-only at runtime
        logger.warning("Cannot set secrets in environment backend")
        return False
    
    def delete_secret(self, key: str) -> bool:
        return False


class EncryptedFileBackend(SecretBackend):
    """Encrypted file backend with master key."""
    
    def __init__(self, config_dir: Path, master_key: Optional[str] = None):
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography module not available")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.secrets_file = self.config_dir / '.secrets'
        
        # Derive encryption key
        if master_key:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'game_engine_studio_v1',
                iterations=480000,
            )
            key = kdf.derive(master_key.encode())
            # Fernet requires base64-encoded 32-byte key
            import base64
            key_b64 = base64.urlsafe_b64encode(key)
            self._fernet = Fernet(key_b64)
        else:
            self._fernet = None
        
        self._cache: Dict[str, str] = {}
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load secrets from encrypted file."""
        if not self.secrets_file.exists():
            return
        
        if not self._fernet:
            logger.error("No master key provided for encrypted file")
            return
        
        try:
            with open(self.secrets_file, 'rb') as f:
                encrypted = f.read()
            
            decrypted = self._fernet.decrypt(encrypted)
            self._cache = json.loads(decrypted.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            self._cache = {}
    
    def _save_cache(self) -> None:
        """Save secrets to encrypted file."""
        if not self._fernet:
            return
        
        data = json.dumps(self._cache).encode('utf-8')
        encrypted = self._fernet.encrypt(data)
        
        # Atomic write
        temp_file = self.secrets_file.with_suffix('.tmp')
        with open(temp_file, 'wb') as f:
            f.write(encrypted)
        temp_file.replace(self.secrets_file)
        
        # Set restrictive permissions
        if os.name != 'nt':
            os.chmod(self.secrets_file, 0o600)
    
    def get_secret(self, key: str) -> Optional[str]:
        return self._cache.get(key)
    
    def set_secret(self, key: str, value: str) -> bool:
        self._cache[key] = value
        self._save_cache()
        return True
    
    def delete_secret(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            self._save_cache()
            return True
        return False


@dataclass
class TelemetryConfig:
    """Telemetry configuration with secure credential handling."""
    endpoint: str = ""
    project_id: str = ""
    _api_key_ref: str = field(default="", repr=False)
    batch_size: int = 10
    auto_upload: bool = False
    compress: bool = True
    max_queue_size: int = 100
    rate_limit: int = 60  # requests per minute
    
    def __post_init__(self):
        """Validate configuration."""
        if self.batch_size < 1 or self.batch_size > 1000:
            raise ValueError("batch_size must be between 1 and 1000")
        if self.max_queue_size < 1 or self.max_queue_size > 10000:
            raise ValueError("max_queue_size must be between 1 and 10000")
    
    @property
    def api_key(self) -> Optional[str]:
        """Get API key from secure storage."""
        if not self._api_key_ref:
            return None
        return SecureConfigManager.get_secret(self._api_key_ref)
    
    def set_api_key(self, api_key: str) -> None:
        """Store API key securely."""
        key_id = f"telemetry_api_key_{secrets.token_hex(8)}"
        SecureConfigManager.set_secret(key_id, api_key)
        self._api_key_ref = key_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Export config (without secrets)."""
        return {
            "endpoint": self.endpoint,
            "project_id": self.project_id,
            "batch_size": self.batch_size,
            "auto_upload": self.auto_upload,
            "compress": self.compress,
            "max_queue_size": self.max_queue_size,
            "rate_limit": self.rate_limit,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryConfig":
        """Create from dict."""
        return cls(
            endpoint=data.get("endpoint", ""),
            project_id=data.get("project_id", ""),
            _api_key_ref=data.get("_api_key_ref", ""),
            batch_size=data.get("batch_size", 10),
            auto_upload=data.get("auto_upload", False),
            compress=data.get("compress", True),
            max_queue_size=data.get("max_queue_size", 100),
            rate_limit=data.get("rate_limit", 60),
        )


@dataclass 
class DashboardConfig:
    """Dashboard integration configuration."""
    dashboard_url: str = ""
    project_id: str = ""
    _api_key_ref: str = field(default="", repr=False)
    refresh_interval: int = 300
    
    @property
    def api_key(self) -> Optional[str]:
        """Get API key from secure storage."""
        if not self._api_key_ref:
            return None
        return SecureConfigManager.get_secret(self._api_key_ref)
    
    def set_api_key(self, api_key: str) -> None:
        """Store API key securely."""
        key_id = f"dashboard_api_key_{secrets.token_hex(8)}"
        SecureConfigManager.set_secret(key_id, api_key)
        self._api_key_ref = key_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dashboard_url": self.dashboard_url,
            "project_id": self.project_id,
            "refresh_interval": self.refresh_interval,
        }


class SecureConfigManager:
    """Global secure configuration manager."""
    
    _instance: Optional["SecureConfigManager"] = None
    _backends: list[SecretBackend] = []
    _audit_log: list[Dict[str, Any]] = []
    _home_dir: Optional[Path] = None
    
    def __new__(cls):
        current_home = Path.home()
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_backends()
            cls._home_dir = current_home
        elif cls._home_dir != current_home:
            cls._instance._init_backends()
            cls._home_dir = current_home
        return cls._instance
    
    def _init_backends(self) -> None:
        """Initialize secret storage backends in priority order."""
        self._backends = []
        
        # 1. System keychain (most secure)
        if KEYRING_AVAILABLE:
            try:
                self._backends.append(KeyringBackend())
                logger.info("Keyring backend initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize keyring: {e}")
        
        # 2. Environment variables
        self._backends.append(EnvironmentBackend())
        
        # 3. Encrypted file (fallback)
        config_dir = Path.home() / '.game_engine' / 'config'
        if CRYPTO_AVAILABLE:
            # Derive key from machine-specific data
            machine_id = self._get_machine_id()
            try:
                self._backends.append(EncryptedFileBackend(config_dir, machine_id))
                logger.info("Encrypted file backend initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize encrypted file backend: {e}")
    
    def _get_machine_id(self) -> str:
        """Get machine-specific identifier for key derivation."""
        # Use combination of platform-specific identifiers
        import platform
        import getpass
        
        components = [
            platform.node(),
            platform.machine(),
            platform.system(),
            getpass.getuser(),
        ]
        return hashlib.sha256(''.join(components).encode()).hexdigest()[:32]
    
    @classmethod
    def get_secret(cls, key: str) -> Optional[str]:
        """Get secret from highest-priority backend."""
        instance = cls()
        
        for backend in instance._backends:
            value = backend.get_secret(key)
            if value is not None:
                instance._audit("get", key, backend.__class__.__name__)
                return value
        
        return None
    
    @classmethod
    def set_secret(cls, key: str, value: str) -> bool:
        """Store secret in all writable backends."""
        instance = cls()
        
        success = False
        for backend in instance._backends:
            if backend.set_secret(key, value):
                success = True
                instance._audit("set", key, backend.__class__.__name__)
        
        return success
    
    @classmethod
    def delete_secret(cls, key: str) -> bool:
        """Delete secret from all backends."""
        instance = cls()
        
        success = False
        for backend in instance._backends:
            if backend.delete_secret(key):
                success = True
                instance._audit("delete", key, backend.__class__.__name__)
        
        return success
    
    def _audit(self, action: str, key: str, backend: str) -> None:
        """Log configuration access for audit."""
        import time
        self._audit_log.append({
            "timestamp": time.time(),
            "action": action,
            "key": key[:8] + "...",  # Partial key for privacy
            "backend": backend,
        })
        
        # Keep log size manageable
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-500:]
    
    @classmethod
    def get_audit_log(cls) -> list:
        """Get configuration access audit log."""
        return list(cls()._audit_log)
    
    @classmethod
    def rotate_secret(cls, key: str) -> Optional[str]:
        """Generate new secret value and update all backends."""
        new_value = secrets.token_urlsafe(32)
        if cls.set_secret(key, new_value):
            return new_value
        return None


def requires_secret(secret_key: str):
    """Decorator to inject secrets into functions."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            secret = SecureConfigManager.get_secret(secret_key)
            if secret is None:
                raise SecurityError(f"Required secret not found: {secret_key}")
            return func(*args, secret=secret, **kwargs)
        return wrapper
    return decorator
