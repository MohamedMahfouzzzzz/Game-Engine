# /**************************************************************************/
# /*  camera.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D camera node for viewport control."""

from enum import IntEnum
from typing import Optional
from engine.core.nodes2d import Node2D, Vector2


class CameraAnchorMode(IntEnum):
    """Camera anchor positioning modes."""
    FREE = 0
    FIXED_TOP_LEFT = 1
    DRAG_CENTER = 2


class CameraProcessCallback(IntEnum):
    """Camera update timing."""
    PHYSICS = 0
    IDLE = 1


class Camera2D(Node2D):
    """2D camera for controlling the viewport view.
    
    Features:
    - Zoom control
    - Smooth following with configurable margins
    - World limits (clamp camera movement)
    - Position/rotation smoothing
    """
    
    def __init__(self, name: str = "Camera2D"):
        super().__init__(name)
        self._enabled: bool = True
        self._zoom: Vector2 = Vector2(1, 1)
        self._offset: Vector2 = Vector2()
        self._anchor_mode: CameraAnchorMode = CameraAnchorMode.DRAG_CENTER
        self._process_callback: CameraProcessCallback = CameraProcessCallback.IDLE
        
        # World limits
        self._limit_left: int = -10000000
        self._limit_top: int = -10000000
        self._limit_right: int = 10000000
        self._limit_bottom: int = 10000000
        self._limit_smoothing_enabled: bool = False
        self._limit_smoothing_speed: float = 10.0
        
        # Drag margins
        self._drag_horizontal_enabled: bool = False
        self._drag_vertical_enabled: bool = False
        self._drag_horizontal_margin: float = 0.2
        self._drag_vertical_margin: float = 0.2
        
        # Smoothing
        self._smoothing_enabled: bool = False
        self._smoothing_speed: float = 5.0
        self._position_smoothing_enabled: bool = False
        self._position_smoothing_speed: float = 10.0
        self._rotation_smoothing_enabled: bool = False
        self._rotation_smoothing_speed: float = 5.0
        
        # Editor
        self._editor_draw_screen: bool = True
        self._editor_draw_limits: bool = False
        self._editor_draw_drag_margin: bool = False
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_zoom(self, zoom: Vector2) -> None:
        self._zoom = Vector2(max(0.001, zoom.x), max(0.001, zoom.y))
    
    def get_zoom(self) -> Vector2:
        return self._zoom
    
    def set_offset(self, offset: Vector2) -> None:
        self._offset = offset
    
    def get_offset(self) -> Vector2:
        return self._offset
    
    def set_anchor_mode(self, mode: CameraAnchorMode) -> None:
        self._anchor_mode = mode
    
    def get_anchor_mode(self) -> CameraAnchorMode:
        return self._anchor_mode
    
    # Limits
    def set_limit_left(self, limit: int) -> None:
        self._limit_left = limit
    
    def get_limit_left(self) -> int:
        return self._limit_left
    
    def set_limit_top(self, limit: int) -> None:
        self._limit_top = limit
    
    def get_limit_top(self) -> int:
        return self._limit_top
    
    def set_limit_right(self, limit: int) -> None:
        self._limit_right = limit
    
    def get_limit_right(self) -> int:
        return self._limit_right
    
    def set_limit_bottom(self, limit: int) -> None:
        self._limit_bottom = limit
    
    def get_limit_bottom(self) -> int:
        return self._limit_bottom
    
    def set_limit_smoothing_enabled(self, enabled: bool) -> None:
        self._limit_smoothing_enabled = enabled
    
    def is_limit_smoothing_enabled(self) -> bool:
        return self._limit_smoothing_enabled
    
    def set_limit_smoothing_speed(self, speed: float) -> None:
        self._limit_smoothing_speed = speed
    
    def get_limit_smoothing_speed(self) -> float:
        return self._limit_smoothing_speed
    
    # Drag margins
    def set_drag_horizontal_enabled(self, enabled: bool) -> None:
        self._drag_horizontal_enabled = enabled
    
    def is_drag_horizontal_enabled(self) -> bool:
        return self._drag_horizontal_enabled
    
    def set_drag_vertical_enabled(self, enabled: bool) -> None:
        self._drag_vertical_enabled = enabled
    
    def is_drag_vertical_enabled(self) -> bool:
        return self._drag_vertical_enabled
    
    def set_drag_horizontal_margin(self, margin: float) -> None:
        self._drag_horizontal_margin = margin
    
    def get_drag_horizontal_margin(self) -> float:
        return self._drag_horizontal_margin
    
    def set_drag_vertical_margin(self, margin: float) -> None:
        self._drag_vertical_margin = margin
    
    def get_drag_vertical_margin(self) -> float:
        return self._drag_vertical_margin
    
    # Smoothing
    def set_smoothing_enabled(self, enabled: bool) -> None:
        self._smoothing_enabled = enabled
    
    def is_smoothing_enabled(self) -> bool:
        return self._smoothing_enabled
    
    def set_smoothing_speed(self, speed: float) -> None:
        self._smoothing_speed = speed
    
    def get_smoothing_speed(self) -> float:
        return self._smoothing_speed
    
    def __repr__(self) -> str:
        return f"Camera2D('{self.name}', zoom=({self._zoom.x}, {self._zoom.y}))"
