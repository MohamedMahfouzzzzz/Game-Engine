# /**************************************************************************/
# /*  light_occluder_2d.py                                                  */
# /**************************************************************************/

"""Godot LightOccluder2D port - Light shadow caster."""

from typing import List
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2


class OccluderPolygon2D:
    """Polygon for light occlusion."""
    
    def __init__(self):
        self._polygon: List[Point2] = []
        self._closed: bool = True
        self._cull_mode: int = 0  # 0=disabled, 1=clockwise, 2=counter-clockwise
    
    def set_polygon(self, polygon: List[Point2]) -> None:
        self._polygon = list(polygon)
    
    def get_polygon(self) -> List[Point2]:
        return self._polygon.copy()
    
    def set_closed(self, closed: bool) -> None:
        self._closed = closed
    
    def is_closed(self) -> bool:
        return self._closed
    
    def set_cull_mode(self, mode: int) -> None:
        self._cull_mode = mode
    
    def get_cull_mode(self) -> int:
        return self._cull_mode


class LightOccluder2D(Node2D):
    """Occludes light creating shadows."""
    
    def __init__(self, name: str = "LightOccluder2D"):
        super().__init__(name)
        self._occluder: OccluderPolygon2D = OccluderPolygon2D()
        self._sdf_collision: bool = False
        self._occluder_light_mask: int = 1
    
    def set_occluder_polygon(self, polygon: OccluderPolygon2D) -> None:
        self._occluder = polygon
    
    def get_occluder_polygon(self) -> OccluderPolygon2D:
        return self._occluder
    
    def set_as_sdf_collision(self, enable: bool) -> None:
        self._sdf_collision = enable
    
    def is_set_as_sdf_collision(self) -> bool:
        return self._sdf_collision
    
    def set_occluder_light_mask(self, mask: int) -> None:
        self._occluder_light_mask = mask
    
    def get_occluder_light_mask(self) -> int:
        return self._occluder_light_mask
    
    def __repr__(self) -> str:
        return f"LightOccluder2D('{self.name}', mask={self._occluder_light_mask})"
