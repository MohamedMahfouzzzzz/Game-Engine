# /**************************************************************************/
# /*  touch_screen_button.py                                                */
# /**************************************************************************/

"""Godot TouchScreenButton port - On-screen touch button."""

from enum import IntEnum
from typing import Optional, Callable, List
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Rect2, Size2
from engine.godot_scene2d.physics.collision_shape_2d import Shape2D


class TouchScreenButtonVisibilityMode(IntEnum):
    ALWAYS = 0
    TOUCHSCREEN_ONLY = 1
    WHEN_TOUCHED = 2


class TouchScreenButton(Node2D):
    """On-screen touch button for mobile."""
    
    def __init__(self, name: str = "TouchScreenButton"):
        super().__init__(name)
        self._normal: Optional[any] = None
        self._pressed: Optional[any] = None
        self._bitmask: Optional[any] = None
        self._shape: Optional[Shape2D] = None
        self._shape_centered: bool = True
        self._shape_visible: bool = True
        self._passby_press: bool = False
        self._action: str = ""
        self._visibility_mode: TouchScreenButtonVisibilityMode = TouchScreenButtonVisibilityMode.ALWAYS
        self._pressed_state: bool = False
        self._pressed_position: Point2 = Point2()
        
        self._pressed_callbacks: List[Callable] = []
        self._released_callbacks: List[Callable] = []
    
    def set_texture_normal(self, normal: Optional[any]) -> None:
        self._normal = normal
    
    def get_texture_normal(self) -> Optional[any]:
        return self._normal
    
    def set_texture_pressed(self, pressed: Optional[any]) -> None:
        self._pressed = pressed
    
    def get_texture_pressed(self) -> Optional[any]:
        return self._pressed
    
    def set_bitmask(self, bitmask: Optional[any]) -> None:
        self._bitmask = bitmask
    
    def get_bitmask(self) -> Optional[any]:
        return self._bitmask
    
    def set_shape(self, shape: Optional[Shape2D]) -> None:
        self._shape = shape
    
    def get_shape(self) -> Optional[Shape2D]:
        return self._shape
    
    def set_shape_centered(self, centered: bool) -> None:
        self._shape_centered = centered
    
    def is_shape_centered(self) -> bool:
        return self._shape_centered
    
    def set_shape_visible(self, visible: bool) -> None:
        self._shape_visible = visible
    
    def is_shape_visible(self) -> bool:
        return self._shape_visible
    
    def set_passby_press(self, enabled: bool) -> None:
        self._passby_press = enabled
    
    def is_passby_press_enabled(self) -> bool:
        return self._passby_press
    
    def set_action(self, action: str) -> None:
        self._action = action
    
    def get_action(self) -> str:
        return self._action
    
    def set_visibility_mode(self, mode: TouchScreenButtonVisibilityMode) -> None:
        self._visibility_mode = mode
    
    def get_visibility_mode(self) -> TouchScreenButtonVisibilityMode:
        return self._visibility_mode
    
    def is_pressed(self) -> bool:
        return self._pressed_state
    
    def simulate_press(self, pressed: bool, position: Point2 = None, strength: float = 1.0) -> None:
        if pressed and not self._pressed_state:
            self._pressed_state = True
            self._pressed_position = position if position else Point2()
            for callback in self._pressed_callbacks:
                callback()
        elif not pressed and self._pressed_state:
            self._pressed_state = False
            for callback in self._released_callbacks:
                callback()
    
    def connect_pressed(self, callback: Callable) -> None:
        self._pressed_callbacks.append(callback)
    
    def connect_released(self, callback: Callable) -> None:
        self._released_callbacks.append(callback)
    
    def __repr__(self) -> str:
        return f"TouchScreenButton('{self.name}', action='{self._action}', pressed={self._pressed_state})"
