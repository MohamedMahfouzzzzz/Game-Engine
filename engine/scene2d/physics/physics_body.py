# /**************************************************************************/
# /*  physics_body.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Base physics body for 2D physics simulation."""

from typing import Set
from engine.core.nodes2d import Node2D


class PhysicsBody2D(Node2D):
    """Base class for all 2D physics bodies.
    
    Provides collision layer/mask management and collision exceptions.
    """
    
    def __init__(self, name: str = "PhysicsBody2D"):
        super().__init__(name)
        self._collision_layer: int = 1
        self._collision_mask: int = 1
        self._input_pickable: bool = False
        self._collision_exceptions: Set[int] = set()
        self._collision_priority: float = 1.0
    
    def set_collision_layer(self, layer: int) -> None:
        self._collision_layer = layer
    
    def get_collision_layer(self) -> int:
        return self._collision_layer
    
    def set_collision_mask(self, mask: int) -> None:
        self._collision_mask = mask
    
    def get_collision_mask(self) -> int:
        return self._collision_mask
    
    def set_collision_layer_bit(self, bit: int, value: bool) -> None:
        if value:
            self._collision_layer |= (1 << bit)
        else:
            self._collision_layer &= ~(1 << bit)
    
    def get_collision_layer_bit(self, bit: int) -> bool:
        return (self._collision_layer & (1 << bit)) != 0
    
    def set_collision_mask_bit(self, bit: int, value: bool) -> None:
        if value:
            self._collision_mask |= (1 << bit)
        else:
            self._collision_mask &= ~(1 << bit)
    
    def get_collision_mask_bit(self, bit: int) -> bool:
        return (self._collision_mask & (1 << bit)) != 0
    
    def set_collision_priority(self, priority: float) -> None:
        self._collision_priority = max(0.0, priority)
    
    def get_collision_priority(self) -> float:
        return self._collision_priority
    
    def add_collision_exception_with(self, body: 'PhysicsBody2D') -> None:
        self._collision_exceptions.add(id(body))
    
    def remove_collision_exception_with(self, body: 'PhysicsBody2D') -> None:
        self._collision_exceptions.discard(id(body))
    
    def __repr__(self) -> str:
        return f"PhysicsBody2D('{self.name}', layer={self._collision_layer}, mask={self._collision_mask})"
