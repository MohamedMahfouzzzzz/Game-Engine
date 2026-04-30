# /**************************************************************************/
# /*  nodes2d/sprite2d.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Sprite2D - 2D sprite with texture support."""

from __future__ import annotations

from typing import Optional

from .node2d import Node2D
from .types import Vector2, Texture2D, Color
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Sprite2D(Node2D):
    """2D textured sprite node.
    
    Properties:
        texture: Texture2D to display
        offset: Drawing offset from position
        flip_h: Horizontal flip
        flip_v: Vertical flip
        centered: Center texture on position
        modulate: Color tint
        hframes: Horizontal frames for animation
        vframes: Vertical frames for animation
        frame: Current animation frame
    
    Signals:
        texture_changed: When texture changes
        frame_changed: When animation frame changes
    """
    
    __slots__ = [
        "texture", "offset", "flip_h", "flip_v", "centered",
        "hframes", "vframes", "_frame",
        "region_enabled", "region_rect"
    ]
    
    _SIGNALS = ["texture_changed", "frame_changed"]
    
    def __init__(self, name: str = "Sprite2D"):
        super().__init__(name)
        self.node_type = NodeType.SPRITE
        
        self.texture: Optional[Texture2D] = None
        self.offset = Vector2(0, 0)
        self.flip_h = False
        self.flip_v = False
        self.centered = True
        
        # Animation frames
        self.hframes = 1
        self.vframes = 1
        self._frame = 0
        
        # Region (sub-rectangle) of texture
        self.region_enabled = False
        self.region_rect = (0, 0, 0, 0)  # x, y, w, h
    
    @property
    def frame(self) -> int:
        return self._frame
    
    @frame.setter
    def frame(self, value: int) -> None:
        if value != self._frame:
            self._frame = value
            self.signals.emit("frame_changed", value)
    
    def get_frame_coords(self) -> tuple:
        """Get frame grid coordinates (col, row)."""
        return (self._frame % self.hframes, self._frame // self.hframes)
    
    def set_texture(self, texture: Optional[Texture2D]) -> None:
        """Set texture and emit signal."""
        self.texture = texture
        self.signals.emit("texture_changed", texture)
    
    def _draw(self, renderer) -> None:
        """Draw the sprite."""
        if not self.texture or not self.visible:
            return
        
        # Load texture if not loaded
        if not self.texture.is_loaded():
            self.texture.load()
        
        if not self.texture.is_loaded():
            return
        
        # Calculate frame rect
        if self.hframes > 1 or self.vframes > 1:
            fw = self.texture.width // self.hframes
            fh = self.texture.height // self.vframes
            col, row = self.get_frame_coords()
            src_rect = (col * fw, row * fh, fw, fh)
        elif self.region_enabled:
            src_rect = self.region_rect
        else:
            src_rect = (0, 0, self.texture.width, self.texture.height)
        
        # Calculate draw position
        pos = self.get_global_position() + self.offset
        
        if self.centered:
            w, h = src_rect[2], src_rect[3]
            pos = pos - Vector2(w/2, h/2)
        
        # Draw using renderer
        if hasattr(renderer, 'draw_sprite'):
            renderer.draw_sprite(
                texture=self.texture,
                position=pos,
                source_rect=src_rect,
                scale=None,
                rotation=self.rotation,
                modulate=self.modulate
            )
