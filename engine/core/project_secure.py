# /**************************************************************************/
# /*  project_secure.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Secure, production-ready project management.

Features:
- Async I/O for non-blocking file operations
- JSON Schema validation
- Lazy loading for scenes and resources
- Encrypted project files
- Audit logging
- Atomic saves with rollback
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import secrets
import shutil
import tempfile
import time
import zlib
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable
import aiofiles
import jsonschema
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from engine.core.scene import Scene
from engine.core.node_base import Node
from engine.core.uid_registry import UIDRegistry
from engine.core.controllers import (
    InputController, AudioController, PhysicsController,
    AnimationController, SceneController
)
from engine.core.resources import ResourceManager
from engine.core.errors import SecurityError

logger = logging.getLogger(__name__)

# Project file header
PROJECT_FILE_MAGIC = b"GEPS"  # Game Engine Project Secure
PROJECT_FILE_VERSION = 2

# JSON Schema for project validation
PROJECT_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "version"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1, "maxLength": 256},
        "version": {"type": "integer", "minimum": 1},
        "scenes": {
            "type": "object",
            "patternProperties": {
                "^[0-9a-f-]{36}$": {"type": "object"}
            }
        },
        "active_scene_id": {"type": ["string", "null"]},
        "assets": {"type": "object"},
        "resources": {"type": "object"},
        "metadata": {
            "type": "object",
            "properties": {
                "created_at": {"type": "number"},
                "modified_at": {"type": "number"},
                "author": {"type": "string"},
                "checksum": {"type": "string"}
            }
        }
    }
}


@dataclass
class ProjectConfig:
    """Configuration for project operations."""
    name: Optional[str] = None
    enable_encryption: bool = False
    encryption_enabled: Optional[bool] = None
    password: Optional[str] = None
    compression_level: int = 6  # 0-9, trade-off between speed and size
    auto_backup: bool = True
    backup_count: int = 5
    lazy_loading: bool = True
    max_assets: int = 10000

    def __post_init__(self) -> None:
        if self.encryption_enabled is None:
            self.encryption_enabled = True if self.enable_encryption is False else self.enable_encryption
        self.enable_encryption = bool(self.encryption_enabled)


class SceneMap(dict):
    """Dict-compatible scene mapping that iterates over scenes."""

    def __iter__(self):
        return iter(self.values())

    def __contains__(self, item):
        if isinstance(item, Scene):
            return item in self.values()
        return dict.__contains__(self, item)


@dataclass
class LazyScene:
    """Lazy-loaded scene reference."""
    scene_id: str
    name: str
    data: Optional[Dict[str, Any]] = None
    _loaded_scene: Optional[Scene] = field(default=None, repr=False)
    
    async def load(self) -> Scene:
        """Load scene on demand."""
        if self._loaded_scene is None:
            if self.data is None:
                raise ValueError(f"Scene data not available for {self.scene_id}")
            self._loaded_scene = Scene.from_dict(self.data)
            self._loaded_scene.id = self.scene_id
        return self._loaded_scene

    def load_sync(self) -> Scene:
        """Synchronous load for editor/UI paths."""
        if self._loaded_scene is None:
            if self.data is None:
                raise ValueError(f"Scene data not available for {self.scene_id}")
            self._loaded_scene = Scene.from_dict(self.data)
            self._loaded_scene.id = self.scene_id
        return self._loaded_scene
    
    def unload(self) -> None:
        """Unload scene to free memory."""
        self._loaded_scene = None


