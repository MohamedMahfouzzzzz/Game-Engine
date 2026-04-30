# /**************************************************************************/
# /*  animation_tree.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Animation tree for advanced animation blending with state machines."""

from enum import IntEnum
from typing import Optional, Dict, List, Callable, Any
from engine.core.nodes2d import Node2D


class AnimationNode:
    """Base class for animation tree nodes."""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.blend = 0.0
    
    def get_child_by_name(self, name: str) -> Optional['AnimationNode']:
        return None
    
    def get_parameter_list(self) -> List[str]:
        return []


class AnimationNodeStateMachine(AnimationNode):
    """State machine for animation switching."""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self._states: Dict[str, AnimationNode] = {}
        self._transitions: List[tuple] = []  # (from_state, to_state, condition)
        self._start_state: str = ""
        self._end_state: Optional[str] = None
        self._playback = None
    
    def add_state(self, name: str, node: AnimationNode) -> None:
        self._states[name] = node
    
    def remove_state(self, name: str) -> bool:
        if name in self._states:
            del self._states[name]
            # Remove related transitions
            self._transitions = [t for t in self._transitions if t[0] != name and t[1] != name]
            return True
        return False
    
    def has_state(self, name: str) -> bool:
        return name in self._states
    
    def get_state(self, name: str) -> Optional[AnimationNode]:
        return self._states.get(name)
    
    def add_transition(self, from_state: str, to_state: str, condition: str = "") -> None:
        self._transitions.append((from_state, to_state, condition))
    
    def set_start_state(self, name: str) -> None:
        self._start_state = name
    
    def get_start_state(self) -> str:
        return self._start_state
    
    def set_end_state(self, name: Optional[str]) -> None:
        self._end_state = name
    
    def get_end_state(self) -> Optional[str]:
        return self._end_state


class AnimationNodeStateMachinePlayback:
    """Playback controller for state machine."""
    
    def __init__(self, state_machine: AnimationNodeStateMachine):
        self._state_machine = state_machine
        self._current_state: str = ""
        self._previous_state: str = ""
        self._is_playing: bool = False
        self._travel_path: List[str] = []
    
    def start(self, state: str) -> None:
        """Start playback from a state."""
        if self._state_machine.has_state(state):
            self._current_state = state
            self._is_playing = True
    
    def travel(self, to_state: str) -> None:
        """Travel to a state via shortest path."""
        if self._state_machine.has_state(to_state):
            self._travel_path.append(to_state)
    
    def next(self) -> bool:
        """Advance to next state in travel path."""
        if self._travel_path:
            self._previous_state = self._current_state
            self._current_state = self._travel_path.pop(0)
            return True
        return False
    
    def stop(self) -> None:
        """Stop playback."""
        self._is_playing = False
    
    def is_playing(self) -> bool:
        return self._is_playing
    
    def get_current_play_position(self) -> float:
        return 0.0
    
    def get_current_length(self) -> float:
        return 0.0
    
    def get_current_node(self) -> str:
        return self._current_state
    
    def get_travel_path(self) -> List[str]:
        return list(self._travel_path)


class AnimationNodeBlendTree(AnimationNode):
    """Blend tree for mixing animations."""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self._nodes: Dict[str, AnimationNode] = {}
        self._connections: List[tuple] = []  # (from, from_port, to, to_port)
    
    def add_node(self, name: str, node: AnimationNode, position: tuple = (0, 0)) -> None:
        self._nodes[name] = node
    
    def remove_node(self, name: str) -> bool:
        if name in self._nodes:
            del self._nodes[name]
            self._connections = [c for c in self._connections if c[0] != name and c[2] != name]
            return True
        return False
    
    def connect_node(self, from_node: str, from_port: int, to_node: str, to_port: int) -> bool:
        self._connections.append((from_node, from_port, to_node, to_port))
        return True


class AnimationNodeBlend2(AnimationNode):
    """Blend between two animations."""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self._blend: float = 0.0  # 0 = input 1, 1 = input 2
    
    def set_blend(self, value: float) -> None:
        self._blend = max(0.0, min(1.0, value))
    
    def get_blend(self) -> float:
        return self._blend


class AnimationNodeBlend3(AnimationNode):
    """Blend between three animations."""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self._blend: float = 0.0  # -1 = input 1, 0 = input 2, 1 = input 3
    
    def set_blend(self, value: float) -> None:
        self._blend = max(-1.0, min(1.0, value))
    
    def get_blend(self) -> float:
        return self._blend


class AnimationNodeOneShot(AnimationNode):
    """Play animation once then return to previous."""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self._active: bool = False
        self._fadein_time: float = 0.0
        self._fadeout_time: float = 0.0
        self._autorestart: bool = False
        self._autorestart_delay: float = 0.0
    
    def start(self) -> None:
        self._active = True
    
    def stop(self) -> None:
        self._active = False
    
    def is_active(self) -> bool:
        return self._active


class AnimationTree(Node2D):
    """Advanced animation blending using trees and state machines.
    
    Controls animation playback through:
    - State machines (AnimationNodeStateMachine)
    - Blend trees (AnimationNodeBlendTree)
    - Blend nodes (AnimationNodeBlend2, AnimationNodeBlend3)
    - One-shot nodes (AnimationNodeOneShot)
    """
    
    ANIMATION_PROCESS_PHYSICS = 0
    ANIMATION_PROCESS_IDLE = 1
    ANIMATION_PROCESS_MANUAL = 2
    
    def __init__(self, name: str = "AnimationTree"):
        super().__init__(name)
        self._tree_root: Optional[AnimationNode] = None
        self._animation_player: str = ""
        self._active: bool = True
        self._advance_expression_base_node: str = ""
        self._root_motion_track = None
        self._root_motion_transform = None
        self._process_callback: int = self.ANIMATION_PROCESS_IDLE
        
        # Callbacks
        self._animation_started_callbacks: List[Callable] = []
        self._animation_finished_callbacks: List[Callable] = []
    
    def set_tree_root(self, root: Optional[AnimationNode]) -> None:
        """Set the root node of the blend tree."""
        self._tree_root = root
    
    def get_tree_root(self) -> Optional[AnimationNode]:
        return self._tree_root
    
    def set_animation_player(self, path: str) -> None:
        """Set path to AnimationPlayer node."""
        self._animation_player = path
    
    def get_animation_player(self) -> str:
        return self._animation_player
    
    def set_active(self, active: bool) -> None:
        """Enable/disable tree processing."""
        self._active = active
    
    def is_active(self) -> bool:
        return self._active
    
    def set_process_callback(self, callback: int) -> None:
        """Set when tree updates (physics, idle, manual)."""
        self._process_callback = callback
    
    def get_process_callback(self) -> int:
        return self._process_callback
    
    def advance(self, delta: float) -> None:
        """Manually advance animation."""
        pass
    
    def get_root_motion_position(self) -> Any:
        """Get accumulated root motion position."""
        return None
    
    def get_root_motion_rotation(self) -> float:
        """Get accumulated root motion rotation."""
        return 0.0
    
    def connect_animation_started(self, callback: Callable) -> None:
        """Called when any animation starts."""
        self._animation_started_callbacks.append(callback)
    
    def connect_animation_finished(self, callback: Callable) -> None:
        """Called when any animation finishes."""
        self._animation_finished_callbacks.append(callback)
    
    def __repr__(self) -> str:
        return f"AnimationTree('{self.name}', active={self._active}, root={self._tree_root.__class__.__name__ if self._tree_root else None})"
