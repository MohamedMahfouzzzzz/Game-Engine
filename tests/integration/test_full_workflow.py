# /**************************************************************************/
# /*  test_full_workflow.py                                                 */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Full workflow integration tests.

End-to-end tests that simulate real user workflows.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path

from engine.core.project_secure import SecureProject, ProjectConfig
from engine.core.node_base import Node, Node2D
from engine.tools.pixel_art_editor.scripting.api.sprite import Sprite


class TestFullGameWorkflow:
    """Test complete game development workflow."""
    
    @pytest.mark.asyncio
    async def test_create_project_with_scene(self):
        """Create project, add scene, add nodes."""
        config = ProjectConfig(name="My Game")
        project = SecureProject("game-uuid", config)
        
        # Create scene
        scene = project.create_scene("Level 1")
        
        # Add nodes
        player = Node2D("Player")
        enemy = Node2D("Enemy")
        scene.root.add_child(player)
        scene.root.add_child(enemy)
        
        assert len(scene.root.children) == 2
        assert project.active_scene is None  # Not set yet
        
        project.set_active_scene(scene)
        assert project.active_scene is scene
    
    @pytest.mark.asyncio
    async def test_save_and_load_full_project(self, tmp_path):
        """Save project with all content and reload."""
        # Create project with content
        config = ProjectConfig(encryption_enabled=False)
        project = SecureProject("save-test", config)
        
        scene = project.create_scene("Test Scene")
        
        # Add various node types
        player = Node2D("Player")
        player.x = 100
        player.y = 200
        scene.root.add_child(player)
        
        # Register assets
        project.register_asset("player_tex", "player.png", {"size": 1024})
        project.register_asset("bg_music", "music.ogg", {"duration": 120})
        
        # Save
        save_path = tmp_path / "full_project.geps"
        await project.save_to_file_async(str(save_path))
        
        # Load
        loaded = await SecureProject.load_from_file_async(str(save_path))
        
        # Verify
        assert loaded.id == "save-test"
        assert len(loaded.scenes) == 1
        assert len(loaded.assets) == 2
    
    @pytest.mark.asyncio
    async def test_multi_scene_workflow(self):
        """Create multiple scenes and switch between them."""
        config = ProjectConfig()
        project = SecureProject("multi", config)
        
        # Create menu and game scenes
        menu = project.create_scene("Menu")
        game = project.create_scene("Game")
        game_over = project.create_scene("Game Over")
        
        # Set up menu
        start_btn = Node("StartButton")
        menu.root.add_child(start_btn)
        
        # Set up game
        player = Node2D("Player")
        game.root.add_child(player)
        
        # Switch scenes
        project.set_active_scene(menu)
        assert project.active_scene.name == "Menu"
        
        project.set_active_scene(game)
        assert project.active_scene.name == "Game"
        
        project.set_active_scene(game_over)
        assert project.active_scene.name == "Game Over"


class TestAssetWorkflow:
    """Test asset management workflow."""
    
    @pytest.mark.asyncio
    async def test_asset_lifecycle(self):
        """Register, modify, remove assets."""
        config = ProjectConfig()
        project = SecureProject("asset-test", config)
        
        # Register
        project.register_asset("hero", "hero.png", {"w": 32, "h": 32})
        assert "hero" in project.assets
        
        # Update metadata
        project.assets["hero"]["tags"] = ["character", "player"]
        assert "tags" in project.assets["hero"]
        
        # Get source path
        source = project.get_asset_source("hero")
        assert source == "hero.png"


class TestPixelArtWorkflow:
    """Test pixel art editor workflow."""
    
    def test_create_sprite_with_layers_and_frames(self):
        """Create complex sprite with animation."""
        sprite = Sprite(32, 32)
        
        # Set up layers
        bg = sprite.newLayer("Background")
        player = sprite.newLayer("Player")
        fg = sprite.newLayer("Foreground")
        
        # Create animation frames
        for i in range(8):  # 8 frame animation
            sprite.newFrame()
        
        assert len(sprite.layers) >= 4
        assert len(sprite.frames) >= 9
    
    def test_layer_hierarchy(self):
        """Create layer groups and organize."""
        sprite = Sprite(64, 64)
        
        # Create groups
        characters = sprite.newGroup()
        characters.name = "Characters"
        
        effects = sprite.newGroup()
        effects.name = "Effects"
        
        # Add layers to groups
        hero = sprite.newLayer("Hero")
        hero.parent = characters
        
        sparkles = sprite.newLayer("Sparkles")
        sparkles.parent = effects
        
        assert hero.parent == characters
        assert sparkles.parent == effects


class TestExportWorkflow:
    """Test export workflow."""
    
    @pytest.mark.asyncio
    async def test_project_export_preparation(self):
        """Prepare project for export."""
        config = ProjectConfig()
        project = SecureProject("export-test", config)
        
        # Create content
        scene = project.create_scene("Level 1")
        
        # Add content
        for i in range(10):
            node = Node2D(f"Entity{i}")
            scene.root.add_child(node)
        
        # Verify export readiness
        assert len(project.scenes) == 1
        assert len(scene.root.children) == 10


class TestErrorRecovery:
    """Test error handling and recovery in workflows."""
    
    @pytest.mark.asyncio
    async def test_scene_recovery_after_error(self):
        """Recover from scene creation error."""
        config = ProjectConfig()
        project = SecureProject("recovery", config)
        
        try:
            # Simulate error
            raise RuntimeError("Simulated error")
        except RuntimeError:
            # Should be able to continue
            scene = project.create_scene("Recovered")
            assert scene is not None
    
    @pytest.mark.asyncio
    async def test_asset_recovery_after_failed_registration(self):
        """Handle failed asset registration gracefully."""
        config = ProjectConfig(max_assets=2)
        project = SecureProject("limited", config)
        
        # Fill up
        project.register_asset("a1", "f1.png")
        project.register_asset("a2", "f2.png")
        
        # Third should fail gracefully
        project.register_asset("a3", "f3.png")
        # Should not crash, even if rejected
