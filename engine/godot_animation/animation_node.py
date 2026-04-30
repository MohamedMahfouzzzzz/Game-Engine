# /**************************************************************************/
# /*  animation_node.py                                                     */
# /**************************************************************************/

"""Animation tree nodes for blend trees and state machines."""

from typing import Dict, List, Optional, Any
from enum import IntEnum
from engine.core.nodes2d import Node2D, Vector2 as Point2


class AnimationNodeSync(IntEnum):
    SYNC_DEFAULT = 0
    SYNC_OFF = 1
    SYNC_ENABLED = 2


class AnimationNode:
    """Base class for animation tree nodes."""
    
    def __init__(self):
        self._filters: Dict[str, bool] = {}
        self._filter_enabled: bool = False
        self._sync: AnimationNodeSync = AnimationNodeSync.SYNC_DEFAULT
    
    def get_output(self) -> Any:
        return None
    
    def set_filter_path(self, path: str, enable: bool) -> None:
        self._filters[path] = enable
        self._filter_enabled = any(self._filters.values())
    
    def is_path_filtered(self, path: str) -> bool:
        return self._filters.get(path, False)


class AnimationNodeBlend2(AnimationNode):
    """Blend between two animations based on blend amount."""
    
    def __init__(self):
        super().__init__()
        self._blend_amount: float = 0.0
        self._node_a: Optional[AnimationNode] = None
        self._node_b: Optional[AnimationNode] = None
    
    def set_blend_amount(self, amount: float) -> None:
        self._blend_amount = max(0.0, min(1.0, amount))
    
    def get_blend_amount(self) -> float:
        return self._blend_amount


class AnimationNodeBlend3(AnimationNode):
    """Blend between three animations using a 2D blend position."""
    
    def __init__(self):
        super().__init__()
        self._blend_position: Point2 = Point2()
        self._nodes: List[Optional[AnimationNode]] = [None, None, None]
    
    def set_blend_position(self, position: Point2) -> None:
        self._blend_position = position
    
    def get_blend_position(self) -> Point2:
        return self._blend_position


class AnimationNodeOneShot(AnimationNode):
    """Play one animation, then return to previous."""
    
    def __init__(self):
        super().__init__()
        self._fadein_time: float = 0.0
        self._fadeout_time: float = 0.0
        self._autorestart: bool = False
        self._playing: bool = False
    
    def start(self) -> None:
        self._playing = True
    
    def stop(self) -> None:
        self._playing = False
    
    def is_playing(self) -> bool:
        return self._playing
    
    def set_fadein_time(self, time: float) -> None:
        self._fadein_time = max(0.0, time)
    
    def get_fadein_time(self) -> float:
        return self._fadein_time
    
    def set_fadeout_time(self, time: float) -> None:
        self._fadeout_time = max(0.0, time)
    
    def get_fadeout_time(self) -> float:
        return self._fadeout_time


class AnimationNodeTransition(AnimationNode):
    """Switch between multiple inputs with crossfade."""
    
    def __init__(self, input_count: int = 2):
        super().__init__()
        self._inputs: List[Optional[AnimationNode]] = [None] * input_count
        self._current: int = 0
        self._xfade_time: float = 0.0
    
    def set_input(self, index: int, node: Optional[AnimationNode]) -> None:
        if 0 <= index < len(self._inputs):
            self._inputs[index] = node
    
    def set_current(self, current: int) -> None:
        if 0 <= current < len(self._inputs):
            self._current = current
    
    def get_current(self) -> int:
        return self._current
    
    def set_xfade_time(self, time: float) -> None:
        self._xfade_time = max(0.0, time)
    
    def get_xfade_time(self) -> float:
        return self._xfade_time


class AnimationNodeStateMachineTransition:
    """Transition between state machine states."""
    
    def __init__(self):
        self._xfade_time: float = 0.0
        self._advance_condition: str = ""
        self._reset: bool = True
    
    def set_xfade_time(self, time: float) -> None:
        self._xfade_time = max(0.0, time)
    
    def get_xfade_time(self) -> float:
        return self._xfade_time
    
    def set_advance_condition(self, condition: str) -> None:
        self._advance_condition = condition
    
    def get_advance_condition(self) -> str:
        return self._advance_condition
    
    def set_reset(self, reset: bool) -> None:
        self._reset = reset
    
    def is_reset(self) -> bool:
        return self._reset


class AnimationNodeStateMachine(AnimationNode):
    """State machine for animation blending."""
    
    def __init__(self):
        super().__init__()
        self._states: Dict[str, AnimationNode] = {}
        self._transitions: Dict[tuple, AnimationNodeStateMachineTransition] = {}
        self._start_state: str = ""
        self._current_state: str = ""
        self._playback: Optional['AnimationNodeStateMachinePlayback'] = None
    
    def add_state(self, name: str, node: AnimationNode) -> None:
        self._states[name] = node
    
    def remove_state(self, name: str) -> None:
        if name in self._states:
            del self._states[name]
    
    def has_state(self, name: str) -> bool:
        return name in self._states
    
    def add_transition(self, from_state: str, to_state: str, transition: AnimationNodeStateMachineTransition) -> None:
        self._transitions[(from_state, to_state)] = transition
    
    def set_start_state(self, name: str) -> None:
        if name in self._states:
            self._start_state = name
    
    def get_start_state(self) -> str:
        return self._start_state
    
    def get_current_state(self) -> str:
        return self._current_state
    
    def travel(self, to_state: str, reset_on_teleport: bool = True) -> None:
        if to_state in self._states:
            self._current_state = to_state


class AnimationNodeStateMachinePlayback:
    """Playback control for state machine."""
    
    def __init__(self, state_machine: AnimationNodeStateMachine):
        self._state_machine = state_machine
        self._is_playing: bool = False
    
    def travel(self, to_state: str, reset_on_teleport: bool = True) -> None:
        self._state_machine.travel(to_state, reset_on_teleport)
    
    def start(self, state: str = "") -> None:
        self._is_playing = True
        if state:
            self._state_machine.travel(state)
        elif self._state_machine.get_start_state():
            self._state_machine.travel(self._state_machine.get_start_state())
    
    def stop(self) -> None:
        self._is_playing = False
    
    def is_playing(self) -> bool:
        return self._is_playing
    
    def get_current_state(self) -> str:
        return self._state_machine.get_current_state()
