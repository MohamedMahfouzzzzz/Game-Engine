# /**************************************************************************/
# /*  animation_tree.py                                                     */
# /**************************************************************************/

"""AnimationTree - Advanced animation blending with trees and state machines."""

from typing import Optional, Dict, Any
from engine.core.nodes2d import Node2D
from engine.godot_animation.animation_player import AnimationPlayer
from engine.godot_animation.animation_node import AnimationNode, AnimationNodeStateMachine, AnimationNodeStateMachinePlayback


class AnimationTree(Node2D):
    """Advanced animation blending using trees and state machines."""
    
    def __init__(self, name: str = "AnimationTree"):
        super().__init__(name)
        self._animation_player: Optional[AnimationPlayer] = None
        self._tree_root: Optional[AnimationNode] = None
        self._active: bool = True
        self._advance_expression_base: Optional[Node2D] = None
        self._state_machine_playback: Optional[AnimationNodeStateMachinePlayback] = None
        self._parameters: Dict[str, Any] = {}
    
    def set_animation_player(self, player: Optional[AnimationPlayer]) -> None:
        self._animation_player = player
    
    def get_animation_player(self) -> Optional[AnimationPlayer]:
        return self._animation_player
    
    def set_tree_root(self, root: Optional[AnimationNode]) -> None:
        self._tree_root = root
        if isinstance(root, AnimationNodeStateMachine):
            self._state_machine_playback = AnimationNodeStateMachinePlayback(root)
    
    def get_tree_root(self) -> Optional[AnimationNode]:
        return self._tree_root
    
    def set_active(self, active: bool) -> None:
        self._active = active
    
    def is_active(self) -> bool:
        return self._active
    
    def get(self, name: str) -> Any:
        return self._parameters.get(name)
    
    def set(self, name: str, value: Any) -> None:
        self._parameters[name] = value
    
    def set_parameter(self, name: str, value: Any) -> None:
        self._parameters[name] = value
    
    def get_parameter(self, name: str) -> Any:
        return self._parameters.get(name)
    
    def has_parameter(self, name: str) -> bool:
        return name in self._parameters
    
    def get_parameter_list(self) -> list:
        return list(self._parameters.keys())
    
    def advance(self, delta: float) -> None:
        if not self._active or not self._tree_root:
            return
        if self._state_machine_playback and self._state_machine_playback.is_playing():
            pass
    
    def set_advance_expression_base_node(self, node: Optional[Node2D]) -> None:
        self._advance_expression_base = node
    
    def get_advance_expression_base_node(self) -> Optional[Node2D]:
        return self._advance_expression_base
    
    def __repr__(self) -> str:
        return f"AnimationTree('{self.name}', active={self._active}, player={self._animation_player is not None})"
