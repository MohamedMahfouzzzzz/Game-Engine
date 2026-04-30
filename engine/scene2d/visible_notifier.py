# /**************************************************************************/
# /*  visible_notifier.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D visibility notifier - detects when on/off screen."""

from typing import Callable, Optional
from engine.core.nodes2d import Node2D, Rect2


class VisibleOnScreenNotifier2D(Node2D):
    """Notifies when node enters/leaves screen.
    
    Useful for:
    - Activating/deactivating enemies
    - Starting/stopping animations
    - Streaming content
    - Performance optimization
    """
    
    def __init__(self, name: str = "VisibleOnScreenNotifier2D"):
        super().__init__(name)
        self._rect: Rect2 = Rect2(-10, -10, 20, 20)
        self._is_on_screen: bool = False
        
        # Callbacks
        self._on_screen_callback: Optional[Callable] = None
        self._off_screen_callback: Optional[Callable] = None
    
    def set_rect(self, rect: Rect2) -> None:
        """Set detection rectangle in local coordinates."""
        self._rect = rect
    
    def get_rect(self) -> Rect2:
        return self._rect
    
    def is_on_screen(self) -> bool:
        """Returns true if currently visible on screen."""
        return self._is_on_screen
    
    def set_on_screen_callback(self, callback: Optional[Callable]) -> None:
        """Called when entering screen."""
        self._on_screen_callback = callback
    
    def set_off_screen_callback(self, callback: Optional[Callable]) -> None:
        """Called when leaving screen."""
        self._off_screen_callback = callback
    
    def _update_visibility(self, camera_rect: Rect2) -> None:
        """Update visibility state based on camera."""
        # Transform local rect to global
        global_rect = Rect2(
            self._rect.x + self.position.x,
            self._rect.y + self._rect.y,
            self._rect.w,
            self._rect.h
        )
        
        # Check intersection
        was_on_screen = self._is_on_screen
        self._is_on_screen = (
            global_rect.x < camera_rect.x + camera_rect.w and
            global_rect.x + global_rect.w > camera_rect.x and
            global_rect.y < camera_rect.y + camera_rect.h and
            global_rect.y + global_rect.h > camera_rect.y
        )
        
        # Trigger callbacks
        if not was_on_screen and self._is_on_screen:
            if self._on_screen_callback:
                self._on_screen_callback()
        elif was_on_screen and not self._is_on_screen:
            if self._off_screen_callback:
                self._off_screen_callback()
    
    def __repr__(self) -> str:
        return f"VisibleOnScreenNotifier2D('{self.name}', on_screen={self._is_on_screen})"


class VisibleOnScreenEnabler2D(Node2D):
    """Automatically enables/disables nodes based on visibility.
    
    More efficient than notifier - directly controls node processing.
    """
    
    ENABLE_MODE_INHERIT = 0
    ENABLE_MODE_ALWAYS = 1
    ENABLE_MODE_WHEN_VISIBLE = 2
    
    def __init__(self, name: str = "VisibleOnScreenEnabler2D"):
        super().__init__(name)
        self._rect: Rect2 = Rect2(-10, -10, 20, 20)
        self._enable_node_path: str = ".."
        self._enable_mode: int = self.ENABLE_MODE_INHERIT
    
    def set_rect(self, rect: Rect2) -> None:
        self._rect = rect
    
    def get_rect(self) -> Rect2:
        return self._rect
    
    def set_enable_node_path(self, path: str) -> None:
        """Node path to enable/disable."""
        self._enable_node_path = path
    
    def get_enable_node_path(self) -> str:
        return self._enable_node_path
    
    def set_enable_mode(self, mode: int) -> None:
        """When to enable the target node."""
        self._enable_mode = mode
    
    def get_enable_mode(self) -> int:
        return self._enable_mode
    
    def __repr__(self) -> str:
        return f"VisibleOnScreenEnabler2D('{self.name}', path='{self._enable_node_path}')"
