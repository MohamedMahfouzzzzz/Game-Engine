# /**************************************************************************/
# /*  ui_nodes.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""UI control nodes for in-game interfaces."""

from typing import Callable, List, Optional, Tuple
from engine.core.node_base import Node2D
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Control(Node2D):
    """Base class for UI controls."""

    def __init__(self, name: str = "Control"):
        super().__init__(name)
        self.node_type = NodeType.CONTROL

        # Layout properties
        self.size: Tuple[int, int] = (100, 50)
        self.min_size: Tuple[int, int] = (0, 0)
        self.max_size: Tuple[int, int] = (99999, 99999)
        self.margin: Tuple[int, int, int, int] = (0, 0, 0, 0)  # left, top, right, bottom

        # Visual properties
        self.background_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
        self.border_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
        self.border_width: int = 0

        # Interaction
        self.mouse_filter: int = 0  # 0=stop, 1=pass, 2=ignore
        self.focus_mode: int = 0  # 0=none, 1=click, 2=all
        self.disabled: bool = False
        self.visible: bool = True

        # Anchors (for responsive layout)
        self.anchor_left: float = 0.0
        self.anchor_top: float = 0.0
        self.anchor_right: float = 0.0
        self.anchor_bottom: float = 0.0

        # Callbacks
        self.on_click: Optional[Callable] = None
        self.on_hover: Optional[Callable] = None

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside control bounds."""
        pos_x, pos_y = self.get_position()
        return (pos_x <= x <= pos_x + self.size[0] and
                pos_y <= y <= pos_y + self.size[1])

    def set_size(self, width: int, height: int) -> None:
        """Set control size."""
        w = max(self.min_size[0], min(width, self.max_size[0]))
        h = max(self.min_size[1], min(height, self.max_size[1]))
        self.size = (w, h)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "size": self.size,
            "min_size": self.min_size,
            "max_size": self.max_size,
            "margin": self.margin,
            "background_color": self.background_color,
            "border_color": self.border_color,
            "border_width": self.border_width,
            "disabled": self.disabled,
            "anchor_left": self.anchor_left,
            "anchor_top": self.anchor_top,
            "anchor_right": self.anchor_right,
            "anchor_bottom": self.anchor_bottom,
        })
        return data


class Label(Control):
    """Text display control."""

    def __init__(self, name: str = "Label", text: str = ""):
        super().__init__(name)
        self.node_type = NodeType.LABEL
        self.text: str = text
        self.font_size: int = 14
        self.font_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self.alignment: int = 0  # 0=left, 1=center, 2=right
        self.valignment: int = 0  # 0=top, 1=center, 2=bottom
        self.wrap_enabled: bool = False
        self.autowrap: bool = False
        self.uppercase: bool = False

    def set_text(self, text: str) -> None:
        """Set label text."""
        self.text = text.upper() if self.uppercase else text

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "text": self.text,
            "font_size": self.font_size,
            "font_color": self.font_color,
            "alignment": self.alignment,
            "valignment": self.valignment,
            "wrap_enabled": self.wrap_enabled,
            "autowrap": self.autowrap,
            "uppercase": self.uppercase,
        })
        return data


class Button(Control):
    """Clickable button control."""

    def __init__(self, name: str = "Button", text: str = "Button"):
        super().__init__(name)
        self.node_type = NodeType.BUTTON
        self.text: str = text
        self.font_size: int = 14
        self.font_color: Tuple[int, int, int, int] = (255, 255, 255, 255)

        # Button states
        self.pressed: bool = False
        self.hovered: bool = False

        # Colors for states
        self.normal_color: Tuple[int, int, int, int] = (64, 64, 64, 255)
        self.hover_color: Tuple[int, int, int, int] = (80, 80, 80, 255)
        self.pressed_color: Tuple[int, int, int, int] = (48, 48, 48, 255)
        self.disabled_color: Tuple[int, int, int, int] = (32, 32, 32, 255)

        # Callbacks
        self._on_pressed: List[Callable] = []
        self._on_released: List[Callable] = []

    def press(self) -> None:
        """Simulate button press."""
        self.pressed = True
        for cb in self._on_pressed:
            cb()

    def release(self) -> None:
        """Simulate button release."""
        self.pressed = False
        for cb in self._on_released:
            cb()

    def connect_pressed(self, callback: Callable) -> None:
        """Connect callback to pressed signal."""
        self._on_pressed.append(callback)

    def connect_released(self, callback: Callable) -> None:
        """Connect callback to released signal."""
        self._on_released.append(callback)

    def get_current_color(self) -> Tuple[int, int, int, int]:
        """Get current button color based on state."""
        if self.disabled:
            return self.disabled_color
        if self.pressed:
            return self.pressed_color
        if self.hovered:
            return self.hover_color
        return self.normal_color

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "text": self.text,
            "font_size": self.font_size,
            "font_color": self.font_color,
            "normal_color": self.normal_color,
            "hover_color": self.hover_color,
            "pressed_color": self.pressed_color,
            "disabled_color": self.disabled_color,
        })
        return data


class Panel(Control):
    """Container panel for grouping controls."""

    def __init__(self, name: str = "Panel"):
        super().__init__(name)
        self.node_type = NodeType.PANEL

        # Panel styling
        self.corner_radius: int = 4
        self.shadow_enabled: bool = False
        self.shadow_size: int = 4
        self.shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 128)

    def add_child(self, child: "Node") -> None:
        """Add a child control with type safety."""
        if not isinstance(child, Control):
            raise TypeError("Panel children must be Control nodes")
        super().add_child(child)

    def remove_child(self, child: "Node") -> None:
        """Remove a child control."""
        super().remove_child(child)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "corner_radius": self.corner_radius,
            "shadow_enabled": self.shadow_enabled,
            "shadow_size": self.shadow_size,
            "shadow_color": self.shadow_color,
        })
        return data
