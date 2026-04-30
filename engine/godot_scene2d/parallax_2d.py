# /**************************************************************************/
# /*  parallax_2d.py                                                        */
# /**************************************************************************/

"""Godot Parallax2D port - Individual parallax node."""

from typing import Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Size2


class Parallax2D(Node2D):
    """Self-contained parallax scrolling node.
    
    Newer alternative to ParallaxBackground/Layer.
    """
    
    def __init__(self, name: str = "Parallax2D"):
        super().__init__(name)
        self._scroll_scale: Point2 = Point2(1, 1)
        self._repeat_size: Size2 = Size2()
        self._repeat_times: int = 1
        self._screen_offset: Point2 = Point2()
        self._limit_begin: Point2 = Point2(-10000000, -10000000)
        self._limit_end: Point2 = Point2(10000000, 10000000)
        self._autoscroll: Point2 = Point2()
    
    def set_scroll_scale(self, scale: Point2) -> None:
        self._scroll_scale = scale
    
    def get_scroll_scale(self) -> Point2:
        return self._scroll_scale
    
    def set_repeat_size(self, size: Size2) -> None:
        self._repeat_size = size
    
    def get_repeat_size(self) -> Size2:
        return self._repeat_size
    
    def set_repeat_times(self, times: int) -> None:
        self._repeat_times = max(1, times)
    
    def get_repeat_times(self) -> int:
        return self._repeat_times
    
    def set_screen_offset(self, offset: Point2) -> None:
        self._screen_offset = offset
    
    def get_screen_offset(self) -> Point2:
        return self._screen_offset
    
    def set_limit_begin(self, offset: Point2) -> None:
        self._limit_begin = offset
    
    def get_limit_begin(self) -> Point2:
        return self._limit_begin
    
    def set_limit_end(self, offset: Point2) -> None:
        self._limit_end = offset
    
    def get_limit_end(self) -> Point2:
        return self._limit_end
    
    def set_autoscroll(self, speed: Point2) -> None:
        self._autoscroll = speed
    
    def get_autoscroll(self) -> Point2:
        return self._autoscroll
    
    def __repr__(self) -> str:
        return f"Parallax2D('{self.name}', scale={self._scroll_scale}, repeat={self._repeat_times})"
