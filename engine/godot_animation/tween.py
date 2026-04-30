    # /**************************************************************************/
# /*  tween.py                                                              */
# /**************************************************************************/

"""Tween - Programmatic interpolation/animation."""

from enum import IntEnum
from typing import Any, Callable, Optional, List
from dataclasses import dataclass


class TweenTransitionType(IntEnum):
    TRANS_LINEAR = 0
    TRANS_SINE = 1
    TRANS_QUINT = 2
    TRANS_QUART = 3
    TRANS_QUAD = 4
    TRANS_EXPO = 5
    TRANS_ELASTIC = 6
    TRANS_CUBIC = 7
    TRANS_BACK = 8
    TRANS_BOUNCE = 9
    TRANS_SPRING = 10


class TweenEaseType(IntEnum):
    EASE_IN = 0
    EASE_OUT = 1
    EASE_IN_OUT = 2
    EASE_OUT_IN = 3


@dataclass
class TweenStep:
    target: Any = None
    property: str = ""
    initial_val: Any = None
    final_val: Any = None
    duration: float = 0.0
    trans_type: TweenTransitionType = TweenTransitionType.TRANS_LINEAR
    ease_type: TweenEaseType = TweenEaseType.EASE_IN_OUT
    delay: float = 0.0
    elapsed: float = 0.0
    finished: bool = False
    setter: Optional[Callable] = None


