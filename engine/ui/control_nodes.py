# /**************************************************************************/
# /*  control_nodes.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Godot-inspired UI Control Nodes

Control: Base UI element with box model
Container: Automatic child layout
HBoxContainer: Horizontal layout
VBoxContainer: Vertical layout

Features:
- Anchors and margins for responsive UI
- Size flags for layout behavior
- Focus and input handling
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass

from engine.core.nodes2d import Node2D, Vector2, Color
from engine.core.types import NodeType

import logging



# =============================================================================
# Anchor Enum
# =============================================================================

logger = logging.getLogger(__name__)

class Anchor(Enum):
    """Screen anchor points for responsive positioning."""
    BEGIN = 0.0      # Left or Top
    CENTER = 0.5     # Center
    END = 1.0        # Right or Bottom
    
    # Common presets
    TOP_LEFT = (BEGIN, BEGIN)
    TOP_CENTER = (CENTER, BEGIN)
    TOP_RIGHT = (END, BEGIN)
    CENTER_LEFT = (BEGIN, CENTER)
    CENTER_CENTER = (CENTER, CENTER)
    CENTER_RIGHT = (END, CENTER)
    BOTTOM_LEFT = (BEGIN, END)
    BOTTOM_CENTER = (CENTER, END)
    BOTTOM_RIGHT = (END, END)
    FILL_LEFT_WIDE = (BEGIN, BEGIN, 0, END)  # x, y, x2, y2


# =============================================================================
# Size Flag Enum
# =============================================================================

class SizeFlag(Enum):
    """Flags controlling how children behave in containers."""
    NONE = 0
    FILL = 1           # Fill available space
    EXPAND = 2         # Expand to take extra space
    SHRINK_CENTER = 4  # Shrink to fit, centered
    SHRINK_END = 8     # Shrink to fit, aligned to end


# =============================================================================
# Margin
# =============================================================================

@dataclass
class Margin:
    """Space between edges and content."""
    left: float = 0
    top: float = 0
    right: float = 0
    bottom: float = 0
    
    @classmethod
    def all(cls, value: float) -> Margin:
        return cls(value, value, value, value)
    
    @classmethod
    def symmetric(cls, horizontal: float, vertical: float) -> Margin:
        return cls(horizontal, vertical, horizontal, vertical)
    
    @property
    def width(self) -> float:
        return self.left + self.right
    
    @property
    def height(self) -> float:
        return self.top + self.bottom


# =============================================================================
# Control (Base UI Node)
# =============================================================================

