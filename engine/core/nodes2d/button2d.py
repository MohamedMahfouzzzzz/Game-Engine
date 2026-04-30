# /**************************************************************************/
# /*  button2d.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Button2D - Interactive button node with hover and pressed states."""

from __future__ import annotations

from typing import Optional, Callable, Any

from .types import Vector2, Color, Texture2D
from .node2d import Node2D
from .sprite2d import Sprite2D

import logging


logger = logging.getLogger(__name__)


class Button2D(Sprite2D):
    """Interactive button with visual states.
    
    Properties:
        text: Button text label
        font_size: Size of text (int)
        text_color: Color of text (Color)
        normal_texture: Texture when idle (Texture2D)
        hover_texture: Texture when hovered (Texture2D)
        pressed_texture: Texture when pressed (Texture2D)
        disabled: If True, button doesn't respond to input (bool)
        toggle_mode: If True, button stays pressed (bool)
        action_mode: Release or press to trigger (str)
        
    Signals:
        pressed: Emitted when button is pressed
        released: Emitted when button is released
        toggled: Emitted when toggle state changes
        hover_entered: Emitted when mouse enters
        hover_exited: Emitted when mouse exits
    """
    
    __slots__ = [
        "text", "font_size", "text_color",
        "normal_texture", "hover_texture", "pressed_texture",
        "disabled", "toggle_mode", "pressed_state", "hover_state",
        "action_mode"
    ]
    
    _SIGNALS = [
        "pressed", "released", "toggled",
        "hover_entered", "hover_exited", "clicked"
    ]
    
    def __init__(self, name: str = "Button2D"):
        super().__init__(name)
        self.node_type = "Button2D"
        
        # Text properties
        self.text: str = "Button"
        self.font_size: int = 16
        self.text_color: Color = Color.black()
        
        # State textures
        self.normal_texture: Optional[Texture2D] = None
        self.hover_texture: Optional[Texture2D] = None
        self.pressed_texture: Optional[Texture2D] = None
        
        # State
        self.disabled: bool = False
        self.toggle_mode: bool = False
        self.pressed_state: bool = False
        self.hover_state: bool = False
        self.action_mode: str = "release"  # "release" or "press"
    
    def set_text(self, text: str) -> None:
        """Set button text."""
        self.text = text
    
    def set_text_color(self, color: Color) -> None:
        """Set text color."""
        self.text_color = color
    
    def set_text_color_rgb(self, r: int, g: int, b: int) -> None:
        """Set text color from RGB values."""
        self.text_color = Color(r, g, b)
    
    def is_pressed(self) -> bool:
        """Check if button is in pressed state."""
        return self.pressed_state
    
    def is_hovered(self) -> bool:
        """Check if button is being hovered."""
        return self.hover_state
    
    def is_disabled(self) -> bool:
        """Check if button is disabled."""
        return self.disabled
    
    def set_disabled(self, disabled: bool) -> None:
        """Enable or disable button."""
        self.disabled = disabled
        if disabled:
            self.pressed_state = False
            self.hover_state = False
    
    def on_mouse_enter(self) -> None:
        """Called when mouse enters button area."""
        if self.disabled:
            return
        self.hover_state = True
        self.signals.emit("hover_entered")
    
    def on_mouse_exit(self) -> None:
        """Called when mouse exits button area."""
        self.hover_state = False
        self.signals.emit("hover_exited")
        
        # Release if pressed and not toggle mode
        if self.pressed_state and not self.toggle_mode:
            self.pressed_state = False
            self.signals.emit("released")
    
    def on_mouse_down(self) -> None:
        """Called when mouse button is pressed on button."""
        if self.disabled:
            return
        
        if self.toggle_mode:
            self.pressed_state = not self.pressed_state
            self.signals.emit("toggled", self.pressed_state)
            if self.pressed_state:
                self.signals.emit("pressed")
            else:
                self.signals.emit("released")
        else:
            self.pressed_state = True
            self.signals.emit("pressed")
            
            if self.action_mode == "press":
                self.signals.emit("clicked")
    
    def on_mouse_up(self) -> None:
        """Called when mouse button is released."""
        if self.disabled or self.toggle_mode:
            return
        
        if self.pressed_state:
            self.pressed_state = False
            self.signals.emit("released")
            
            if self.action_mode == "release" and self.hover_state:
                self.signals.emit("clicked")
    
    def _get_current_texture(self) -> Optional[Texture2D]:
        """Get texture for current state."""
        if self.disabled:
            return self.normal_texture
        if self.pressed_state:
            return self.pressed_texture or self.normal_texture
        if self.hover_state:
            return self.hover_texture or self.normal_texture
        return self.normal_texture
    
    def _draw(self, renderer) -> None:
        """Draw button with current state texture."""
        # Use state-specific texture
        original_texture = self.texture
        self.texture = self._get_current_texture() or self.texture
        
        # Draw as sprite
        super()._draw(renderer)
        
        # Restore original
        self.texture = original_texture
    
    def get_button_rect(self) -> tuple:
        """Get button rectangle for hit testing."""
        pos = self.get_global_position()
        
        if self.texture and self.texture.is_loaded():
            width = self.texture.width
            height = self.texture.height
        else:
            width = 100
            height = 40
        
        if self.centered:
            return (pos.x - width/2, pos.y - height/2, width, height)
        return (pos.x, pos.y, width, height)
    
    def contains_point(self, point: Vector2) -> bool:
        """Check if point is inside button."""
        x, y, w, h = self.get_button_rect()
        return x <= point.x <= x + w and y <= point.y <= y + h
