# /**************************************************************************/
# /*  test_config_security.py                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Security tests for secure configuration management.

Tests secret storage, credential encryption, and audit logging.
"""

import os
import tempfile
from pathlib import Path

import pytest

from engine.config.secure_config import (
    SecureConfigManager,
    TelemetryConfig,
    DashboardConfig,
    EnvironmentBackend,
    EncryptedFileBackend
)


class TestEnvironmentBackend:
    """Test environment variable backend."""
    
    def test_gets_secret_from_env(self, monkeypatch):
        """Retrieve secret from environment variable."""
        monkeypatch.setenv("GE_TEST_KEY", "secret_value")
        
        backend = EnvironmentBackend()
        value = backend.get_secret("test_key")
        
        assert value == "secret_value"
    
    def test_returns_none_for_missing_secret(self):
        """Return None for non-existent env var."""
        backend = EnvironmentBackend()
        value = backend.get_secret("nonexistent_key")
        
        assert value is None
    
    def test_set_secret_returns_false(self):
        """Environment backend is read-only."""
        backend = EnvironmentBackend()
        result = backend.set_secret("key", "value")
        
        assert result is False


class TestSecureConfigManager:
    """Test global configuration manager."""
    
    def test_stores_and_retrieves_secret(self, monkeypatch, tmp_path):
        """Store and retrieve secret from secure storage."""
        # Use temp directory for encrypted file backend
        monkeypatch.setenv("HOME", str(tmp_path))
        
        # Store secret
        result = SecureConfigManager.set_secret("test_secret", "my_value")
        assert result is True
        
        # Retrieve secret
        value = SecureConfigManager.get_secret("test_secret")
        assert value == "my_value"
    
    def test_returns_none_for_missing_secret(self):
        """Return None for non-existent secret."""
        value = SecureConfigManager.get_secret("definitely_not_set")
        assert value is None
    
    def test_deletes_secret(self, monkeypatch, tmp_path):
        """Delete secret from storage."""
        monkeypatch.setenv("HOME", str(tmp_path))
        
        # Store then delete
        SecureConfigManager.set_secret("to_delete", "value")
        result = SecureConfigManager.delete_secret("to_delete")
        
        assert result is True
        assert SecureConfigManager.get_secret("to_delete") is None
    
    def test_audit_logging(self, monkeypatch, tmp_path):
        """Log configuration access for audit."""
        monkeypatch.setenv("HOME", str(tmp_path))
        
        # Perform operations
        SecureConfigManager.set_secret("audited_key", "value")
        SecureConfigManager.get_secret("audited_key")
        
        # Check audit log
        log = SecureConfigManager.get_audit_log()
        assert len(log) >= 2
        
        # Verify log entries
        set_entries = [e for e in log if e["action"] == "set"]
        get_entries = [e for e in log if e["action"] == "get"]
        
        assert len(set_entries) >= 1
        assert len(get_entries) >= 1
    
    def test_rotate_secret(self, monkeypatch, tmp_path):
        """Generate new secret value."""
        monkeypatch.setenv("HOME", str(tmp_path))
        
        # Set initial secret
        SecureConfigManager.set_secret("rotating", "old_value")
        
        # Rotate
        new_value = SecureConfigManager.rotate_secret("rotating")
        
        assert new_value is not None
        assert new_value != "old_value"
        assert SecureConfigManager.get_secret("rotating") == new_value


class TestTelemetryConfig:
    """Test telemetry configuration."""
    
    def test_api_key_not_in_dict_export(self, monkeypatch, tmp_path):
        """API key not included in to_dict() output."""
        monkeypatch.setenv("HOME", str(tmp_path))
        
        config = TelemetryConfig()
        config.set_api_key("secret_api_key_123")
        
        exported = config.to_dict()
        
        # API key should not be in export
        assert "api_key" not in exported
        assert "_api_key_ref" not in exported
    
    def test_api_key_stored_securely(self, monkeypatch, tmp_path):
        """API key stored via secure config manager."""
        monkeypatch.setenv("HOME", str(tmp_path))
        
        config = TelemetryConfig()
        config.set_api_key("my_secret_key")
        
        # Retrieve via property
        retrieved = config.api_key
        assert retrieved == "my_secret_key"
    
    def test_validates_batch_size(self):
        """Batch size must be in valid range."""
        with pytest.raises(ValueError):
            TelemetryConfig(batch_size=0)
        
        with pytest.raises(ValueError):
            TelemetryConfig(batch_size=1001)
    
    def test_validates_queue_size(self):
        """Queue size must be in valid range."""
        with pytest.raises(ValueError):
            TelemetryConfig(max_queue_size=0)
        
        with pytest.raises(ValueError):
            TelemetryConfig(max_queue_size=10001)
    
    def test_default_values_are_safe(self):
        """Default configuration is secure."""
        config = TelemetryConfig()
        
        assert config.batch_size == 10  # Reasonable default
        assert config.max_queue_size == 100  # Prevents memory exhaustion
        assert config.rate_limit == 60  # 1 request per second
        assert config.compress is True  # Reduce bandwidth


class TestDashboardConfig:
    """Test dashboard configuration."""
    
    def test_api_key_not_in_dict_export(self, monkeypatch, tmp_path):
        """API key not included in to_dict() output."""
        monkeypatch.setenv("HOME", str(tmp_path))
        
        config = DashboardConfig()
        config.set_api_key("secret_key")
        
        exported = config.to_dict()
        
        assert "api_key" not in exported
        assert "_api_key_ref" not in exported


class TestEncryptedFileBackend:
    """Test encrypted file storage."""
    
    def test_stores_encrypted(self, tmp_path):
        """Secrets are encrypted on disk."""
        backend = EncryptedFileBackend(tmp_path, master_key="test_password_123")
        
        backend.set_secret("my_key", "my_secret")
        
        # Read file directly - should be encrypted
        secrets_file = tmp_path / '.secrets'
        content = secrets_file.read_bytes()
        
        # Should not contain plaintext
        assert b"my_secret" not in content
    
    def test_retrieves_decrypted(self, tmp_path):
        """Secrets decrypted when retrieved."""
        backend = EncryptedFileBackend(tmp_path, master_key="test_password_123")
        
        backend.set_secret("my_key", "my_secret")
        retrieved = backend.get_secret("my_key")
        
        assert retrieved == "my_secret"
    
    def test_different_passwords_yield_different_ciphertexts(self, tmp_path):
        """Different master keys produce different encryption."""
        backend1 = EncryptedFileBackend(tmp_path / "a", master_key="password1")
        backend2 = EncryptedFileBackend(tmp_path / "b", master_key="password2")
        
        backend1.set_secret("key", "value")
        backend2.set_secret("key", "value")
        
        content1 = (tmp_path / "a" / '.secrets').read_bytes()
        content2 = (tmp_path / "b" / '.secrets').read_bytes()
        
        assert content1 != content2
    
    def test_requires_master_key(self, tmp_path):
        """Cannot decrypt without master key."""
        backend = EncryptedFileBackend(tmp_path, master_key="correct_password")
        backend.set_secret("key", "value")
        
        # Create new backend with wrong password
        wrong_backend = EncryptedFileBackend(tmp_path, master_key="wrong_password")
        
        # Should fail to decrypt
        value = wrong_backend.get_secret("key")
        assert value is None  # Failed to decrypt
    
    def test_file_permissions_restrictive(self, tmp_path):
        """Secrets file has restrictive permissions."""
        import stat
        
        backend = EncryptedFileBackend(tmp_path, master_key="password")
        backend.set_secret("key", "value")
        
        secrets_file = tmp_path / '.secrets'
        
        # On Unix, check permissions
        if os.name != 'nt':
            mode = secrets_file.stat().st_mode
            # Should be 0o600 (owner read/write only)
            assert stat.S_IMODE(mode) == 0o600