class Control(Node2D):
    """Base class for UI elements.
    
    Features:
    - Anchors: Stay relative to screen edges/center
    - Margins: Space around content
    - Size: Minimum and preferred size
    - Focus: Keyboard focus handling
    
    Properties:
        anchor_left/right/top/bottom: Position relative to parent (0.0-1.0)
        margin_left/right/top/bottom: Pixel offset from anchor
        rect_min_size: Minimum width/height (Vector2)
        rect_size: Current size (Vector2)
        focus_mode: How focus behaves (None, Click, All)
        mouse_filter: How mouse events propagate
    
    Signals:
        resized: When size changes
        focus_entered: When gaining focus
        focus_exited: When losing focus
        mouse_entered: Mouse enters control
        mouse_exited: Mouse leaves control
        gui_input: When receiving input event
    """
    
    class FocusMode(Enum):
        NONE = auto()       # Cannot receive focus
        CLICK = auto()      # Focus on click only
        ALL = auto()        # Can receive focus programmatically
    
    class MouseFilter(Enum):
        STOP = auto()       # Block events to parent
        PASS = auto()       # Pass events to parent
        IGNORE = auto()     # Don't receive events
    
    # Additional slots
    __slots__ = [
        "anchor_left", "anchor_right", "anchor_top", "anchor_bottom",
        "margin_left", "margin_right", "margin_top", "margin_bottom",
        "rect_min_size", "rect_size",
        "focus_mode", "mouse_filter",
        "has_focus", "mouse_over",
        "theme_override"
    ]
    
    _SIGNALS = [
        "resized",
        "focus_entered", "focus_exited",
        "mouse_entered", "mouse_exited",
        "gui_input"
    ]
    
    def __init__(self, name: str = "Control"):
        super().__init__(name)
        
        # Anchors (0.0-1.0, relative to parent)
        self.anchor_left = 0.0
        self.anchor_right = 0.0
        self.anchor_top = 0.0
        self.anchor_bottom = 0.0
        
        # Margins (pixels, offset from anchor)
        self.margin_left = 0.0
        self.margin_right = 0.0
        self.margin_top = 0.0
        self.margin_bottom = 0.0
        
        # Size constraints
        self.rect_min_size = Vector2(0, 0)
        self.rect_size = Vector2(100, 40)  # Default size
        
        # Interaction
        self.focus_mode = self.FocusMode.CLICK
        self.mouse_filter = self.MouseFilter.STOP
        
        # State
        self.has_focus = False
        self.mouse_over = False
        
        # Theme overrides
        self.theme_override: Dict[str, Any] = {}
    
    # =======================================================================
    # Layout
    # =======================================================================
    
    def set_anchors_preset(self, preset: str, keep_size: bool = False) -> None:
        """Set anchor layout preset.
        
        Presets:
            "top_left", "top_right", "bottom_left", "bottom_right"
            "center", "center_top", "center_bottom", "center_left", "center_right"
            "full_rect", "wide"
        """
        presets = {
            "top_left": (0.0, 0.0, 0.0, 0.0),      # l, r, t, b
            "top_right": (1.0, 1.0, 0.0, 0.0),
            "bottom_left": (0.0, 0.0, 1.0, 1.0),
            "bottom_right": (1.0, 1.0, 1.0, 1.0),
            "center": (0.5, 0.5, 0.5, 0.5),
            "center_top": (0.5, 0.5, 0.0, 0.0),
            "full_rect": (0.0, 1.0, 0.0, 1.0),     # Fill parent
            "wide": (0.0, 1.0, 0.5, 0.5),          # Full width, center height
        }
        
        if preset in presets:
            l, r, t, b = presets[preset]
            self.anchor_left = l
            self.anchor_right = r
            self.anchor_top = t
            self.anchor_bottom = b
    
    def set_margins(self, left: float = None, top: float = None,
                   right: float = None, bottom: float = None) -> None:
        """Set all margins at once."""
        if left is not None:
            self.margin_left = left
        if top is not None:
            self.margin_top = top
        if right is not None:
            self.margin_right = right
        if bottom is not None:
            self.margin_bottom = bottom
    
    def get_rect(self) -> tuple:
        """Get (x, y, width, height) in parent space."""
        return (
            self.position.x,
            self.position.y,
            self.rect_size.x,
            self.rect_size.y
        )
    
    def get_global_rect(self) -> tuple:
        """Get rect in screen coordinates."""
        global_pos = self.get_global_position()
        return (
            global_pos.x,
            global_pos.y,
            self.rect_size.x,
            self.rect_size.y
        )
    
    def get_minimum_size(self) -> Vector2:
        """Get minimum required size."""
        return self.rect_min_size
    
    def set_size(self, size: Vector2, keep_offsets: bool = False) -> None:
        """Set control size."""
        old_size = self.rect_size
        self.rect_size = Vector2(
            max(size.x, self.rect_min_size.x),
            max(size.y, self.rect_min_size.y)
        )
        
        if old_size.x != self.rect_size.x or old_size.y != self.rect_size.y:
            self.signals.emit("resized", self.rect_size)
    
    def has_point(self, point: Vector2) -> bool:
        """Check if point is inside control rect."""
        pos = self.get_global_position()
        return (
            pos.x <= point.x <= pos.x + self.rect_size.x and
            pos.y <= point.y <= pos.y + self.rect_size.y
        )
    
    # =======================================================================
    # Focus
    # =======================================================================
    
    def grab_focus(self) -> None:
        """Steal focus from another control."""
        if self.focus_mode == self.FocusMode.NONE:
            return
        
        # Release focus from current
        # This would interact with a focus manager
        self.has_focus = True
        self.signals.emit("focus_entered")
    
    def release_focus(self) -> None:
        """Give up focus."""
        if self.has_focus:
            self.has_focus = False
            self.signals.emit("focus_exited")
    
    def is_focused(self) -> bool:
        """Check if has focus."""
        return self.has_focus
    
    def find_next_focus(self) -> Optional[Control]:
        """Find next control in tab order."""
        # Simplified - would traverse children
        return None
    
    def find_prev_focus(self) -> Optional[Control]:
        """Find previous control in tab order."""
        return None
    
    # =======================================================================
    # Input
    # =======================================================================
    
    def _on_mouse_enter(self) -> None:
        """Called when mouse enters."""
        if not self.mouse_over:
            self.mouse_over = True
            self.signals.emit("mouse_entered")
    
    def _on_mouse_exit(self) -> None:
        """Called when mouse leaves."""
        if self.mouse_over:
            self.mouse_over = False
            self.signals.emit("mouse_exited")
    
    def _gui_input(self, event: Any) -> None:
        """Process input event.
        
        Args:
            event: InputEvent with type and data
        """
        self.signals.emit("gui_input", event)
    
    def accepts_event(self, event: Any) -> bool:
        """Check if control should handle this event."""
        if not self.visible:
            return False
        if self.mouse_filter == self.MouseFilter.IGNORE:
            return False
        return True
    
    # =======================================================================
    # Drawing
    # =======================================================================
    
    def _draw(self, renderer) -> None:
        """Render control background/border."""
        # Base Control draws nothing - subclasses override
        pass
    
    def queue_redraw(self) -> None:
        """Request redraw."""
        # Would mark for redraw in next frame
        pass