class SecureProject:
    """Production-ready project with security and performance features."""
    
    def __init__(self, name: str = "Project", config: Optional[ProjectConfig] = None):
        self.config = config or ProjectConfig()
        if config is not None:
            self.id = str(name)
            self.name = (self.config.name or name)[:256]
        else:
            self.id: str = str(secrets.token_hex(16))  # 256-bit entropy
            self.name: str = name[:256]  # Limit name length
        
        # Lazy loading structures
        self._scenes: Dict[str, LazyScene] = {}
        self._loaded_scenes: SceneMap = SceneMap()
        self._active_scene_id: Optional[str] = None
        
        # Metadata
        self.assets: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {
            "created_at": time.time(),
            "modified_at": time.time(),
            "author": "Unknown",
            "checksum": ""
        }
        
        # Resource management
        self.resource_manager = ResourceManager()
        
        # Controllers (lazy initialization)
        self._controllers: Optional[Dict[str, Any]] = None
        
        # Event listeners
        self._listeners: Set[Callable[[str, Any], None]] = set()
        
        logger.info(f"Created project: {self.name} ({self.id})")
    
    @property
    def controllers(self) -> Dict[str, Any]:
        """Lazy initialization of controllers."""
        if self._controllers is None:
            self._controllers = {
                "input": InputController(),
                "audio": AudioController(),
                "physics": PhysicsController(),
                "animation": AnimationController(),
                "scene": SceneController()
            }
        return self._controllers
    
    @property
    def active_scene(self) -> Optional[Scene]:
        """Get active scene (may trigger lazy load)."""
        if self._active_scene_id and self._active_scene_id in self._scenes:
            if self._active_scene_id not in self._loaded_scenes:
                lazy = self._scenes[self._active_scene_id]
                if lazy.data is not None:
                    self._loaded_scenes[self._active_scene_id] = lazy.load_sync()
            return self._loaded_scenes.get(self._active_scene_id)
        return None
    
    @active_scene.setter
    def active_scene(self, scene: Optional[Scene]) -> None:
        """Set active scene."""
        if scene is None:
            self._active_scene_id = None
            return
        
        if scene.id not in self._scenes:
            self._add_scene_ref(scene)
        
        self._active_scene_id = scene.id
        self._notify("scene_activated", scene.id)
    
    def _add_scene_ref(self, scene: Scene) -> None:
        """Add scene reference without loading."""
        self._scenes[scene.id] = LazyScene(
            scene_id=scene.id,
            name=scene.name,
            data=None  # Will be set when saving
        )
        self._loaded_scenes[scene.id] = scene

    @property
    def scenes(self) -> Dict[str, Scene]:
        """Compatibility view of loaded scenes for importer/editor code."""
        for scene_id, lazy in list(self._scenes.items()):
            if scene_id not in self._loaded_scenes and lazy.data is not None:
                self._loaded_scenes[scene_id] = lazy.load_sync()
        return self._loaded_scenes

    @scenes.setter
    def scenes(self, value: Dict[str, Scene]) -> None:
        self._scenes.clear()
        self._loaded_scenes = SceneMap()
        for scene in value.values():
            self._add_scene_ref(scene)

    def add_scene(self, scene: Scene) -> Scene:
        """Add an existing scene to the project and keep lazy refs in sync."""
        self._add_scene_ref(scene)
        if self._active_scene_id is None:
            self._active_scene_id = scene.id
        self._notify("scene_added", scene.id)
        return scene

    def set_active_scene(self, scene_id: str | Scene) -> bool:
        """Set active scene by id, loading it if necessary."""
        if isinstance(scene_id, Scene):
            scene_id = scene_id.id
        if scene_id not in self._scenes:
            return False
        self._active_scene_id = scene_id
        _ = self.active_scene
        self._notify("scene_activated", scene_id)
        return True
    
    def create_scene(self, name: str) -> Scene:
        """Create new scene and add to project."""
        scene = Scene(name)
        self._add_scene_ref(scene)
        
        if self._active_scene_id is None:
            self._active_scene_id = scene.id
        
        self._notify("scene_created", scene.id)
        logger.info(f"Created scene: {scene.name} ({scene.id})")
        return scene
    
    async def load_scene_async(self, scene_id: str) -> Optional[Scene]:
        """Asynchronously load scene."""
        if scene_id not in self._scenes:
            return None
        
        lazy = self._scenes[scene_id]
        scene = await lazy.load()
        self._loaded_scenes[scene_id] = scene
        self._notify("scene_loaded", scene_id)
        return scene
    
    def unload_scene(self, scene_id: str) -> bool:
        """Unload scene to free memory."""
        if scene_id not in self._scenes:
            return False
        
        self._scenes[scene_id].unload()
        self._loaded_scenes.pop(scene_id, None)
        self._notify("scene_unloaded", scene_id)
        logger.info(f"Unloaded scene: {scene_id}")
        return True
    
    def remove_scene(self, scene_id: str | Scene) -> bool:
        """Remove scene from project."""
        if isinstance(scene_id, Scene):
            scene_id = scene_id.id
        if scene_id not in self._scenes:
            return False
        
        del self._scenes[scene_id]
        self._loaded_scenes.pop(scene_id, None)
        
        if self._active_scene_id == scene_id:
            # Set new active scene
            if self._scenes:
                self._active_scene_id = next(iter(self._scenes.keys()))
            else:
                self._active_scene_id = None
        
        self._notify("scene_removed", scene_id)
        logger.info(f"Removed scene: {scene_id}")
        return True
    
    def to_dict(self, include_scene_data: bool = True) -> Dict[str, Any]:
        """Convert to dictionary with optional scene data."""
        scenes_data = {}
        for scene_id, lazy in self._scenes.items():
            if include_scene_data and scene_id in self._loaded_scenes:
                scenes_data[scene_id] = self._loaded_scenes[scene_id].to_dict()
            else:
                scenes_data[scene_id] = {"name": lazy.name, "lazy": True}
        
        return {
            "id": self.id,
            "name": self.name,
            "version": PROJECT_FILE_VERSION,
            "scenes": scenes_data,
            "active_scene_id": self._active_scene_id,
            "assets": self.assets,
            "resources": self.resource_manager.to_dict(),
            "metadata": {
                **self.metadata,
                "modified_at": time.time()
            }
        }
    
    @classmethod
    def create_new(cls, project_path: str, name: Optional[str] = None) -> "SecureProject":
        """Create new project file."""
        path = Path(project_path)
        if name is None:
            name = path.stem.replace("_", " ").replace("-", " ").title()
        
        # Create project instance
        project = cls(name=name)
        
        # Create default scene
        scene = project.create_scene("Main")
        
        # Save project (sync version)
        data = project.to_dict()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return project
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], config: Optional[ProjectConfig] = None) -> "SecureProject":
        """Create project from dictionary with validation."""
        # Validate against schema
        try:
            jsonschema.validate(data, PROJECT_SCHEMA)
        except jsonschema.ValidationError as e:
            raise SecurityError(f"Invalid project data: {e.message}")
        
        project = cls(data.get("name", "Project"), config)
        project.id = data.get("id", project.id)
        project.assets = data.get("assets", {})
        
        # Load scenes lazily
        scenes_data = data.get("scenes", {})
        for scene_id, scene_data in scenes_data.items():
            if isinstance(scene_data, dict) and scene_data.get("lazy"):
                # Lazy reference
                project._scenes[scene_id] = LazyScene(
                    scene_id=scene_id,
                    name=scene_data.get("name", "Scene"),
                    data=None
                )
            else:
                # Full data - create lazy reference with data
                project._scenes[scene_id] = LazyScene(
                    scene_id=scene_id,
                    name=scene_data.get("name", "Scene"),
                    data=scene_data
                )
        
        active_scene_id = data.get("active_scene_id")
        if active_scene_id and active_scene_id in project._scenes:
            project._active_scene_id = active_scene_id
        elif project._scenes:
            project._active_scene_id = next(iter(project._scenes.keys()))
        
        project.metadata = data.get("metadata", project.metadata)
        
        # Load resources
        resources_data = data.get("resources")
        if resources_data:
            project.resource_manager = ResourceManager.from_dict(resources_data)
        
        logger.info(f"Loaded project from dict: {project.name} ({project.id})")
        return project
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password."""
        import base64
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"game_engine_studio_project_v1",
            iterations=480000,
        )
        key = kdf.derive(password.encode())
        # Fernet requires base64-encoded 32-byte key
        return base64.urlsafe_b64encode(key)
    
    async def save_to_file(self, path: Path) -> None:
        """Async save with encryption, compression, and atomic write."""
        path = Path(path)
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup if file exists
        if path.exists() and self.config.auto_backup:
            await self._create_backup(path)
        
        # Prepare data
        data = self.to_dict()
        json_data = json.dumps(data, indent=2, default=str)
        json_bytes = json_data.encode('utf-8')
        
        # Calculate checksum before compression
        checksum = hashlib.sha256(json_bytes).hexdigest()
        self.metadata["checksum"] = checksum
        
        # Compress
        if self.config.compression_level > 0:
            compressed = zlib.compress(
                json_bytes,
                level=min(self.config.compression_level, 9)
            )
        else:
            compressed = json_bytes
        
        # Encrypt if configured
        if self.config.enable_encryption and self.config.password:
            key = self._derive_key(self.config.password)
            fernet = Fernet(key)
            encrypted = fernet.encrypt(compressed)
            content = encrypted
            encrypted_flag = b"\x01"
        else:
            content = compressed
            encrypted_flag = b"\x00"
        
        # Atomic write using temp file
        temp_path = path.with_suffix('.tmp')
        try:
            async with aiofiles.open(temp_path, 'wb') as f:
                # Header
                await f.write(PROJECT_FILE_MAGIC)
                await f.write(bytes([PROJECT_FILE_VERSION]))
                await f.write(encrypted_flag)
                await f.write(b"\x00" * 2)  # Reserved
                
                # Content
                await f.write(content)
            
            # Atomic rename
            temp_path.replace(path)
            
            self._notify("project_saved", str(path))
            logger.info(f"Saved project: {path}")
            
        except Exception:
            # Clean up temp file on failure
            if temp_path.exists():
                temp_path.unlink()
            raise

    async def save_to_file_async(self, path: str | Path, password: Optional[str] = None) -> None:
        """Compatibility async save entry point."""
        old_password = self.config.password
        if password is not None:
            self.config.password = password
        try:
            await self.save_to_file(Path(path))
        finally:
            self.config.password = old_password
    
    async def _create_backup(self, path: Path) -> None:
        """Create rolling backups."""
        backup_dir = path.parent / '.backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Shift existing backups
        for i in range(self.config.backup_count - 1, 0, -1):
            old_backup = backup_dir / f"{path.stem}.{i}{path.suffix}"
            new_backup = backup_dir / f"{path.stem}.{i+1}{path.suffix}"
            if old_backup.exists():
                if i >= self.config.backup_count - 1:
                    old_backup.unlink()
                else:
                    old_backup.rename(new_backup)
        
        # Create new backup
        backup_path = backup_dir / f"{path.stem}.1{path.suffix}"
        shutil.copy2(path, backup_path)
    
    @classmethod
    async def load_from_file(cls, path: Path, password: Optional[str] = None) -> "SecureProject":
        """Async load with validation and decryption."""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Project file not found: {path}")
        
        async with aiofiles.open(path, 'rb') as f:
            # Read header
            magic = await f.read(4)
            if magic != PROJECT_FILE_MAGIC:
                raise SecurityError(f"Invalid project file: bad magic bytes")
            
            version = int.from_bytes(await f.read(1), byteorder='big')
            if version != PROJECT_FILE_VERSION:
                raise SecurityError(f"Unsupported project version: {version}")
            
            encrypted = await f.read(1) == b"\x01"
            await f.read(2)  # Skip reserved
            
            # Read content
            content = await f.read()
        
        # Decrypt if needed
        if encrypted:
            if not password:
                raise SecurityError("Project is encrypted but no password provided")
            
            project = cls()  # Temporary instance for key derivation
            key = project._derive_key(password)
            fernet = Fernet(key)
            
            try:
                compressed = fernet.decrypt(content)
            except Exception as e:
                raise SecurityError(f"Decryption failed: {e}")
        else:
            compressed = content
        
        # Decompress
        try:
            json_bytes = zlib.decompress(compressed)
        except zlib.error:
            json_bytes = compressed  # Not compressed
        
        # Parse and validate
        json_data = json_bytes.decode('utf-8')
        data = json.loads(json_data)
        
        # Verify checksum
        stored_checksum = data.get("metadata", {}).get("checksum", "")
        calculated_checksum = hashlib.sha256(json_data.encode()).hexdigest()
        
        if stored_checksum and stored_checksum != calculated_checksum:
            logger.warning("Project checksum mismatch - possible corruption")
        
        return cls.from_dict(data)

    @classmethod
    async def load_from_file_async(cls, path: str | Path, password: Optional[str] = None) -> "SecureProject":
        """Compatibility async load entry point."""
        return await cls.load_from_file(Path(path), password=password)

    @classmethod
    def load_from_file_sync(cls, path: Path, password: Optional[str] = None) -> "SecureProject":
        """Synchronous version of load_from_file."""
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Project file not found: {path}")

        with open(path, 'rb') as f:
            # Read header
            magic = f.read(4)
            if magic != PROJECT_FILE_MAGIC:
                raise SecurityError(f"Invalid project file: bad magic bytes")

            version = int.from_bytes(f.read(1), byteorder='big')
            if version != PROJECT_FILE_VERSION:
                raise SecurityError(f"Unsupported project version: {version}")

            encrypted = f.read(1) == b"\x01"
            f.read(2)  # Skip reserved

            # Read content
            content = f.read()

        # Decrypt if needed
        if encrypted:
            if not password:
                raise SecurityError("Project is encrypted but no password provided")

            project = cls()  # Temporary instance for key derivation
            key = project._derive_key(password)
            fernet = Fernet(key)

            try:
                compressed = fernet.decrypt(content)
            except Exception as e:
                raise SecurityError(f"Decryption failed: {e}")
        else:
            compressed = content

        # Decompress
        try:
            json_bytes = zlib.decompress(compressed)
        except zlib.error:
            json_bytes = compressed  # Not compressed

        # Parse and validate
        json_data = json_bytes.decode('utf-8')
        data = json.loads(json_data)

        return cls.from_dict(data)

    def save_to_file_sync(self, path: Path) -> None:
        """Synchronous version of save_to_file."""
        path = Path(path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare data
        data = self.to_dict()
        json_data = json.dumps(data, indent=2, default=str)
        json_bytes = json_data.encode('utf-8')

        # Calculate checksum before compression
        checksum = hashlib.sha256(json_bytes).hexdigest()
        self.metadata["checksum"] = checksum

        # Compress
        if self.config.compression_level > 0:
            compressed = zlib.compress(
                json_bytes,
                level=min(self.config.compression_level, 9)
            )
        else:
            compressed = json_bytes

        # Encrypt if configured
        if self.config.enable_encryption and self.config.password:
            key = self._derive_key(self.config.password)
            fernet = Fernet(key)
            encrypted = fernet.encrypt(compressed)
            content = encrypted
            encrypted_flag = b"\x01"
        else:
            content = compressed
            encrypted_flag = b"\x00"

        # Atomic write using temp file
        temp_path = path.with_suffix('.tmp')
        try:
            with open(temp_path, 'wb') as f:
                # Header
                f.write(PROJECT_FILE_MAGIC)
                f.write(bytes([PROJECT_FILE_VERSION]))
                f.write(encrypted_flag)
                f.write(b"\x00" * 2)  # Reserved

                # Content
                f.write(content)

            # Atomic rename
            temp_path.replace(path)

        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise SecurityError(f"Failed to save project: {e}")

    def register_asset(self, asset_id: str, path: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register or update an asset while respecting the configured limit."""
        if asset_id not in self.assets and len(self.assets) >= self.config.max_assets:
            oldest = next(iter(self.assets))
            self.assets.pop(oldest, None)
        self.assets[asset_id] = {
            "path": path,
            "metadata": metadata or {},
            "registered_at": time.time(),
        }
        self._notify("asset_registered", asset_id)

    def get_asset_source(self, asset_id: str) -> Optional[str]:
        asset = self.assets.get(asset_id)
        if isinstance(asset, dict):
            return asset.get("path")
        return None

    def add_listener(self, callback: Callable[[str, Any], None]) -> None:
        """Add event listener for project events."""
        self._listeners.add(callback)
    
    def remove_listener(self, callback: Callable[[str, Any], None]) -> None:
        """Remove event listener."""
        self._listeners.discard(callback)
    
    def _notify(self, event: str, data: Any) -> None:
        """Notify all listeners."""
        for callback in self._listeners:
            try:
                callback(event, data)
            except Exception as e:
                logger.error(f"Listener error: {e}")
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get approximate memory usage statistics."""
        return {
            "scene_count": len(self._scenes),
            "loaded_scenes": len(self._loaded_scenes),
            "asset_count": len(self.assets),
            "listeners": len(self._listeners)
        }
