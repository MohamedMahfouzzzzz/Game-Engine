# /**************************************************************************/
# /*  animation_player.py                                                   */
# /**************************************************************************/

"""AnimationPlayer - Node for playing animations."""

from enum import IntEnum
from typing import Optional, Callable, Dict, List
from engine.godot_animation.animation import Animation
from engine.core.nodes2d import Node2D


class AnimationPlayerPlaybackProcessCallback(IntEnum):
    PHYSICS = 0
    IDLE = 1
    MANUAL = 2


class AnimationPlayer(Node2D):
    """Node that controls animation playback."""
    
    def __init__(self, name: str = "AnimationPlayer"):
        super().__init__(name)
        self._animations: Dict[str, Animation] = {}
        self._current_animation: str = ""
        self._current_time: float = 0.0
        self._playing: bool = False
        self._active: bool = True
        self._speed_scale: float = 1.0
        self._playback_process_mode = AnimationPlayerPlaybackProcessCallback.IDLE
        self._animation_finished_callbacks: List[Callable] = []
        self._animation_started_callbacks: List[Callable] = []
        self._animation_looping_callbacks: List[Callable] = []
        self._queued: Optional[str] = None
        self._autoplay: str = ""
    
    def add_animation(self, name: str, animation: Animation) -> bool:
        if name in self._animations:
            return False
        self._animations[name] = animation
        return True
    
    def remove_animation(self, name: str) -> bool:
        if name in self._animations:
            if self._current_animation == name:
                self.stop()
            del self._animations[name]
            return True
        return False
    
    def has_animation(self, name: str) -> bool:
        return name in self._animations
    
    def get_animation(self, name: str) -> Optional[Animation]:
        return self._animations.get(name)
    
    def get_animation_list(self) -> List[str]:
        return list(self._animations.keys())
    
    def play(self, name: str = "", custom_blend: float = -1, custom_speed: float = 1.0, from_end: bool = False) -> None:
        if not name:
            name = self._current_animation
        if name not in self._animations:
            return
        self._current_animation = name
        self._current_time = self._animations[name].get_length() if from_end else 0.0
        self._playing = True
        for callback in self._animation_started_callbacks:
            callback(name)
    
    def play_backwards(self, name: str = "", custom_blend: float = -1) -> None:
        self.play(name, custom_blend, -1.0, True)
    
    def pause(self) -> None:
        self._playing = False
    
    def stop(self, keep_state: bool = False) -> None:
        self._playing = False
        if not keep_state:
            self._current_time = 0.0
            self._current_animation = ""
    
    def is_playing(self) -> bool:
        return self._playing
    
    def seek(self, time: float, update: bool = False) -> None:
        if self._current_animation and self._current_animation in self._animations:
            anim = self._animations[self._current_animation]
            self._current_time = max(0.0, min(time, anim.get_length()))
    
    def get_current_animation_position(self) -> float:
        return self._current_time
    
    def queue(self, name: str) -> None:
        if name in self._animations:
            self._queued = name
    
    def clear_queue(self) -> None:
        self._queued = None
    
    def set_speed_scale(self, speed: float) -> None:
        self._speed_scale = max(0.0, speed)
    
    def get_speed_scale(self) -> float:
        return self._speed_scale
    
    def set_autoplay(self, name: str) -> None:
        self._autoplay = name
    
    def get_autoplay(self) -> str:
        return self._autoplay
    
    def connect_animation_finished(self, callback: Callable) -> None:
        self._animation_finished_callbacks.append(callback)
    
    def connect_animation_started(self, callback: Callable) -> None:
        self._animation_started_callbacks.append(callback)
    
    def process(self, delta: float) -> None:
        if not self._playing or not self._active:
            return
        if not self._current_animation or self._current_animation not in self._animations:
            return
        
        anim = self._animations[self._current_animation]
        speed = self._speed_scale * anim.get_speed_scale()
        self._current_time += delta * speed
        
        if self._current_time >= anim.get_length():
            from engine.godot_animation.types import AnimationLoopMode
            if anim.get_loop_mode() == AnimationLoopMode.LOOP_NONE:
                self._current_time = anim.get_length()
                self._playing = False
                for callback in self._animation_finished_callbacks:
                    callback(self._current_animation)
                if self._queued:
                    self.play(self._queued)
                    self._queued = None
            elif anim.get_loop_mode() == AnimationLoopMode.LOOP_LINEAR:
                self._current_time = self._current_time % anim.get_length()
                for callback in self._animation_looping_callbacks:
                    callback(self._current_animation)
    
    def __repr__(self) -> str:
        return f"AnimationPlayer('{self.name}', current='{self._current_animation}', playing={self._playing})"
