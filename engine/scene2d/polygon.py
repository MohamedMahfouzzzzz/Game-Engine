# /**************************************************************************/
# /*  polygon.py                                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D polygon drawing node."""

from typing import List, Optional
from engine.core.nodes2d import Node2D, Vector2, Color
from engine.scene2d.sprite import Texture2D


class Polygon2D(Node2D):
    """Draws a filled polygon with optional texture.
    
    Features:
    - Solid color or textured fill
    - UV coordinate mapping
    - Bone weighting for deformation
    - Internal polygons for holes
    """
    
    def __init__(self, name: str = "Polygon2D"):
        super().__init__(name)
        self._polygon: List[Vector2] = []
        self._uv: List[Vector2] = []
        self._skeleton = None
        self._bones: List[tuple] = []  # (path, weights)
        self._internal: List[List[Vector2]] = []  # Holes
        self._color: Color = Color(1, 1, 1, 1)
        self._offset: Vector2 = Vector2()
        self._texture: Optional[Texture2D] = None
        self._invert: bool = False
        self._invert_border: float = 100.0
        self._antialiased: bool = False
        self._polygons: List[List[int]] = []  # Triangle indices
        self._bone_weights: List[dict] = []
    
    def set_polygon(self, polygon: List[Vector2]) -> None:
        """Set polygon vertices."""
        self._polygon = list(polygon)
    
    def get_polygon(self) -> List[Vector2]:
        return list(self._polygon)
    
    def set_uv(self, uv: List[Vector2]) -> None:
        """Set UV coordinates for texture mapping."""
        self._uv = list(uv)
    
    def get_uv(self) -> List[Vector2]:
        return list(self._uv)
    
    def set_color(self, color: Color) -> None:
        """Set fill color."""
        self._color = color
    
    def get_color(self) -> Color:
        return self._color
    
    def set_texture(self, texture: Optional[Texture2D]) -> None:
        """Set texture for fill."""
        self._texture = texture
    
    def get_texture(self) -> Optional[Texture2D]:
        return self._texture
    
    def set_offset(self, offset: Vector2) -> None:
        """Set polygon offset."""
        self._offset = offset
    
    def get_offset(self) -> Vector2:
        return self._offset
    
    def set_invert(self, invert: bool) -> None:
        """Invert fill (draw outside polygon)."""
        self._invert = invert
    
    def get_invert(self) -> bool:
        return self._invert
    
    def set_invert_border(self, border: float) -> None:
        """Border size for inverted polygon."""
        self._invert_border = max(0.0, border)
    
    def get_invert_border(self) -> float:
        return self._invert_border
    
    def set_antialiased(self, antialiased: bool) -> None:
        """Enable antialiasing."""
        self._antialiased = antialiased
    
    def get_antialiased(self) -> bool:
        return self._antialiased
    
    def add_bone(self, path: str, weights: List[float]) -> None:
        """Add bone with weights for deformation."""
        self._bones.append((path, list(weights)))
    
    def clear_bones(self) -> None:
        """Remove all bones."""
        self._bones.clear()
    
    def get_bone_count(self) -> int:
        return len(self._bones)
    
    def add_internal_polygon(self, polygon: List[Vector2]) -> None:
        """Add internal polygon (hole)."""
        self._internal.append(list(polygon))
    
    def clear_internal_polygons(self) -> None:
        """Remove all internal polygons."""
        self._internal.clear()
    
    def __repr__(self) -> str:
        return f"Polygon2D('{self.name}', vertices={len(self._polygon)})"
