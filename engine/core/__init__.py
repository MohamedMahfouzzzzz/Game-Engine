# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from engine.core.errors import SecurityError, ScriptingSecurityError
from engine.core.instancing import instance_scene
from engine.core.node_base import Node, Node2D
from engine.core.nodes import (
    AnimatedSprite,
    Button,
    Control,
    Label,
    Panel,
    Sprite,
    TileMap,
    TileSet,
)
from engine.core.nodes2d import (
    # Core 2D types
    Vector2,
    Vector2i,
    Color,
    Texture2D,
    # 2D Node hierarchy
    Node2D,
    Sprite2D,
    AnimatedSprite2D,
    SpriteFrames,
    SpriteAnimation,
    CollisionShape2D,
    CharacterBody2D,
    RigidBody2D,
    PhysicsMaterial,
    StaticBody2D,
    Area2D,
    Camera2D,
    CanvasLayer,
    RayCast2D,
    Line2D,
    GPUParticles2D,
    Rect2,
    AudioStreamPlayer2D,
    AudioStream,
    PathFollow2D,
    Curve2D,
)
from engine.core.tilemap import (
    # TileMap system
    Direction,
    Vector2i,
    Rect2i,
    Shape2D,
    RectangleShape2D,
    NavigationPolygon,
    CustomDataLayer,
    PhysicsLayer,
    TerrainMode,
    TerrainSet,
    TileData,
    CellData,
    TileSet as TileSetResource,
    TileMapLayer,
)
from engine.core.project_secure import SecureProject as Project
from engine.core.scene import Scene
from engine.core.transform import Transform2D
from engine.core.types import NodeType
from engine.core.undo_manager import (
    AddNodeCommand,
    Command,
    PropertyCommand,
    RemoveNodeCommand,
    ReorderNodeCommand,
    TransformCommand,
    UndoManager,
    global_undo_manager,
)

import logging


logger = logging.getLogger(__name__)

__all__ = [
    "Node",
    "Node2D",
    "NodeType",
    "Transform2D",
    "Scene",
    "Project",
    "instance_scene",
    # Extended node types
    "Sprite",
    "AnimatedSprite",
    "TileMap",
    "TileSet",
    "Control",
    "Label",
    "Button",
    "Panel",
    # Godot-inspired 2D Node Hierarchy
    "Vector2",
    "Vector2i",
    "Color",
    "Texture2D",
    "Node2D",
    "Sprite2D",
    "AnimatedSprite2D",
    "SpriteFrames",
    "SpriteAnimation",
    "CollisionShape2D",
    "CharacterBody2D",
    "RigidBody2D",
    "PhysicsMaterial",
    "StaticBody2D",
    "Area2D",
    "Camera2D",
    "CanvasLayer",
    "RayCast2D",
    "Line2D",
    "GPUParticles2D",
    "Rect2",
    "AudioStreamPlayer2D",
    "AudioStream",
    "PathFollow2D",
    "Curve2D",
    # TileMap System
    "Direction",
    "Vector2i",
    "Rect2i",
    "Shape2D",
    "RectangleShape2D",
    "NavigationPolygon",
    "CustomDataLayer",
    "PhysicsLayer",
    "TerrainMode",
    "TerrainSet",
    "TileData",
    "CellData",
    "TileSetResource",
    "TileMapLayer",
    # Undo system
    "UndoManager",
    "Command",
    "PropertyCommand",
    "TransformCommand",
    "AddNodeCommand",
    "RemoveNodeCommand",
    "ReorderNodeCommand",
    "global_undo_manager",
    # Errors
    "SecurityError",
    "ScriptingSecurityError",
]
