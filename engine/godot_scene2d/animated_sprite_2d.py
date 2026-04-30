# /**************************************************************************/
# /*  animated_sprite_2d.py                                                 */
# /**************************************************************************/

"""Godot AnimatedSprite2D port - Frame-based animation."""

from typing import Dict, List, Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.sprite_2d import Texture2D
from engine.godot_scene2d.types import Point2


class SpriteFrames:
    """Collection of animation frames."""
    
    def __init__(self):
        self._animations: Dict[str, Dict] = {}
    
    def add_animation(self, anim: str) -> None:
        if anim not in self._animations:
            self._animations[anim] = {"frames": [], "fps": 5.0, "loop": True}
    
    def has_animation(self, anim: str) -> bool:
        return anim in self._animations
    
    def remove_animation(self, anim: str) -> None:
        if anim in self._animations:
            del self._animations[anim]
    
    def get_animation_names(self) -> List[str]:
        return list(self._animations.keys())
    
    def set_animation_speed(self, anim: str, speed: float) -> None:
        if anim in self._animations:
            self._animations[anim]["fps"] = speed
    
    def get_animation_speed(self, anim: str) -> float:
        if anim in self._animations:
            return self._animations[anim]["fps"]
        return 5.0
    
    def set_animation_loop(self, anim: str, loop: bool) -> None:
        if anim in self._animations:
            self._animations[anim]["loop"] = loop
    
    def get_animation_loop(self, anim: str) -> bool:
        if anim in self._animations:
            return self._animations[anim]["loop"]
        return True
    
    def add_frame(self, anim: str, texture: Texture2D, duration: int = 1) -> None:
        if anim in self._animations:
            self._animations[anim]["frames"].append({"texture": texture, "duration": duration})
    
    def get_frame_count(self, anim: str) -> int:
        if anim in self._animations:
            return len(self._animations[anim]["frames"])
        return 0
    
    def get_frame_texture(self, anim: str, frame: int) -> Optional[Texture2D]:
        if anim in self._animations:
            frames = self._animations[anim]["frames"]
            if 0 <= frame < len(frames):
                return frames[frame]["texture"]
        return None


class AnimatedSprite2D(Node2D):
    """Animated sprite with multiple animations."""
    
    def __init__(self, name: str = "AnimatedSprite2D"):
        super().__init__(name)
        self._sprite_frames: Optional[SpriteFrames] = None
        self._animation: str = "default"
        self._frame: int = 0
        self._playing: bool = False
        self._speed_scale: float = 1.0
        self._centered: bool = True
        self._offset: Point2 = Point2()
        self._flip_h: bool = False
        self._flip_v: bool = False
        self._time: float = 0.0
    
    def set_sprite_frames(self, frames: Optional[SpriteFrames]) -> None:
        self._sprite_frames = frames
    
    def get_sprite_frames(self) -> Optional[SpriteFrames]:
        return self._sprite_frames
    
    def play(self, anim: str = "", backwards: bool = False) -> None:
        if anim:
            self._animation = anim
        self._playing = True
        if backwards:
            self._speed_scale = -abs(self._speed_scale)
    
    def pause(self) -> None:
        self._playing = False
    
    def stop(self) -> None:
        self._playing = False
        self._frame = 0
        self._time = 0.0
    
    def is_playing(self) -> bool:
        return self._playing
    
    def set_animation(self, anim: str) -> None:
        if self._sprite_frames and self._sprite_frames.has_animation(anim):
            self._animation = anim
            self._frame = 0
            self._time = 0.0
    
    def get_animation(self) -> str:
        return self._animation
    
    def set_frame(self, frame: int) -> None:
        self._frame = max(0, frame)
    
    def get_frame(self) -> int:
        return self._frame
    
    def set_speed_scale(self, scale: float) -> None:
        self._speed_scale = scale
    
    def get_speed_scale(self) -> float:
        return self._speed_scale
    
    def set_centered(self, centered: bool) -> None:
        self._centered = centered
    
    def set_flip_h(self, flip: bool) -> None:
        self._flip_h = flip
    
    def set_flip_v(self, flip: bool) -> None:
        self._flip_v = flip
    
    def process(self, delta: float) -> None:
        if not self._playing or not self._sprite_frames:
            return
        
        fps = self._sprite_frames.get_animation_speed(self._animation)
        self._time += delta * abs(self._speed_scale)
        
        frame_duration = 1.0 / fps if fps > 0 else 0.2
        frame_count = self._sprite_frames.get_frame_count(self._animation)
        
        if frame_count > 0:
            self._frame = int(self._time / frame_duration) % frame_count
    
    def __repr__(self) -> str:
        return f"AnimatedSprite2D('{self.name}', anim='{self._animation}', frame={self._frame}, playing={self._playing})"
