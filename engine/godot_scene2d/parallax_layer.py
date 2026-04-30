# /**************************************************************************/
# /*  parallax_layer.py                                                     */
# /**************************************************************************/

"""Godot ParallaxLayer port - Parallax layer child."""

from typing import Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Vector2i


class ParallaxLayer(Node2D):
    """Layer in a parallax background."""
    
    def __init__(self, name: str = "ParallaxLayer"):
        super().__init__(name)
        self._motion_scale: Point2 = Point2(1, 1)
        self._motion_offset: Point2 = Point2()
        self._motion_mirroring: Point2 = Point2()
        self._ignore_camera_zoom: bool = False
    
    def set_motion_scale(self, scale: Point2) -> None:
        self._motion_scale = scale
    
    def get_motion_scale(self) -> Point2:
        return self._motion_scale
    
    def set_motion_offset(self, offset: Point2) -> None:
        self._motion_offset = offset
    
    def get_motion_offset(self) -> Point2:
        return self._motion_offset
    
    def set_motion_mirroring(self, mirroring: Point2) -> None:
        self._motion_mirroring = mirroring
    
    def get_motion_mirroring(self) -> Point2:
        return self._motion_mirroring
    
    def set_ignore_camera_zoom(self, ignore: bool) -> None:
        self._ignore_camera_zoom = ignore
    
    def is_ignore_camera_zoom(self) -> bool:
        return self._ignore_camera_zoom
    
    def get_screen_offset(self) -> Point2:
        return Point2()
    
    def __repr__(self) -> str:
        return f"ParallaxLayer('{self.name}', scale={self._motion_scale}, mirroring={self._motion_mirroring})"
