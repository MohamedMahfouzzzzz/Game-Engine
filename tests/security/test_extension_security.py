# /**************************************************************************/
# /*  test_extension_security.py                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Security tests for extension manager.

Tests path traversal prevention, zip bomb detection,
manifest validation, and sandbox isolation.
"""

import asyncio
import os
import tempfile
import zipfile
from pathlib import Path

import pytest

from engine.core.errors import SecurityError
from engine.extensions.manager_secure import SecureExtensionManager, ExtensionManifest


@pytest.fixture
def temp_extensions_dir():
    """Create temporary extensions directory."""
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


@pytest.fixture
def extension_manager(temp_extensions_dir):
    """Create secure extension manager."""
    return SecureExtensionManager(temp_extensions_dir)


class TestPathTraversalPrevention:
    """Test path traversal attack prevention."""
    
    def test_blocks_absolute_paths(self, extension_manager, temp_extensions_dir):
        """Reject zip entries with absolute paths."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                # Attempt path traversal
                zf.writestr('../../../etc/passwd', 'malicious')
            
            with pytest.raises(SecurityError) as exc:
                asyncio.run(extension_manager.install_from_zip(zip_path))
            
            assert "traversal" in str(exc.value).lower()
        finally:
            os.unlink(zip_path)
    
    def test_blocks_dotdot_paths(self, extension_manager):
        """Reject zip entries with .. in paths."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('subdir/../../evil.txt', 'malicious')
            
            with pytest.raises(SecurityError):
                asyncio.run(extension_manager.install_from_zip(zip_path))
        finally:
            os.unlink(zip_path)
    
    def test_allows_valid_paths(self, extension_manager, temp_extensions_dir):
        """Accept valid zip entries."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('manifest.json', '{"name": "test", "version": "1.0", "author": "test"}')
                zf.writestr('subdir/file.txt', 'content')
            
            # Should succeed
            manifest = asyncio.run(
                extension_manager.install_from_zip(zip_path, verify_signature=False)
            )
            assert manifest.name == "test"
        finally:
            os.unlink(zip_path)