class Tween:
    """Programmatic interpolation between values."""
    
    def __init__(self):
        self._default_transition = TweenTransitionType.TRANS_LINEAR
        self._default_ease = TweenEaseType.EASE_IN_OUT
        self._default_parallel = False
        self._steps: List[TweenStep] = []
        self._current_step = 0
        self._playing = False
        self._loops = 0
        self._loop_count = 0
        self._speed_scale = 1.0
        self._paused = False
        self._step_finished_callbacks: List[Callable] = []
        self._loop_finished_callbacks: List[Callable] = []
        self._finished_callbacks: List[Callable] = []
    
    def tween_property(self, target: Any, property_name: str, final_val: Any, duration: float) -> 'Tween':
        step = TweenStep(
            target=target, property=property_name, final_val=final_val,
            duration=max(0.0, duration),
            trans_type=self._default_transition, ease_type=self._default_ease
        )
        self._steps.append(step)
        return self
    
    def tween_interval(self, duration: float) -> 'Tween':
        self._steps.append(TweenStep(duration=max(0.0, duration)))
        return self
    
    def tween_callback(self, callback: Callable, args: tuple = ()) -> 'Tween':
        step = TweenStep(setter=lambda _: callback(*args), duration=0.0)
        self._steps.append(step)
        return self
    
    def tween_method(self, method: Callable, from_val: Any, to_val: Any, duration: float) -> 'Tween':
        step = TweenStep(
            setter=method, initial_val=from_val, final_val=to_val,
            duration=max(0.0, duration),
            trans_type=self._default_transition, ease_type=self._default_ease
        )
        self._steps.append(step)
        return self
    
    def set_trans(self, trans: TweenTransitionType) -> 'Tween':
        self._default_transition = trans
        return self
    
    def set_ease(self, ease: TweenEaseType) -> 'Tween':
        self._default_ease = ease
        return self
    
    def set_parallel(self, parallel: bool) -> 'Tween':
        self._default_parallel = parallel
        return self
    
    def parallel(self) -> 'Tween':
        self._default_parallel = True
        return self
    
    def chain(self) -> 'Tween':
        self._default_parallel = False
        return self
    
    def play(self) -> 'Tween':
        self._playing = True
        self._paused = False
        return self
    
    def stop(self) -> 'Tween':
        self._playing = False
        self._paused = False
        self._current_step = 0
        for step in self._steps:
            step.elapsed = 0.0
            step.finished = False
        return self
    
    def pause(self) -> 'Tween':
        self._paused = True
        return self
    
    def is_playing(self) -> bool:
        return self._playing and not self._paused
    
    def is_running(self) -> bool:
        return self._playing
    
    def set_loops(self, loops: int = 0) -> 'Tween':
        self._loops = max(0, loops)
        return self
    
    def set_speed_scale(self, speed: float) -> 'Tween':
        self._speed_scale = max(0.0, speed)
        return self
    
    def process(self, delta: float) -> None:
        if not self._playing or self._paused:
            return
        
        delta *= self._speed_scale
        
        for step in self._steps:
            if step.finished:
                continue
            
            if step.elapsed < step.delay:
                step.elapsed += delta
                continue
            
            effective_elapsed = step.elapsed - step.delay
            t = min(1.0, effective_elapsed / step.duration) if step.duration > 0 else 1.0
            t = self._apply_ease(t, step.trans_type, step.ease_type)
            
            if step.setter:
                if step.initial_val is not None and step.final_val is not None:
                    val = self._interpolate(step.initial_val, step.final_val, t)
                    step.setter(val)
                else:
                    step.setter(None)
            elif step.target and step.property:
                setattr(step.target, step.property, step.final_val)
            
            step.elapsed += delta
            
            if effective_elapsed >= step.duration:
                step.finished = True
                for callback in self._step_finished_callbacks:
                    callback(step)
        
        if all(step.finished for step in self._steps):
            self._loop_count += 1
            if self._loops == 0 or self._loop_count < self._loops:
                for step in self._steps:
                    step.elapsed = 0.0
                    step.finished = False
                for callback in self._loop_finished_callbacks:
                    callback(self._loop_count)
            else:
                self._playing = False
                for callback in self._finished_callbacks:
                    callback()
    
    def _interpolate(self, a: Any, b: Any, t: float) -> Any:
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + (b - a) * t
        return b if t >= 0.5 else a
    
    def _apply_ease(self, t: float, trans: TweenTransitionType, ease: TweenEaseType) -> float:
        import math
        
        if ease == TweenEaseType.EASE_OUT:
            t = 1.0 - t
        elif ease == TweenEaseType.EASE_IN_OUT:
            t = t * 2.0 if t < 0.5 else 2.0 - t * 2.0
            t = min(1.0, t)
        elif ease == TweenEaseType.EASE_OUT_IN:
            t = t * 2.0 - 1.0 if t > 0.5 else 1.0 - t * 2.0
        
        if trans == TweenTransitionType.TRANS_LINEAR:
            return t
        elif trans == TweenTransitionType.TRANS_QUAD:
            return t * t
        elif trans == TweenTransitionType.TRANS_CUBIC:
            return t * t * t
        elif trans == TweenTransitionType.TRANS_SINE:
            return 1.0 - math.cos(t * math.pi / 2)
        elif trans == TweenTransitionType.TRANS_EXPO:
            return math.pow(2, 10 * (t - 1))
        elif trans == TweenTransitionType.TRANS_BACK:
            return t * t * (2.70158 * t - 1.70158)
        elif trans == TweenTransitionType.TRANS_BOUNCE:
            if t < 1 / 2.75:
                return 7.5625 * t * t
            elif t < 2 / 2.75:
                t -= 1.5 / 2.75
                return 7.5625 * t * t + 0.75
            else:
                t -= 2.625 / 2.75
                return 7.5625 * t * t + 0.984375
        elif trans == TweenTransitionType.TRANS_ELASTIC:
            if t == 0:
                return 0
            return math.pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1
        return t
    
    def connect_step_finished(self, callback: Callable) -> None:
        self._step_finished_callbacks.append(callback)
    
    def connect_loop_finished(self, callback: Callable) -> None:
        self._loop_finished_callbacks.append(callback)
    
    def connect_finished(self, callback: Callable) -> None:
        self._finished_callbacks.append(callback)
    
    def kill(self) -> None:
        self._playing = False
        self._steps.clear()
    
    def is_valid(self) -> bool:
        return len(self._steps) > 0
    
    def __repr__(self) -> str:
        return f"Tween(steps={len(self._steps)}, playing={self._playing})"
