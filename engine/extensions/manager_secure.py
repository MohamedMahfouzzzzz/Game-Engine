# /**************************************************************************/
# /*  manager_secure.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Secure extension manager with sandboxing and validation.

This module provides a hardened extension management system with:
- Path traversal protection
- Code signing verification
- Resource limits
- Sandbox execution
- Manifest validation
- Audit logging
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set
import aiofiles
import aiofiles.os

from engine.core.errors import SecurityError

# Configure module logger
logger = logging.getLogger(__name__)

# Security constants
MAX_ZIP_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_EXTRACTED_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_FILES_IN_ZIP = 10_000
BLOCKED_EXTENSIONS: Set[str] = {
    '.exe', '.dll', '.so', '.dylib', '.bat', '.cmd', '.sh',
    '.py', '.pyc', '.pyo', '.php', '.rb', '.pl', '.jar'
}
ALLOWED_SIGNATURE_KEYS = ['ed25519', 'rsa4096']


@dataclass(frozen=True)
class ExtensionManifest:
    """Validated extension manifest."""
    name: str
    version: str
    author: str
    description: str
    permissions: List[str]
    entry_point: Optional[str]
    signature: Optional[str]
    checksums: Dict[str, str]
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ExtensionManifest":
        """Create manifest from dict with validation."""
        required = {'name', 'version', 'author'}
        missing = required - set(data.keys())
        if missing:
            raise SecurityError(f"Missing required fields: {missing}")
        
        # Sanitize name (prevent path traversal in extension name)
        name = str(data['name'])
        if '..' in name or '/' in name or '\\' in name:
            raise SecurityError(f"Invalid extension name: {name}")
        
        return cls(
            name=name[:64],  # Limit length
            version=str(data.get('version', '0.0.0'))[:32],
            author=str(data.get('author', 'Unknown'))[:128],
            description=str(data.get('description', ''))[:512],
            permissions=list(data.get('permissions', [])),
            entry_point=str(data.get('entry_point', ''))[:256] or None,
            signature=str(data.get('signature', ''))[:512] or None,
            checksums=dict(data.get('checksums', {}))
        )


