# /**************************************************************************/
# /*  test_project_system.py                                                */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Engine core project system tests.

Tests project creation, serialization, and management.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path

from engine.core.project_secure import SecureProject, ProjectConfig


class TestProjectCreation:
    """Test project creation and initialization."""
    
    @pytest.mark.asyncio
    async def test_project_creation(self):
        """Project can be created."""
        config = ProjectConfig(name="Test Project")
        project = SecureProject("test-uuid-1234", config)
        
        assert project.name == "Test Project"
        assert project.id == "test-uuid-1234"
        assert project.config.lazy_loading is True
    
    @pytest.mark.asyncio
    async def test_project_default_config(self):
        """Project has sensible defaults."""
        config = ProjectConfig()
        project = SecureProject("default", config)
        
        assert project.config.encryption_enabled is True
        assert project.config.lazy_loading is True
        assert project.config.max_assets == 10000
    
    @pytest.mark.asyncio
    async def test_project_scene_management(self):
        """Project can manage scenes."""
        config = ProjectConfig()
        project = SecureProject("test", config)
        
        # Create scenes
        scene1 = project.create_scene("Scene 1")
        scene2 = project.create_scene("Scene 2")
        
        assert len(project.scenes) == 2
        assert "Scene 1" in [s.name for s in project.scenes]
    
    @pytest.mark.asyncio
    async def test_project_active_scene(self):
        """Project tracks active scene."""
        config = ProjectConfig()
        project = SecureProject("test", config)
        
        scene = project.create_scene("Main")
        project.set_active_scene(scene)
        
        assert project.active_scene is scene
    
    @pytest.mark.asyncio
    async def test_project_remove_scene(self):
        """Project can remove scenes."""
        config = ProjectConfig()
        project = SecureProject("test", config)
        
        scene = project.create_scene("To Remove")
        project.remove_scene(scene)
        
        assert scene not in project.scenes


class TestProjectSerialization:
    """Test project save/load."""
    
    @pytest.mark.asyncio
    async def test_project_save_and_load(self, tmp_path):
        """Project can be saved and loaded."""
        config = ProjectConfig(encryption_enabled=False)
        project = SecureProject("save-test", config)
        project.create_scene("Test Scene")
        
        save_path = tmp_path / "project.geps"
        
        # Save
        await project.save_to_file_async(str(save_path))
        assert save_path.exists()
        
        # Load
        loaded = await SecureProject.load_from_file_async(str(save_path))
        assert loaded.id == "save-test"
        assert len(loaded.scenes) == 1
    
    @pytest.mark.asyncio
    async def test_project_encrypted_save(self, tmp_path):
        """Project can be saved with encryption."""
        config = ProjectConfig(encryption_enabled=True)
        project = SecureProject("encrypt-test", config)
        
        save_path = tmp_path / "encrypted.geps"
        
        # Save encrypted
        await project.save_to_file_async(str(save_path), password="testpass123")
        assert save_path.exists()
        
        # Verify it's not plaintext
        content = save_path.read_bytes()
        assert b'encrypt-test' not in content  # Should be encrypted


class TestProjectAssets:
    """Test project asset management."""
    
    @pytest.mark.asyncio
    async def test_asset_registration(self):
        """Assets can be registered with project."""
        config = ProjectConfig()
        project = SecureProject("asset-test", config)
        
        project.register_asset("texture", "player.png", {"size": 1024})
        
        assert "texture" in project.assets
        assert project.assets["texture"]["path"] == "player.png"
    
    @pytest.mark.asyncio
    async def test_asset_max_limit(self):
        """Project enforces asset limit."""
        config = ProjectConfig(max_assets=5)
        project = SecureProject("limit-test", config)
        
        # Add up to limit
        for i in range(5):
            project.register_asset(f"asset{i}", f"file{i}.png")
        
        # Next should be rejected or oldest removed
        project.register_asset("new", "new.png")
        assert len(project.assets) <= 5


class TestProjectLazyLoading:
    """Test lazy loading functionality."""
    
    @pytest.mark.asyncio
    async def test_lazy_loading_enabled(self):
        """Lazy loading defers scene loading."""
        config = ProjectConfig(lazy_loading=True)
        project = SecureProject("lazy-test", config)
        
        # Create scenes
        for i in range(10):
            project.create_scene(f"Scene {i}")
        
        # Check loaded count
        stats = project.get_memory_usage()
        assert stats["scene_count"] == 10
    
    @pytest.mark.asyncio
    async def test_scene_unload(self):
        """Scenes can be unloaded."""
        config = ProjectConfig(lazy_loading=True)
        project = SecureProject("unload-test", config)
        
        scene = project.create_scene("Unloadable")
        project.unload_scene(scene.id)
        
        # Should be tracked but not loaded
        stats = project.get_memory_usage()
        assert stats["loaded_scenes"] < stats["scene_count"]