# =============================================================================
# Container (Base for Layout Managers)
# =============================================================================

class Container(Control):
    """Base class for automatic child layout.
    
    Containers arrange children according to their rules.
    Children use size_flags to control their behavior.
    """
    
    __slots__ = ["separation", "theme"]
    
    def __init__(self, name: str = "Container"):
        super().__init__(name)
        
        self.separation = 4  # Pixels between children
        self.theme: Dict[str, Any] = {}
    
    def queue_sort(self) -> None:
        """Request child re-sorting."""
        # Would queue for next frame
        self._sort_children()
    
    def _sort_children(self) -> None:
        """Override to implement layout logic."""
        pass
    
    def fit_child_in_rect(self, child: Control, rect: tuple) -> None:
        """Position child within rectangle respecting anchors."""
        x, y, width, height = rect
        
        # Simple positioning - full rect
        child.position = Vector2(x, y)
        
        # Apply size respecting minimums
        min_size = child.get_minimum_size()
        child_size = Vector2(
            max(width, min_size.x),
            max(height, min_size.y)
        )
        child.set_size(child_size)


# =============================================================================
# HBoxContainer
# =============================================================================

class HBoxContainer(Container):
    """Horizontal box container.
    
    Arranges children left-to-right. Each child can:
    - FILL: Fill their allocated space
    - EXPAND: Take extra available space
    
    Example:
        container = HBoxContainer()
        
        child1 = Button("Small")
        child1.size_flags = SizeFlag.FILL
        container.add_child(child1)
        
        child2 = Button("Big")
        child2.size_flags = SizeFlag.EXPAND | SizeFlag.FILL
        container.add_child(child2)
        # child2 takes all extra space
    """
    
    __slots__ = ["alignment"]
    
    class Alignment(Enum):
        BEGIN = auto()      # Left-align
        CENTER = auto()     # Center
        END = auto()        # Right-align
        FILL = auto()       # Stretch to fill
    
    def __init__(self, name: str = "HBoxContainer"):
        super().__init__(name)
        self.alignment = self.Alignment.CENTER
    
    def _sort_children(self) -> None:
        """Layout children horizontally."""
        # Get visible children
        children = [c for c in self.children 
                   if isinstance(c, Control) and c.visible]
        
        if not children:
            return
        
        # Calculate minimum widths
        min_widths = []
        min_heights = []
        expands = []
        
        for child in children:
            min_size = child.get_minimum_size()
            min_widths.append(min_size.x)
            min_heights.append(min_size.y)
            
            # Check if child wants to expand
            has_expand = hasattr(child, 'size_flags_horizontal') and \
                        child.size_flags_horizontal and \
                        SizeFlag.EXPAND in child.size_flags_horizontal
            expands.append(1 if has_expand else 0)
        
        total_min_width = sum(min_widths) + self.separation * (len(children) - 1)
        max_min_height = max(min_heights) if min_heights else 0
        
        # Available space
        available_width = self.rect_size.x - total_min_width
        available_height = self.rect_size.y
        
        # Distribute extra space to expanding children
        total_expand = sum(expands)
        if total_expand > 0 and available_width > 0:
            expand_width = available_width / total_expand
            for i, child in enumerate(children):
                if expands[i]:
                    min_widths[i] += expand_width
        
        # Position children
        current_x = 0
        for i, child in enumerate(children):
            child_width = min_widths[i]
            child_height = min(min_heights[i], available_height)
            
            # Center vertically if space allows
            y_offset = (available_height - child_height) / 2
            
            child.position = Vector2(current_x, y_offset)
            child.set_size(Vector2(child_width, child_height))
            
            current_x += child_width + self.separation


