# /**************************************************************************/
# /*  parallax_background.py                                                */
# /**************************************************************************/

"""Godot ParallaxBackground port - Parallax scrolling background."""

from typing import Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Vector2i


class ParallaxBackground(Node2D):
    """Parallax background with scrolling layers."""
    
    def __init__(self, name: str = "ParallaxBackground"):
        super().__init__(name)
        self._scroll_offset: Point2 = Point2()
        self._scroll_base_offset: Point2 = Point2()
        self._scroll_base_scale: Point2 = Point2(1, 1)
        self._scroll_limit_begin: Point2 = Point2(-10000000, -10000000)
        self._scroll_limit_end: Point2 = Point2(10000000, 10000000)
        self._scroll_ignore_camera_zoom: bool = False
        self._screen_offset: Point2 = Point2()
    
    def set_scroll_offset(self, offset: Point2) -> None:
        self._scroll_offset = offset
    
    def get_scroll_offset(self) -> Point2:
        return self._scroll_offset
    
    def set_scroll_base_offset(self, offset: Point2) -> None:
        self._scroll_base_offset = offset
    
    def get_scroll_base_offset(self) -> Point2:
        return self._scroll_base_offset
    
    def set_scroll_base_scale(self, scale: Point2) -> None:
        self._scroll_base_scale = scale
    
    def get_scroll_base_scale(self) -> Point2:
        return self._scroll_base_scale
    
    def set_scroll_limit_begin(self, offset: Point2) -> None:
        self._scroll_limit_begin = offset
    
    def get_scroll_limit_begin(self) -> Point2:
        return self._scroll_limit_begin
    
    def set_scroll_limit_end(self, offset: Point2) -> None:
        self._scroll_limit_end = offset
    
    def get_scroll_limit_end(self) -> Point2:
        return self._scroll_limit_end
    
    def set_scroll_ignore_camera_zoom(self, ignore: bool) -> None:
        self._scroll_ignore_camera_zoom = ignore
    
    def is_scroll_ignore_camera_zoom(self) -> bool:
        return self._scroll_ignore_camera_zoom
    
    def get_final_offset(self) -> Point2:
        return Point2(
            self._scroll_offset.x + self._scroll_base_offset.x,
            self._scroll_offset.y + self._scroll_base_offset.y
        )
    
    def __repr__(self) -> str:
        return f"ParallaxBackground('{self.name}', offset={self._scroll_offset})"
