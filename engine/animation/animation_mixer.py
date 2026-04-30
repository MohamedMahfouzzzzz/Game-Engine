# /**************************************************************************/
# /*  animation_mixer.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""AnimationMixer - Mix multiple animations with weights."""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from engine.animation.animation import Animation, AnimationLoopMode


@dataclass
class BlendEntry:
    animation: Animation = None
    weight: float = 1.0
    time: float = 0.0
    speed: float = 1.0
    playing: bool = False


class AnimationMixer:
    """Mix multiple animations with individual weights."""
    
    def __init__(self):
        self._animations: Dict[str, BlendEntry] = {}
        self._callbacks: List[Callable] = []
    
    def add_animation(self, name: str, animation: Animation) -> None:
        self._animations[name] = BlendEntry(animation=animation)
    
    def remove_animation(self, name: str) -> bool:
        if name in self._animations:
            del self._animations[name]
            return True
        return False
    
    def has_animation(self, name: str) -> bool:
        return name in self._animations
    
    def play(self, name: str) -> None:
        if name in self._animations:
            self._animations[name].playing = True
    
    def stop(self, name: str) -> None:
        if name in self._animations:
            self._animations[name].playing = False
            self._animations[name].time = 0.0
    
    def pause(self, name: str) -> None:
        if name in self._animations:
            self._animations[name].playing = False
    
    def is_playing(self, name: str) -> bool:
        if name in self._animations:
            return self._animations[name].playing
        return False
    
    def stop_all(self) -> None:
        for entry in self._animations.values():
            entry.playing = False
            entry.time = 0.0
    
    def set_weight(self, name: str, weight: float) -> None:
        if name in self._animations:
            self._animations[name].weight = max(0.0, min(1.0, weight))
    
    def get_weight(self, name: str) -> float:
        if name in self._animations:
            return self._animations[name].weight
        return 0.0
    
    def seek(self, name: str, time: float) -> None:
        if name in self._animations:
            anim = self._animations[name].animation
            self._animations[name].time = max(0.0, min(time, anim.get_length()))
    
    def get_play_position(self, name: str) -> float:
        if name in self._animations:
            return self._animations[name].time
        return 0.0
    
    def set_speed(self, name: str, speed: float) -> None:
        if name in self._animations:
            self._animations[name].speed = speed
    
    def get_speed(self, name: str) -> float:
        if name in self._animations:
            return self._animations[name].speed
        return 1.0
    
    def process(self, delta: float) -> None:
        for name, entry in self._animations.items():
            if not entry.playing:
                continue
            entry.time += delta * entry.speed * entry.animation.get_speed_scale()
            if entry.time >= entry.animation.get_length():
                if entry.animation.get_loop_mode() == AnimationLoopMode.LOOP_NONE:
                    entry.playing = False
                    entry.time = entry.animation.get_length()
                elif entry.animation.get_loop_mode() == AnimationLoopMode.LOOP_LINEAR:
                    entry.time = entry.time % entry.animation.get_length()
    
    def get_active_count(self) -> int:
        return sum(1 for entry in self._animations.values() if entry.playing)
    
    def __repr__(self) -> str:
        playing = sum(1 for e in self._animations.values() if e.playing)
        return f"AnimationMixer(anims={len(self._animations)}, playing={playing})"
