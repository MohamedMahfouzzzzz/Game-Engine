# /**************************************************************************/
# /*  sprite.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D sprite node with texture support."""

from typing import Optional
from engine.core.nodes2d import Node2D, Vector2, Color, Rect2


class Texture2D:
    """2D texture resource."""
    def __init__(self, width: int = 32, height: int = 32):
        self.width = width
        self.height = height


class Sprite2D(Node2D):
    """2D sprite node for displaying textures.
    
    Features:
    - Texture display with optional region
    - Center/offset positioning
    - Horizontal/vertical flipping
    - Color modulation
    - Sprite sheet animation (hframes/vframes)
    """
    
    def __init__(self, name: str = "Sprite2D"):
        super().__init__(name)
        self._texture: Optional[Texture2D] = None
        self._centered: bool = True
        self._offset: Vector2 = Vector2()
        self._flip_h: bool = False
        self._flip_v: bool = False
        self._modulate: Color = Color(1, 1, 1, 1)
        self._region_enabled: bool = False
        self._region_rect: Rect2 = Rect2()
        self._frame: int = 0
        self._hframes: int = 1
        self._vframes: int = 1
    
    # Texture
    def set_texture(self, texture: Optional[Texture2D]) -> None:
        self._texture = texture
    
    def get_texture(self) -> Optional[Texture2D]:
        return self._texture
    
    # Positioning
    def set_centered(self, centered: bool) -> None:
        self._centered = centered
    
    def is_centered(self) -> bool:
        return self._centered
    
    def set_offset(self, offset: Vector2) -> None:
        self._offset = offset
    
    def get_offset(self) -> Vector2:
        return self._offset
    
    # Flipping
    def set_flip_h(self, flip: bool) -> None:
        self._flip_h = flip
    
    def is_flipped_h(self) -> bool:
        return self._flip_h
    
    def set_flip_v(self, flip: bool) -> None:
        self._flip_v = flip
    
    def is_flipped_v(self) -> bool:
        return self._flip_v
    
    # Color
    def set_modulate(self, color: Color) -> None:
        self._modulate = color
    
    def get_modulate(self) -> Color:
        return self._modulate
    
    # Region
    def set_region_enabled(self, enabled: bool) -> None:
        self._region_enabled = enabled
    
    def is_region_enabled(self) -> bool:
        return self._region_enabled
    
    def set_region_rect(self, rect: Rect2) -> None:
        self._region_rect = rect
    
    def get_region_rect(self) -> Rect2:
        return self._region_rect
    
    # Sprite sheet
    def set_frame(self, frame: int) -> None:
        self._frame = max(0, frame)
    
    def get_frame(self) -> int:
        return self._frame
    
    def set_hframes(self, frames: int) -> None:
        self._hframes = max(1, frames)
    
    def get_hframes(self) -> int:
        return self._hframes
    
    def set_vframes(self, frames: int) -> None:
        self._vframes = max(1, frames)
    
    def get_vframes(self) -> int:
        return self._vframes
    
    def __repr__(self) -> str:
        return f"Sprite2D('{self.name}', texture={self._texture is not None})"
