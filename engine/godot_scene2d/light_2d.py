# /**************************************************************************/
# /*  light_2d.py                                                           */
# /**************************************************************************/

"""Godot Light2D port - 2D light source."""

from enum import IntEnum
from typing import Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Color


class Light2DShadowFilter(IntEnum):
    SHADOW_FILTER_NONE = 0
    SHADOW_FILTER_PCF3 = 1
    SHADOW_FILTER_PCF5 = 2
    SHADOW_FILTER_PCF7 = 3
    SHADOW_FILTER_PCF13 = 4


class Light2D(Node2D):
    """2D light source."""
    
    def __init__(self, name: str = "Light2D"):
        super().__init__(name)
        self._enabled: bool = True
        self._color: Color = Color(1, 1, 1)
        self._energy: float = 1.0
        self._range: float = 500.0
        self._texture_scale: float = 1.0
        self._z_range_min: int = -1024
        self._z_range_max: int = 1024
        self._layer_range_min: int = 0
        self._layer_range_max: int = 0
        self._item_cull_mask: int = 1
        self._shadow_enabled: bool = False
        self._shadow_color: Color = Color(0, 0, 0, 1)
        self._shadow_filter: Light2DShadowFilter = Light2DShadowFilter.SHADOW_FILTER_NONE
        self._shadow_filter_smooth: float = 0.0
        self._shadow_item_cull_mask: int = 1
        self._blend_mode: int = 0  # 0=add, 1=sub, 2=mix
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_color(self, color: Color) -> None:
        self._color = color
    
    def get_color(self) -> Color:
        return self._color
    
    def set_energy(self, energy: float) -> None:
        self._energy = max(0.0, energy)
    
    def get_energy(self) -> float:
        return self._energy
    
    def set_range(self, range_val: float) -> None:
        self._range = max(0.0, range_val)
    
    def get_range(self) -> float:
        return self._range
    
    def set_texture_scale(self, scale: float) -> None:
        self._texture_scale = scale
    
    def get_texture_scale(self) -> float:
        return self._texture_scale
    
    def set_item_cull_mask(self, mask: int) -> None:
        self._item_cull_mask = mask
    
    def get_item_cull_mask(self) -> int:
        return self._item_cull_mask
    
    def set_item_cull_mask_bit(self, bit: int, value: bool) -> None:
        if value:
            self._item_cull_mask |= (1 << bit)
        else:
            self._item_cull_mask &= ~(1 << bit)
    
    def set_shadow_enabled(self, enabled: bool) -> None:
        self._shadow_enabled = enabled
    
    def is_shadow_enabled(self) -> bool:
        return self._shadow_enabled
    
    def set_shadow_color(self, color: Color) -> None:
        self._shadow_color = color
    
    def get_shadow_color(self) -> Color:
        return self._shadow_color
    
    def set_shadow_filter(self, filter_mode: Light2DShadowFilter) -> None:
        self._shadow_filter = filter_mode
    
    def get_shadow_filter(self) -> Light2DShadowFilter:
        return self._shadow_filter
    
    def set_shadow_item_cull_mask(self, mask: int) -> None:
        self._shadow_item_cull_mask = mask
    
    def get_shadow_item_cull_mask(self) -> int:
        return self._shadow_item_cull_mask
    
    def set_blend_mode(self, mode: int) -> None:
        self._blend_mode = mode
    
    def get_blend_mode(self) -> int:
        return self._blend_mode
    
    def __repr__(self) -> str:
        return f"Light2D('{self.name}', color={self._color}, energy={self._energy}, shadows={self._shadow_enabled})"