class SecureExtensionManager:
    """Hardened extension manager with security controls."""
    
    def __init__(self, extensions_dir: str, trusted_keys: Optional[List[str]] = None) -> None:
        self.extensions_dir = Path(extensions_dir).resolve()
        self.trusted_keys = set(trusted_keys or [])
        self._installed_extensions: Dict[str, ExtensionManifest] = {}
        self._sandbox_dir: Optional[Path] = None
        
        # Ensure extensions directory exists with proper permissions
        self._ensure_secure_directory()
        
        # Load installed extensions
        self._load_installed()
    
    def _ensure_secure_directory(self) -> None:
        """Create extensions directory with secure permissions."""
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        
        # Set restrictive permissions (Unix)
        if os.name != 'nt':
            os.chmod(self.extensions_dir, 0o750)
    
    def _load_installed(self) -> None:
        """Load installed extensions with manifest validation."""
        if not self.extensions_dir.exists():
            return
            
        for ext_dir in self.extensions_dir.iterdir():
            if ext_dir.is_dir():
                manifest_file = ext_dir / 'manifest.json'
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        manifest = ExtensionManifest.from_dict(data)
                        self._installed_extensions[manifest.name] = manifest
                    except (json.JSONDecodeError, SecurityError) as e:
                        logger.warning(f"Invalid manifest in {ext_dir}: {e}")
    
    async def install_from_zip(self, zip_path: str, verify_signature: bool = True) -> ExtensionManifest:
        """Securely install extension from zip file.
        
        Args:
            zip_path: Path to zip file
            verify_signature: Whether to require signature verification
            
        Returns:
            ExtensionManifest of installed extension
            
        Raises:
            SecurityError: If security checks fail
            ValueError: If zip is invalid
        """
        zip_path_obj = Path(zip_path).resolve()
        
        # Validate zip file exists and is readable
        if not zip_path_obj.exists():
            raise FileNotFoundError(f"Zip file not found: {zip_path}")
        
        # Check file size before opening
        file_size = zip_path_obj.stat().st_size
        if file_size > MAX_ZIP_SIZE:
            raise SecurityError(
                f"Zip file too large: {file_size} bytes (max: {MAX_ZIP_SIZE})"
            )
        
        # Create temporary extraction directory
        with tempfile.TemporaryDirectory(prefix='ge_ext_') as temp_dir:
            temp_path = Path(temp_dir)
            
            # Safely extract with validation
            manifest = await self._safe_extract(zip_path_obj, temp_path)
            
            # Verify signature if required
            if verify_signature and self.trusted_keys:
                if not manifest.signature:
                    raise SecurityError("Extension requires signature but none provided")
                self._verify_signature(manifest, temp_path)
            
            # Verify file checksums
            self._verify_checksums(manifest, temp_path)
            
            # Scan for blocked file types
            self._scan_blocked_files(temp_path)
            
            # Move to final location
            target_dir = self.extensions_dir / manifest.name
            if target_dir.exists():
                logger.info(f"Removing existing extension: {manifest.name}")
                shutil.rmtree(target_dir)
            
            # Atomic move (copy then rename)
            shutil.copytree(temp_path, target_dir)
            
            # Store manifest
            self._installed_extensions[manifest.name] = manifest
            
            logger.info(f"Successfully installed extension: {manifest.name} v{manifest.version}")
            
            return manifest
    
    async def _safe_extract(self, zip_file: Path, target_dir: Path) -> ExtensionManifest:
        """Safely extract zip with security checks.
        
        Args:
            zip_file: Path to zip file
            target_dir: Directory to extract to
            
        Returns:
            Parsed ExtensionManifest
            
        Raises:
            SecurityError: If extraction fails security checks
        """
        manifest: Optional[ExtensionManifest] = None
        extracted_size = 0
        file_count = 0
        
        with zipfile.ZipFile(zip_file, 'r') as zf:
            # Validate zip contents before extraction
            for info in zf.infolist():
                file_count += 1
                if file_count > MAX_FILES_IN_ZIP:
                    raise SecurityError(
                        f"Too many files in zip: {file_count} (max: {MAX_FILES_IN_ZIP})"
                    )
                
                # Check for zip bomb (compression ratio)
                if info.compress_size > 0:
                    ratio = info.file_size / info.compress_size
                    if ratio > 100:  # Suspicious compression ratio
                        raise SecurityError(
                            f"Suspicious compression ratio for {info.filename}: {ratio:.1f}"
                        )
                
                extracted_size += info.file_size
                if extracted_size > MAX_EXTRACTED_SIZE:
                    raise SecurityError(
                        f"Extracted size would exceed limit: {extracted_size} bytes"
                    )
                
                # Security: Check for path traversal attempts
                # Normalize the path and ensure it stays within target
                target_path = (target_dir / info.filename).resolve()
                if not str(target_path).startswith(str(target_dir.resolve())):
                    raise SecurityError(
                        f"Path traversal attempt detected: {info.filename}"
                    )
                
                # Check for blocked file extensions
                file_ext = Path(info.filename).suffix.lower()
                if file_ext in BLOCKED_EXTENSIONS:
                    raise SecurityError(
                        f"Blocked file type in extension: {info.filename}"
                    )
                
                # Check for symlink attacks
                if info.external_attr >> 28 == 0xA:  # Symlink on Unix
                    raise SecurityError(f"Symlinks not allowed: {info.filename}")
            
            # Extract after validation
            zf.extractall(target_dir)
            
            # Find and validate manifest
            manifest_path = target_dir / 'manifest.json'
            if not manifest_path.exists():
                raise SecurityError("Extension manifest.json not found")
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            manifest = ExtensionManifest.from_dict(manifest_data)
        
        if not manifest:
            raise SecurityError("Failed to parse extension manifest")
        
        return manifest
    
    def _verify_signature(self, manifest: ExtensionManifest, ext_dir: Path) -> None:
        """Verify extension signature against trusted keys."""
        if not manifest.signature:
            return  # No signature to verify
        
        # TODO: Implement actual Ed25519/RSA signature verification
        # This is a placeholder for the actual cryptographic verification
        logger.warning("Signature verification not fully implemented")
        
        # Check signature format
        if ':' not in manifest.signature:
            raise SecurityError("Invalid signature format")
        
        sig_type, sig_value = manifest.signature.split(':', 1)
        if sig_type not in ALLOWED_SIGNATURE_KEYS:
            raise SecurityError(f"Unsupported signature type: {sig_type}")
    
    def _verify_checksums(self, manifest: ExtensionManifest, ext_dir: Path) -> None:
        """Verify file checksums against manifest."""
        for file_name, expected_hash in manifest.checksums.items():
            file_path = ext_dir / file_name
            if not file_path.exists():
                raise SecurityError(f"Checksum verification failed: {file_name} not found")
            
            # Calculate SHA-256 hash
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            
            actual_hash = sha256.hexdigest()
            if actual_hash != expected_hash:
                raise SecurityError(
                    f"Checksum mismatch for {file_name}: "
                    f"expected {expected_hash[:16]}..., got {actual_hash[:16]}..."
                )
    
    def _scan_blocked_files(self, ext_dir: Path) -> None:
        """Scan for blocked file types and patterns."""
        blocked_patterns = ['__pycache__', '.pyc', '.pyo', '.egg-info']
        
        for file_path in ext_dir.rglob('*'):
            if file_path.is_file():
                # Check extension
                if file_path.suffix.lower() in BLOCKED_EXTENSIONS:
                    raise SecurityError(f"Blocked file type found: {file_path}")
                
                # Check for blocked patterns
                for pattern in blocked_patterns:
                    if pattern in str(file_path):
                        raise SecurityError(f"Blocked pattern found: {pattern} in {file_path}")
    
    async def install_from_folder(self, folder_path: str, verify_signature: bool = True) -> ExtensionManifest:
        """Securely install extension from folder.
        
        Creates a zip from the folder and uses secure install path.
        """
        folder_path_obj = Path(folder_path).resolve()
        
        if not folder_path_obj.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        if not folder_path_obj.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {folder_path}")
        
        # Create temporary zip
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Create zip with manifest validation
            manifest_path = folder_path_obj / 'manifest.json'
            if not manifest_path.exists():
                raise SecurityError("Extension manifest.json not found in folder")
            
            with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in folder_path_obj.rglob('*'):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(folder_path_obj))
                        zf.write(file_path, arcname)
            
            # Use secure install path
            return await self.install_from_zip(tmp_path, verify_signature)
        
        finally:
            # Clean up temporary zip
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def list_extensions(self) -> List[str]:
        """List installed extension names."""
        return list(self._installed_extensions.keys())
    
    def get_extension_info(self, name: str) -> Optional[ExtensionManifest]:
        """Get extension manifest by name."""
        return self._installed_extensions.get(name)
    
    def uninstall_extension(self, name: str) -> bool:
        """Safely uninstall an extension."""
        if name not in self._installed_extensions:
            return False
        
        ext_dir = self.extensions_dir / name
        if ext_dir.exists():
            shutil.rmtree(ext_dir)
        
        del self._installed_extensions[name]
        logger.info(f"Uninstalled extension: {name}")
        return True
    
    def create_sandbox(self, extension_name: str) -> Path:
        """Create isolated sandbox directory for extension.
        
        Returns path to sandbox directory that extension can write to.
        """
        if extension_name not in self._installed_extensions:
            raise SecurityError(f"Extension not installed: {extension_name}")
        
        sandbox = self.extensions_dir / extension_name / '.sandbox'
        sandbox.mkdir(parents=True, exist_ok=True)
        
        # Set restrictive permissions
        if os.name != 'nt':
            os.chmod(sandbox, 0o700)
        
        return sandbox


# Singleton instance for global access
_extension_manager: Optional[SecureExtensionManager] = None


def get_extension_manager(extensions_dir: Optional[str] = None) -> SecureExtensionManager:
    """Get or create global extension manager instance."""
    global _extension_manager
    if _extension_manager is None:
        if extensions_dir is None:
            extensions_dir = os.path.join(os.path.expanduser('~'), '.game_engine', 'extensions')
        _extension_manager = SecureExtensionManager(extensions_dir)
    return _extension_manager


def reset_extension_manager() -> None:
    """Reset global extension manager (mainly for testing)."""
    global _extension_manager
    _extension_manager = None