class TestZipBombPrevention:
    """Test zip bomb detection."""
    
    def test_blocks_high_compression_ratio(self, extension_manager):
        """Reject zips with suspicious compression ratios."""
        import json
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                # Create entry claiming huge uncompressed size but tiny compressed
                manifest = {"name": "test", "version": "1.0", "author": "test"}
                info = zipfile.ZipInfo('manifest.json')
                info.compress_size = 10
                info.file_size = 10_000_000  # 10MB claimed
                zf.writestr(info, json.dumps(manifest))
            
            with pytest.raises(SecurityError) as exc:
                asyncio.run(extension_manager.install_from_zip(zip_path))
            
            assert "compression" in str(exc.value).lower()
        finally:
            os.unlink(zip_path)
    
    def test_blocks_too_many_files(self, extension_manager):
        """Reject zips with excessive file count."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                # Add more than 10,000 files
                for i in range(10_001):
                    zf.writestr(f'file{i}.txt', 'x')
            
            with pytest.raises(SecurityError) as exc:
                asyncio.run(extension_manager.install_from_zip(zip_path))
            
            assert "too many files" in str(exc.value).lower()
        finally:
            os.unlink(zip_path)
    
    def test_blocks_oversized_extraction(self, extension_manager):
        """Reject zips that would extract to excessive size."""
        import json
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                # Add manifest first
                zf.writestr('manifest.json', json.dumps({"name": "test", "version": "1.0", "author": "test"}))
                # Files totaling > 500MB
                for i in range(6):
                    info = zipfile.ZipInfo(f'large{i}.bin')
                    info.compress_size = 100
                    info.file_size = 100_000_000  # 100MB each
                    zf.writestr(info, 'x' * 100)
            
            with pytest.raises(SecurityError) as exc:
                asyncio.run(extension_manager.install_from_zip(zip_path))
            
            assert "size" in str(exc.value).lower() or "exceed" in str(exc.value).lower()
        finally:
            os.unlink(zip_path)


class TestManifestValidation:
    """Test extension manifest validation."""
    
    def test_rejects_missing_manifest(self, extension_manager):
        """Reject extensions without manifest.json."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('some_file.txt', 'content')
            
            with pytest.raises(SecurityError) as exc:
                asyncio.run(extension_manager.install_from_zip(zip_path))
            
            assert "manifest" in str(exc.value).lower()
        finally:
            os.unlink(zip_path)
    
    def test_rejects_invalid_manifest_json(self, extension_manager):
        """Reject extensions with invalid manifest."""
        import json
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                # Write a file that looks like JSON but is corrupted
                zf.writestr('manifest.json', '{"name": "test", invalid}')
            
            with pytest.raises((SecurityError, json.JSONDecodeError)):
                asyncio.run(extension_manager.install_from_zip(zip_path))
        finally:
            os.unlink(zip_path)
    
    def test_rejects_missing_required_fields(self, extension_manager):
        """Reject manifest without required fields."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('manifest.json', '{"version": "1.0"}')  # missing name
            
            with pytest.raises(SecurityError) as exc:
                asyncio.run(extension_manager.install_from_zip(zip_path))
            
            assert "missing" in str(exc.value).lower()
        finally:
            os.unlink(zip_path)
    
    def test_rejects_invalid_extension_name(self, extension_manager):
        """Reject extensions with path traversal in name."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr(
                    'manifest.json',
                    '{"name": "../evil", "version": "1.0", "author": "test"}'
                )
            
            with pytest.raises(SecurityError):
                asyncio.run(extension_manager.install_from_zip(zip_path))
        finally:
            os.unlink(zip_path)
    
    def test_accepts_valid_manifest(self, extension_manager):
        """Accept valid manifest."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr(
                    'manifest.json',
                    '{"name": "ValidExtension", "version": "1.0.0", "author": "Test"}'
                )
            
            manifest = asyncio.run(
                extension_manager.install_from_zip(zip_path, verify_signature=False)
            )
            
            assert isinstance(manifest, ExtensionManifest)
            assert manifest.name == "ValidExtension"
            assert manifest.version == "1.0.0"
        finally:
            os.unlink(zip_path)


class TestBlockedFileTypes:
    """Test blocked file type detection."""
    
    def test_blocks_executable_files(self, extension_manager):
        """Reject extensions containing .exe files."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('manifest.json', '{"name": "bad", "version": "1.0", "author": "x"}')
                zf.writestr('evil.exe', 'MZ')  # Windows executable
            
            with pytest.raises(SecurityError) as exc:
                asyncio.run(extension_manager.install_from_zip(zip_path))
            
            assert "blocked" in str(exc.value).lower()
        finally:
            os.unlink(zip_path)
    
    def test_blocks_script_files(self, extension_manager):
        """Reject extensions containing script files."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('manifest.json', '{"name": "bad", "version": "1.0", "author": "x"}')
                zf.writestr('evil.py', 'import os; os.system("rm -rf /")')
            
            with pytest.raises(SecurityError):
                asyncio.run(extension_manager.install_from_zip(zip_path))
        finally:
            os.unlink(zip_path)
    
    def test_blocks_pycache_directories(self, extension_manager):
        """Reject extensions containing __pycache__."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('manifest.json', '{"name": "bad", "version": "1.0", "author": "x"}')
                zf.writestr('__pycache__/module.cpython-311.pyc', 'bytes')
            
            with pytest.raises(SecurityError):
                asyncio.run(extension_manager.install_from_zip(zip_path))
        finally:
            os.unlink(zip_path)


class TestChecksumValidation:
    """Test file checksum verification."""
    
    def test_rejects_checksum_mismatch(self, extension_manager):
        """Reject files with checksum mismatches."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                manifest = {
                    "name": "Test",
                    "version": "1.0",
                    "author": "test",
                    "checksums": {
                        "data.txt": "invalid_checksum"
                    }
                }
                import json
                zf.writestr('manifest.json', json.dumps(manifest))
                zf.writestr('data.txt', 'actual content')
            
            with pytest.raises(SecurityError) as exc:
                asyncio.run(extension_manager.install_from_zip(zip_path))
            
            assert "checksum" in str(exc.value).lower()
        finally:
            os.unlink(zip_path)
    
    def test_accepts_valid_checksums(self, extension_manager, temp_extensions_dir):
        """Accept files with valid checksums."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            import hashlib
            import json
            
            content = b'file content'
            checksum = hashlib.sha256(content).hexdigest()
            
            manifest = {
                "name": "ChecksumTest",
                "version": "1.0",
                "author": "test",
                "checksums": {
                    "data.txt": checksum
                }
            }
            
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('manifest.json', json.dumps(manifest))
                zf.writestr('data.txt', content)
            
            result = asyncio.run(
                extension_manager.install_from_zip(zip_path, verify_signature=False)
            )
            assert result.name == "ChecksumTest"
        finally:
            os.unlink(zip_path)


class TestSandboxing:
    """Test extension sandboxing."""
    
    def test_creates_sandbox_directory(self, extension_manager, temp_extensions_dir):
        """Create sandbox for extension."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            import json
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr(
                    'manifest.json',
                    json.dumps({"name": "SandboxTest", "version": "1.0", "author": "test"})
                )
            
            asyncio.run(
                extension_manager.install_from_zip(zip_path, verify_signature=False)
            )
            
            sandbox = extension_manager.create_sandbox("SandboxTest")
            assert sandbox.exists()
            assert sandbox.name == '.sandbox'
        finally:
            os.unlink(zip_path)
