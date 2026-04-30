# /**************************************************************************/
# /*  touch_button.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Touch screen button for mobile input."""

from enum import IntEnum
from typing import Optional, Callable
from engine.core.nodes2d import Node2D, Vector2
from engine.scene2d.sprite import Texture2D


class TouchScreenButton(Node2D):
    """Button for touch screens.
    
    Can be:
    - Normal button (press/release)
    - Joystick/DPad (analog direction)
    
    Automatically handles multi-touch.
    """
    
    VISIBILITY_ALWAYS = 0
    VISIBILITY_TOUCHSCREEN_ONLY = 1
    VISIBILITY_WHEN_TOUCHED = 2
    
    def __init__(self, name: str = "TouchScreenButton"):
        super().__init__(name)
        self._texture_normal: Optional[Texture2D] = None
        self._texture_pressed: Optional[Texture2D] = None
        self._bitmask = None
        self._shape = None
        self._shape_centered: bool = True
        self._shape_visible: bool = True
        self._passby_press: bool = False
        self._action: str = ""
        self._visibility_mode: int = self.VISIBILITY_ALWAYS
        
        # State
        self._is_pressed: bool = False
        self._finger_pressed: int = -1
        
        # Callbacks
        self._pressed_callback: Optional[Callable] = None
        self._released_callback: Optional[Callable] = None
    
    def set_texture_normal(self, texture: Optional[Texture2D]) -> None:
        """Set normal state texture."""
        self._texture_normal = texture
    
    def get_texture_normal(self) -> Optional[Texture2D]:
        return self._texture_normal
    
    def set_texture_pressed(self, texture: Optional[Texture2D]) -> None:
        """Set pressed state texture."""
        self._texture_pressed = texture
    
    def get_texture_pressed(self) -> Optional[Texture2D]:
        return self._texture_pressed
    
    def set_shape_centered(self, centered: bool) -> None:
        """Center the shape on the node."""
        self._shape_centered = centered
    
    def is_shape_centered(self) -> bool:
        return self._shape_centered
    
    def set_shape_visible(self, visible: bool) -> None:
        """Show/hide shape outline in editor."""
        self._shape_visible = visible
    
    def is_shape_visible(self) -> bool:
        return self._shape_visible
    
    def set_passby_press(self, passby: bool) -> None:
        """Trigger when finger passes over."""
        self._passby_press = passby
    
    def is_passby_press_enabled(self) -> bool:
        return self._passby_press
    
    def set_action(self, action: str) -> None:
        """Input action to trigger."""
        self._action = action
    
    def get_action(self) -> str:
        return self._action
    
    def set_visibility_mode(self, mode: int) -> None:
        """When button is visible."""
        self._visibility_mode = mode
    
    def get_visibility_mode(self) -> int:
        return self._visibility_mode
    
    def is_pressed(self) -> bool:
        """Returns true if currently pressed."""
        return self._is_pressed
    
    def set_pressed_callback(self, callback: Optional[Callable]) -> None:
        """Called when button pressed."""
        self._pressed_callback = callback
    
    def set_released_callback(self, callback: Optional[Callable]) -> None:
        """Called when button released."""
        self._released_callback = callback
    
    def _handle_touch(self, pressed: bool, finger: int = 0) -> None:
        """Handle touch event."""
        was_pressed = self._is_pressed
        self._is_pressed = pressed
        
        if pressed and not was_pressed:
            self._finger_pressed = finger
            if self._pressed_callback:
                self._pressed_callback()
        elif not pressed and was_pressed:
            self._finger_pressed = -1
            if self._released_callback:
                self._released_callback()
    
    def __repr__(self) -> str:
        return f"TouchScreenButton('{self.name}', action='{self._action}', pressed={self._is_pressed})"
