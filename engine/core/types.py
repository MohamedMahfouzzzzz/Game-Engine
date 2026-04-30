# /**************************************************************************/
# /*  types.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""
Enumeration of every supported 2-D node type.

Designed to map 1-to-1 with Godot 4 node class names so that the
Godot importer can convert scenes without data loss.
"""

from __future__ import annotations

from enum import Enum

import logging


logger = logging.getLogger(__name__)



class NodeType(Enum):
    """All supported 2-D node types (Godot 4-compatible names)."""

    # ── Base ──────────────────────────────────────────────────────────
    NODE   = "Node"
    NODE2D = "Node2D"

    # ── Sprites ───────────────────────────────────────────────────────
    SPRITE            = "Sprite"        # Godot 3 compat alias
    SPRITE2D          = "Sprite2D"
    ANIMATED_SPRITE   = "AnimatedSprite"
    ANIMATED_SPRITE2D = "AnimatedSprite2D"

    # ── Camera / Canvas ───────────────────────────────────────────────
    CAMERA2D     = "Camera2D"
    CANVAS_LAYER = "CanvasLayer"
    PARALLAX2D   = "Parallax2D"

    # ── Lighting ──────────────────────────────────────────────────────
    LIGHT2D            = "Light2D"
    DIRECTIONAL_LIGHT2D = "DirectionalLight2D"
    POINT_LIGHT2D      = "PointLight2D"

    # ── Particles ─────────────────────────────────────────────────────
    PARTICLE2D          = "Particle2D"
    GPU_PARTICLES2D     = "GPUParticles2D"
    CPU_PARTICLES2D     = "CPUParticles2D"

    # ── Physics ───────────────────────────────────────────────────────
    RIGIDBODY2D           = "RigidBody2D"
    STATICBODY2D          = "StaticBody2D"
    KINEMATICBODY2D       = "KinematicBody2D"
    CHARACTERBODY2D       = "CharacterBody2D"   # Godot 4
    AREA2D                = "Area2D"
    COLLISIONSHAPE2D      = "CollisionShape2D"
    COLLISIONPOLYGON2D    = "CollisionPolygon2D"
    RAYCAST2D             = "RayCast2D"
    SHAPECASTER2D         = "ShapeCast2D"

    # ── TileMap ───────────────────────────────────────────────────────
    TILEMAP       = "TileMap"
    TILESET       = "TileSet"
    TILEMAPLAYER  = "TileMapLayer"   # Godot 4.3+

    # ── Skeleton ──────────────────────────────────────────────────────
    SKELETON2D = "Skeleton2D"
    BONE2D     = "Bone2D"

    # ── Audio ─────────────────────────────────────────────────────────
    AUDIO_STREAM_PLAYER   = "AudioStreamPlayer"
    AUDIO_STREAM_PLAYER2D = "AudioStreamPlayer2D"

    # ── Animation ─────────────────────────────────────────────────────
    ANIMATION_PLAYER = "AnimationPlayer"
    ANIMATION_TREE   = "AnimationTree"

    # ── Path ──────────────────────────────────────────────────────────
    PATH2D       = "Path2D"
    PATH_FOLLOW2D = "PathFollow2D"

    # ── UI / Control ──────────────────────────────────────────────────
    CONTROL          = "Control"
    LABEL            = "Label"
    RICH_TEXT_LABEL  = "RichTextLabel"
    BUTTON           = "Button"
    CHECK_BOX        = "CheckBox"
    LINE_EDIT        = "LineEdit"
    TEXT_EDIT        = "TextEdit"
    PANEL            = "Panel"
    PANEL_CONTAINER  = "PanelContainer"
    CONTAINER        = "Container"
    VBOX_CONTAINER   = "VBoxContainer"
    HBOX_CONTAINER   = "HBoxContainer"
    GRID_CONTAINER   = "GridContainer"
    MARGIN_CONTAINER = "MarginContainer"
    SCROLL_CONTAINER = "ScrollContainer"
    TAB_CONTAINER    = "TabContainer"
    SPLIT_CONTAINER  = "SplitContainer"
    TEXTURE_RECT     = "TextureRect"
    COLOR_RECT       = "ColorRect"
    PROGRESS_BAR     = "ProgressBar"
    SLIDER           = "Slider"
    SPIN_BOX         = "SpinBox"
    POPUP_MENU       = "PopupMenu"
    DIALOG           = "AcceptDialog"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_godot(cls, godot_class: str) -> "NodeType":
        """Return the closest matching :class:`NodeType` for a Godot class name.

        Falls back to :attr:`NODE2D` for unknown 2-D classes and :attr:`NODE`
        for everything else.
        """
        for member in cls:
            if member.value == godot_class:
                return member
        # Heuristic fallback
        if "2D" in godot_class or "Body" in godot_class:
            return cls.NODE2D
        return cls.NODE

    @classmethod
    def all_values(cls) -> list[str]:
        return [m.value for m in cls]
