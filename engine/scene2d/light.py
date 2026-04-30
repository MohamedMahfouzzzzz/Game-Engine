# /**************************************************************************/
# /*  light.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D lighting nodes."""

from enum import IntEnum
from typing import Optional
from engine.core.nodes2d import Node2D, Vector2, Color
from engine.scene2d.sprite import Texture2D


class ShadowFilter(IntEnum):
    """Shadow filter quality."""
    SHADOW_FILTER_NONE = 0
    SHADOW_FILTER_PCF3 = 1
    SHADOW_FILTER_PCF5 = 2
    SHADOW_FILTER_PCF7 = 3
    SHADOW_FILTER_PCF13 = 4


class Light2D(Node2D):
    """2D light source.
    
    Casts light using a texture and supports shadows.
    """
    
    def __init__(self, name: str = "Light2D"):
        super().__init__(name)
        self._texture: Optional[Texture2D] = None
        self._offset: Vector2 = Vector2()
        self._texture_scale: float = 1.0
        self._color: Color = Color(1, 1, 1, 1)
        self._energy: float = 1.0
        self._blend_mode: int = 0  # Add
        self._range_layer_min: int = -512
        self._range_layer_max: int = 512
        self._range_item_cull_mask: int = 1
        self._shadow_enabled: bool = False
        self._shadow_color: Color = Color(0, 0, 0, 0)
        self._shadow_filter: ShadowFilter = ShadowFilter.SHADOW_FILTER_NONE
        self._shadow_filter_smooth: float = 0.0
        self._shadow_item_cull_mask: int = 1
    
    def set_texture(self, texture: Optional[Texture2D]) -> None:
        """Set the light texture."""
        self._texture = texture
    
    def get_texture(self) -> Optional[Texture2D]:
        """Get the light texture."""
        return self._texture
    
    def set_offset(self, offset: Vector2) -> None:
        """Set texture offset."""
        self._offset = offset
    
    def get_offset(self) -> Vector2:
        return self._offset
    
    def set_texture_scale(self, scale: float) -> None:
        """Set texture scale."""
        self._texture_scale = max(0.001, scale)
    
    def get_texture_scale(self) -> float:
        return self._texture_scale
    
    def set_color(self, color: Color) -> None:
        """Set light color."""
        self._color = color
    
    def get_color(self) -> Color:
        return self._color
    
    def set_energy(self, energy: float) -> None:
        """Set light intensity."""
        self._energy = max(0.0, energy)
    
    def get_energy(self) -> float:
        return self._energy
    
    def set_blend_mode(self, mode: int) -> None:
        """Set blend mode: 0=Add, 1=Sub, 2=Mix."""
        self._blend_mode = mode
    
    def get_blend_mode(self) -> int:
        return self._blend_mode
    
    def set_shadow_enabled(self, enabled: bool) -> None:
        """Enable/disable shadow casting."""
        self._shadow_enabled = enabled
    
    def is_shadow_enabled(self) -> bool:
        return self._shadow_enabled
    
    def set_shadow_color(self, color: Color) -> None:
        """Set shadow color."""
        self._shadow_color = color
    
    def get_shadow_color(self) -> Color:
        return self._shadow_color
    
    def set_shadow_filter(self, filter: ShadowFilter) -> None:
        """Set shadow filter quality."""
        self._shadow_filter = filter
    
    def get_shadow_filter(self) -> ShadowFilter:
        return self._shadow_filter
    
    def set_shadow_item_cull_mask(self, mask: int) -> None:
        """Set which items cast shadows."""
        self._shadow_item_cull_mask = mask
    
    def get_shadow_item_cull_mask(self) -> int:
        return self._shadow_item_cull_mask
    
    def set_range_item_cull_mask(self, mask: int) -> None:
        """Set which items are lit."""
        self._range_item_cull_mask = mask
    
    def get_range_item_cull_mask(self) -> int:
        return self._range_item_cull_mask
    
    def __repr__(self) -> str:
        return f"Light2D('{self.name}', energy={self._energy}, shadows={self._shadow_enabled})"


class LightOccluder2D(Node2D):
    """Occluder that blocks 2D light.
    
    Defines polygon shape that casts shadows from Light2D nodes.
    """
    
    def __init__(self, name: str = "LightOccluder2D"):
        super().__init__(name)
        self._occluder = None
        self._sdf_collision: bool = False
        self._occluder_light_mask: int = 1
        self._polygon: list = []
    
    def set_occluder(self, occluder) -> None:
        """Set the occluder polygon resource."""
        self._occluder = occluder
    
    def get_occluder(self):
        return self._occluder
    
    def set_sdf_collision(self, enabled: bool) -> None:
        """Enable SDF collision."""
        self._sdf_collision = enabled
    
    def is_sdf_collision_enabled(self) -> bool:
        return self._sdf_collision
    
    def set_occluder_light_mask(self, mask: int) -> None:
        """Set which lights this occluder affects."""
        self._occluder_light_mask = mask
    
    def get_occluder_light_mask(self) -> int:
        return self._occluder_light_mask
    
    def set_polygon(self, polygon: list) -> None:
        """Set occluder polygon points."""
        self._polygon = polygon
    
    def get_polygon(self) -> list:
        return self._polygon
    
    def __repr__(self) -> str:
        return f"LightOccluder2D('{self.name}', mask={self._occluder_light_mask})"