# =============================================================================
# VBoxContainer
# =============================================================================

class VBoxContainer(Container):
    """Vertical box container.
    
    Arranges children top-to-bottom. Each child can:
    - FILL: Fill their allocated space
    - EXPAND: Take extra available space
    """
    
    __slots__ = ["alignment"]
    
    class Alignment(Enum):
        BEGIN = auto()      # Top-align
        CENTER = auto()     # Center
        END = auto()        # Bottom-align
        FILL = auto()       # Stretch to fill
    
    def __init__(self, name: str = "VBoxContainer"):
        super().__init__(name)
        self.alignment = self.Alignment.CENTER
    
    def _sort_children(self) -> None:
        """Layout children vertically."""
        children = [c for c in self.children 
                   if isinstance(c, Control) and c.visible]
        
        if not children:
            return
        
        # Calculate minimum heights
        min_widths = []
        min_heights = []
        expands = []
        
        for child in children:
            min_size = child.get_minimum_size()
            min_widths.append(min_size.x)
            min_heights.append(min_size.y)
            
            has_expand = hasattr(child, 'size_flags_vertical') and \
                        child.size_flags_vertical and \
                        SizeFlag.EXPAND in child.size_flags_vertical
            expands.append(1 if has_expand else 0)
        
        total_min_height = sum(min_heights) + self.separation * (len(children) - 1)
        max_min_width = max(min_widths) if min_widths else 0
        
        available_height = self.rect_size.y - total_min_height
        available_width = self.rect_size.x
        
        # Distribute extra height
        total_expand = sum(expands)
        if total_expand > 0 and available_height > 0:
            expand_height = available_height / total_expand
            for i, child in enumerate(children):
                if expands[i]:
                    min_heights[i] += expand_height
        
        # Position children
        current_y = 0
        for i, child in enumerate(children):
            child_width = min(min_widths[i], available_width)
            child_height = min_heights[i]
            
            # Center horizontally
            x_offset = (available_width - child_width) / 2
            
            child.position = Vector2(x_offset, current_y)
            child.set_size(Vector2(child_width, child_height))
            
            current_y += child_height + self.separation


# =============================================================================
# Common UI Controls
# =============================================================================

