# /**************************************************************************/
# /*  sprite.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Sprite node for displaying 2D textures."""

from typing import Optional, Tuple
from engine.core.node_base import Node2D
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Sprite(Node2D):
    """A 2D sprite that displays a texture."""

    def __init__(self, name: str = "Sprite"):
        super().__init__(name)
        self.node_type = NodeType.SPRITE
        self.texture_path: Optional[str] = None
        self.texture_size: Tuple[int, int] = (0, 0)
        self.flip_h: bool = False
        self.flip_v: bool = False
        self.modulate: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self.self_modulate: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self.region_enabled: bool = False
        self.region_rect: Tuple[int, int, int, int] = (0, 0, 0, 0)  # x, y, w, h
        self.centered: bool = True
        self.offset: Tuple[float, float] = (0.0, 0.0)

    def set_texture(self, path: str, width: int = 0, height: int = 0) -> None:
        """Set the texture path and optionally its size."""
        self.texture_path = path
        self.texture_size = (width, height)

    def set_flip(self, horizontal: bool = False, vertical: bool = False) -> None:
        """Set flip flags."""
        self.flip_h = horizontal
        self.flip_v = vertical

    def set_region(self, x: int, y: int, width: int, height: int) -> None:
        """Enable and set texture region for sprite sheets."""
        self.region_enabled = True
        self.region_rect = (x, y, width, height)
        if self.texture_size == (0, 0):
            self.texture_size = (width, height)

    def clear_region(self) -> None:
        """Disable region and use full texture."""
        self.region_enabled = False

    def to_dict(self):
        """Serialize to dictionary."""
        data = super().to_dict()
        data.update({
            "texture_path": self.texture_path,
            "texture_size": self.texture_size,
            "flip_h": self.flip_h,
            "flip_v": self.flip_v,
            "modulate": self.modulate,
            "self_modulate": self.self_modulate,
            "region_enabled": self.region_enabled,
            "region_rect": self.region_rect,
            "centered": self.centered,
            "offset": self.offset,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary."""
        sprite = cls(data.get("name", "Sprite"))
        sprite.texture_path = data.get("texture_path")
        sprite.texture_size = tuple(data.get("texture_size", [0, 0]))
        sprite.flip_h = data.get("flip_h", False)
        sprite.flip_v = data.get("flip_v", False)
        sprite.modulate = tuple(data.get("modulate", [255, 255, 255, 255]))
        sprite.self_modulate = tuple(data.get("self_modulate", [255, 255, 255, 255]))
        sprite.region_enabled = data.get("region_enabled", False)
        sprite.region_rect = tuple(data.get("region_rect", [0, 0, 0, 0]))
        sprite.centered = data.get("centered", True)
        sprite.offset = tuple(data.get("offset", [0.0, 0.0]))
        return sprite
