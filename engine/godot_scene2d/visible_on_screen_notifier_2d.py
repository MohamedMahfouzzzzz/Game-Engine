# /**************************************************************************/
# /*  visible_on_screen_notifier_2d.py                                      */
# /**************************************************************************/

"""Godot VisibleOnScreenNotifier2D port - Screen visibility detection."""

from typing import Callable, List
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Size2, Rect2


class VisibleOnScreenNotifier2D(Node2D):
    """Detects when node enters/exits screen."""
    
    def __init__(self, name: str = "VisibleOnScreenNotifier2D"):
        super().__init__(name)
        self._rect: Rect2 = Rect2(Point2(-10, -10), Size2(20, 20))
        self._on_screen: bool = False
        self._on_screen_entered_callbacks: List[Callable] = []
        self._on_screen_exited_callbacks: List[Callable] = []
    
    def set_rect(self, rect: Rect2) -> None:
        self._rect = rect
    
    def get_rect(self) -> Rect2:
        return self._rect
    
    def is_on_screen(self) -> bool:
        return self._on_screen
    
    def connect_screen_entered(self, callback: Callable) -> None:
        self._on_screen_entered_callbacks.append(callback)
    
    def connect_screen_exited(self, callback: Callable) -> None:
        self._on_screen_exited_callbacks.append(callback)
    
    def _emit_screen_entered(self) -> None:
        self._on_screen = True
        for callback in self._on_screen_entered_callbacks:
            callback()
    
    def _emit_screen_exited(self) -> None:
        self._on_screen = False
        for callback in self._on_screen_exited_callbacks:
            callback()
    
    def __repr__(self) -> str:
        return f"VisibleOnScreenNotifier2D('{self.name}', rect={self._rect}, on_screen={self._on_screen})"


class VisibleOnScreenEnabler2D(Node2D):
    """Enables/disables node based on screen visibility."""
    
    def __init__(self, name: str = "VisibleOnScreenEnabler2D"):
        super().__init__(name)
        self._rect: Rect2 = Rect2(Point2(-10, -10), Size2(20, 20))
        self._enable_node_path: str = ".."
        self._enable_mode: int = 0
    
    def set_rect(self, rect: Rect2) -> None:
        self._rect = rect
    
    def get_rect(self) -> Rect2:
        return self._rect
    
    def __repr__(self) -> str:
        return f"VisibleOnScreenEnabler2D('{self.name}', rect={self._rect})"
