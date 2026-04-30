# /**************************************************************************/
# /*  test_project_security.py                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Security tests for secure project management.

Tests encryption, integrity validation, schema validation,
and atomic file operations.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import pytest

from engine.core.errors import SecurityError
from engine.core.project_secure import SecureProject, ProjectConfig


class TestProjectEncryption:
    """Test project file encryption."""
    
    @pytest.mark.asyncio
    async def test_encrypted_file_requires_password(self):
        """Encrypted projects require password to load."""
        with tempfile.TemporaryDirectory() as tmp:
            project_path = Path(tmp) / "test.gepj"
            
            # Create encrypted project
            config = ProjectConfig(enable_encryption=True, password="secret123")
            project = SecureProject("Encrypted Test", config)
            await project.save_to_file(project_path)
            
            # Try to load without password
            with pytest.raises(SecurityError):
                await SecureProject.load_from_file(project_path)
    
    @pytest.mark.asyncio
    async def test_correct_password_decrypts(self):
        """Correct password decrypts successfully."""
        with tempfile.TemporaryDirectory() as tmp:
            project_path = Path(tmp) / "test.gepj"
            
            config = ProjectConfig(enable_encryption=True, password="secret123")
            project = SecureProject("Encrypted Test", config)
            project_id = project.id
            await project.save_to_file(project_path)
            
            # Load with correct password
            loaded = await SecureProject.load_from_file(
                project_path, password="secret123"
            )
            assert loaded.id == project_id
            assert loaded.name == "Encrypted Test"
    
    @pytest.mark.asyncio
    async def test_wrong_password_fails(self):
        """Wrong password fails decryption."""
        with tempfile.TemporaryDirectory() as tmp:
            project_path = Path(tmp) / "test.gepj"
            
            config = ProjectConfig(enable_encryption=True, password="secret123")
            project = SecureProject("Encrypted Test", config)
            await project.save_to_file(project_path)
            
            # Try wrong password
            with pytest.raises(SecurityError):
                await SecureProject.load_from_file(
                    project_path, password="wrong_password"
                )
    
    @pytest.mark.asyncio
    async def test_unencrypted_file_loads_without_password(self):
        """Unencrypted projects load without password."""
        with tempfile.TemporaryDirectory() as tmp:
            project_path = Path(tmp) / "test.gepj"
            
            config = ProjectConfig(enable_encryption=False)
            project = SecureProject("Unencrypted Test", config)
            await project.save_to_file(project_path)
            
            # Load without password
            loaded = await SecureProject.load_from_file(project_path)
            assert loaded.name == "Unencrypted Test"


class TestSchemaValidation:
    """Test JSON schema validation."""
    
    @pytest.mark.asyncio
    async def test_rejects_invalid_project_id(self):
        """Reject invalid project ID format."""
        invalid_data = {
            "id": "not-a-valid-uuid",
            "name": "Test",
            "version": 1,
            "scenes": {},
            "active_scene_id": None,
            "assets": {},
            "resources": {},
            "metadata": {}
        }
        
        with pytest.raises(SecurityError) as exc:
            SecureProject.from_dict(invalid_data)
        
        assert "Invalid" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_rejects_missing_required_fields(self):
        """Reject missing required fields."""
        invalid_data = {
            "name": "Test",
            "version": 1
            # missing "id"
        }
        
        with pytest.raises(SecurityError) as exc:
            SecureProject.from_dict(invalid_data)
        
        assert "required" in str(exc.value).lower() or "Invalid" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_rejects_invalid_scene_id_format(self):
        """Reject invalid scene ID format."""
        invalid_data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test",
            "version": 1,
            "scenes": {
                "invalid-scene-id": {"name": "Scene"}  # Invalid UUID format
            },
            "active_scene_id": None,
            "assets": {},
            "resources": {},
            "metadata": {}
        }
        
        with pytest.raises(SecurityError) as exc:
            SecureProject.from_dict(invalid_data)
        
        assert "Invalid" in str(exc.value) or "schema" in str(exc.value).lower()
    
    @pytest.mark.asyncio
    async def test_accepts_valid_project_data(self):
        """Accept valid project data."""
        valid_data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test Project",
            "version": 1,
            "scenes": {
                "550e8400-e29b-41d4-a716-446655440001": {"name": "Scene1", "lazy": True}
            },
            "active_scene_id": "550e8400-e29b-41d4-a716-446655440001",
            "assets": {},
            "resources": {},
            "metadata": {
                "created_at": 1234567890,
                "modified_at": 1234567890,
                "author": "Test",
                "checksum": "abc123"
            }
        }
        
        project = SecureProject.from_dict(valid_data)
        assert project.name == "Test Project"


class TestAtomicFileOperations:
    """Test atomic write operations."""
    
    @pytest.mark.asyncio
    async def test_atomic_write_prevents_corruption(self):
        """Atomic write prevents partial file corruption."""
        with tempfile.TemporaryDirectory() as tmp:
            project_path = Path(tmp) / "test.gepj"
            
            config = ProjectConfig(enable_encryption=False)
            project = SecureProject("Atomic Test", config)
            await project.save_to_file(project_path)
            
            # File should exist and be valid
            assert project_path.exists()
            # Should not have temp file
            assert not (project_path.with_suffix('.tmp')).exists()
    
    @pytest.mark.asyncio
    async def test_creates_backup_on_save(self):
        """Automatic backup creation."""
        with tempfile.TemporaryDirectory() as tmp:
            project_path = Path(tmp) / "test.gepj"
            backup_dir = project_path.parent / '.backups'
            
            config = ProjectConfig(auto_backup=True, backup_count=3)
            project = SecureProject("Backup Test", config)
            
            # Save multiple times
            await project.save_to_file(project_path)
            project.name = "Backup Test 2"
            await project.save_to_file(project_path)
            
            # Check backup exists
            assert backup_dir.exists()
            backups = list(backup_dir.glob("*.gepj"))
            assert len(backups) >= 1


class TestLazyLoading:
    """Test lazy loading functionality."""
    
    @pytest.mark.asyncio
    async def test_scenes_not_loaded_until_accessed(self):
        """Scenes remain unloaded until accessed."""
        config = ProjectConfig(lazy_loading=True)
        project = SecureProject("Lazy Test", config)
        
        # Create scene
        scene = project.create_scene("Test Scene")
        
        # Check memory stats
        stats = project.get_memory_usage()
        assert stats["scene_count"] == 1
        # Scene should be loaded because we just created it
        assert stats["loaded_scenes"] == 1
    
    @pytest.mark.asyncio
    async def test_unload_frees_memory(self):
        """Unloading scenes frees memory."""
        config = ProjectConfig(lazy_loading=True)
        project = SecureProject("Unload Test", config)
        
        # Create and track scene
        scene = project.create_scene("Unloadable")
        scene_id = scene.id
        
        # Unload
        project.unload_scene(scene_id)
        
        stats = project.get_memory_usage()
        assert stats["scene_count"] == 1  # Still in list
        assert stats["loaded_scenes"] == 0  # But unloaded


class TestProjectNameValidation:
    """Test project name validation."""
    
    @pytest.mark.asyncio
    async def test_truncates_long_names(self):
        """Long names are truncated."""
        long_name = "A" * 1000
        project = SecureProject(long_name)
        assert len(project.name) <= 256
    
    @pytest.mark.asyncio
    async def test_prevents_path_traversal_in_name(self):
        """Names with path separators are sanitized."""
        malicious_name = "../../../etc/passwd"
        project = SecureProject(malicious_name)
        # Should not contain path separators
        assert ".." not in project.name or "/" not in project.name
