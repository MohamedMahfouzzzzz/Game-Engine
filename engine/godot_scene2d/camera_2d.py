# /**************************************************************************/
# /*  camera_2d.py                                                          */
# /**************************************************************************/

"""Godot Camera2D port - 2D camera node."""

from enum import IntEnum
from typing import Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Rect2, Size2


class Camera2DAnchorMode(IntEnum):
    ANCHOR_MODE_FREE = 0
    ANCHOR_MODE_FIXED_TOP_LEFT = 1
    ANCHOR_MODE_DRAG_CENTER = 2


class Camera2DProcessCallback(IntEnum):
    CAMERA2D_PROCESS_PHYSICS = 0
    CAMERA2D_PROCESS_IDLE = 1


class Camera2D(Node2D):
    """2D camera for viewport control."""
    
    def __init__(self, name: str = "Camera2D"):
        super().__init__(name)
        self._enabled: bool = True
        self._zoom: Point2 = Point2(1, 1)
        self._offset: Point2 = Point2()
        self._anchor_mode: Camera2DAnchorMode = Camera2DAnchorMode.ANCHOR_MODE_DRAG_CENTER
        self._process_callback: Camera2DProcessCallback = Camera2DProcessCallback.CAMERA2D_PROCESS_IDLE
        
        # Limits
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
        
        # Rotation smoothing
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
    
    def set_zoom(self, zoom: Point2) -> None:
        self._zoom = Point2(max(0.001, zoom.x), max(0.001, zoom.y))
    
    def get_zoom(self) -> Point2:
        return self._zoom
    
    def set_offset(self, offset: Point2) -> None:
        self._offset = offset
    
    def get_offset(self) -> Point2:
        return self._offset
    
    def set_anchor_mode(self, mode: Camera2DAnchorMode) -> None:
        self._anchor_mode = mode
    
    def get_anchor_mode(self) -> Camera2DAnchorMode:
        return self._anchor_mode
    
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
    
    def set_drag_horizontal_enabled(self, enabled: bool) -> None:
        self._drag_horizontal_enabled = enabled
    
    def is_drag_horizontal_enabled(self) -> bool:
        return self._drag_horizontal_enabled
    
    def set_drag_vertical_enabled(self, enabled: bool) -> None:
        self._drag_vertical_enabled = enabled
    
    def is_drag_vertical_enabled(self) -> bool:
        return self._drag_vertical_enabled
    
    def set_smoothing_enabled(self, enabled: bool) -> None:
        self._smoothing_enabled = enabled
    
    def is_smoothing_enabled(self) -> bool:
        return self._smoothing_enabled
    
    def set_smoothing_speed(self, speed: float) -> None:
        self._smoothing_speed = max(0.0, speed)
    
    def get_smoothing_speed(self) -> float:
        return self._smoothing_speed
    
    def get_screen_center(self) -> Point2:
        return self.get_global_position() + self._offset
    
    def get_viewport_rect(self) -> Rect2:
        center = self.get_screen_center()
        size = Size2(1024 / self._zoom.x, 768 / self._zoom.y)
        return Rect2(Point2(center.x - size.width/2, center.y - size.height/2), size)
    
    def force_update_scroll(self) -> None:
        pass
    
    def reset_smoothing(self) -> None:
        pass
    
    def __repr__(self) -> str:
        return f"Camera2D('{self.name}', enabled={self._enabled}, zoom={self._zoom.x:.3f},{self._zoom.y:.3f})"