class Button(Control):
    """Clickable button control."""
    
    __slots__ = ["text", "pressed", "size_flags_horizontal", "size_flags_vertical"]
    
    _SIGNALS = ["pressed", "button_down", "button_up"]
    
    def __init__(self, text: str = "Button", name: str = "Button"):
        super().__init__(name)
        
        self.text = text
        self.pressed = False
        
        self.size_flags_horizontal = {SizeFlag.FILL}
        self.size_flags_vertical = {SizeFlag.FILL}
        
        self.rect_min_size = Vector2(80, 30)
        self.set_size(Vector2(100, 40))
    
    def _on_pressed(self) -> None:
        """Handle press."""
        self.signals.emit("pressed")
    
    def _draw(self, renderer) -> None:
        """Draw button."""
        # Would draw button background and text
        pass


class Label(Control):
    """Text display control."""
    
    __slots__ = ["text", "autowrap", "clip_text"]
    
    def __init__(self, text: str = "", name: str = "Label"):
        super().__init__(name)
        
        self.text = text
        self.autowrap = False
        self.clip_text = False
        
        self.rect_min_size = Vector2(10, 20)
    
    def get_minimum_size(self) -> Vector2:
        """Calculate size based on text."""
        # Would measure text
        base = super().get_minimum_size()
        # Add text dimensions
        return Vector2(base.x + len(self.text) * 8, base.y)


class Panel(Control):
    """Panel with background."""
    
    __slots__ = ["panel_style"]
    
    def __init__(self, name: str = "Panel"):
        super().__init__(name)
        
        self.panel_style: Dict[str, Any] = {
            "background_color": Color(0.2, 0.2, 0.2, 1.0),
            "border_width": 1,
            "border_color": Color(0.4, 0.4, 0.4, 1.0),
            "corner_radius": 4,
        }


# =============================================================================
# GridContainer
# =============================================================================

class GridContainer(Container):
    """Grid layout container.
    
    Arranges children in rows and columns.
    
    Properties:
        columns: Number of columns (int)
        rows: Number of rows (int, 0 = auto)
    """
    
    __slots__ = ["columns", "rows"]
    
    def __init__(self, name: str = "GridContainer"):
        super().__init__(name)
        
        self.columns = 1
        self.rows = 0  # 0 = auto calculate
    
    def _sort_children(self) -> None:
        """Layout children in grid."""
        children = [c for c in self.children 
                   if isinstance(c, Control) and c.visible]
        
        if not children:
            return
        
        # Calculate grid dimensions
        cols = self.columns
        rows = (len(children) + cols - 1) // cols  # Ceiling division
        
        # Calculate cell sizes
        cell_width = (self.rect_size.x - self.separation * (cols - 1)) / cols
        cell_height = (self.rect_size.y - self.separation * (rows - 1)) / rows
        
        # Position children
        for i, child in enumerate(children):
            col = i % cols
            row = i // cols
            
            x = col * (cell_width + self.separation)
            y = row * (cell_height + self.separation)
            
            child.position = Vector2(x, y)
            child.set_size(Vector2(cell_width, cell_height))


# =============================================================================
# MarginContainer
# =============================================================================

class MarginContainer(Container):
    """Container with padding around edges."""
    
    __slots__ = ["margin"]
    
    def __init__(self, name: str = "MarginContainer"):
        super().__init__(name)
        
        self.margin = Margin.all(10)
    
    def _sort_children(self) -> None:
        """Position children inside margins."""
        children = [c for c in self.children 
                   if isinstance(c, Control) and c.visible]
        
        if not children:
            return
        
        # Available space after margins
        avail_width = self.rect_size.x - self.margin.width
        avail_height = self.rect_size.y - self.margin.height
        
        # Position each child
        x = self.margin.left
        y = self.margin.top
        
        for child in children:
            child.position = Vector2(x, y)
            child.set_size(Vector2(avail_width, avail_height))


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Anchor",
    "SizeFlag",
    "Margin",
    "Control",
    "Container",
    "HBoxContainer",
    "VBoxContainer",
    "GridContainer",
    "MarginContainer",
    "Button",
    "Label",
    "Panel",
]
