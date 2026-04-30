# /**************************************************************************/
# /*  animated_sprite.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D animated sprite with frame-based animation."""

from typing import Dict, List, Optional
from engine.core.nodes2d import Node2D, Vector2
from engine.scene2d.sprite import Texture2D


class SpriteFrames:
    """Resource containing multiple sprite animations."""
    
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
    """Animated sprite node for frame-based animation.
    
    Plays animations from a SpriteFrames resource.
    """
    
    def __init__(self, name: str = "AnimatedSprite2D"):
        super().__init__(name)
        self._sprite_frames: Optional[SpriteFrames] = None
        self._animation: str = "default"
        self._frame: int = 0
        self._playing: bool = False
        self._speed_scale: float = 1.0
        self._centered: bool = True
        self._offset: Vector2 = Vector2()
        self._flip_h: bool = False
        self._flip_v: bool = False
        self._accumulated_time: float = 0.0
    
    def set_sprite_frames(self, frames: Optional[SpriteFrames]) -> None:
        self._sprite_frames = frames
    
    def get_sprite_frames(self) -> Optional[SpriteFrames]:
        return self._sprite_frames
    
    def play(self, anim: str = "default") -> None:
        self._animation = anim
        self._playing = True
        self._frame = 0
        self._accumulated_time = 0.0
    
    def pause(self) -> None:
        self._playing = False
    
    def stop(self) -> None:
        self._playing = False
        self._frame = 0
    
    def is_playing(self) -> bool:
        return self._playing
    
    def set_animation(self, anim: str) -> None:
        if self._sprite_frames and self._sprite_frames.has_animation(anim):
            self._animation = anim
    
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
    
    def is_centered(self) -> bool:
        return self._centered
    
    def set_offset(self, offset: Vector2) -> None:
        self._offset = offset
    
    def get_offset(self) -> Vector2:
        return self._offset
    
    def set_flip_h(self, flip: bool) -> None:
        self._flip_h = flip
    
    def is_flipped_h(self) -> bool:
        return self._flip_h
    
    def set_flip_v(self, flip: bool) -> None:
        self._flip_v = flip
    
    def is_flipped_v(self) -> bool:
        return self._flip_v
    
    def _update(self, delta: float) -> None:
        if not self._playing or not self._sprite_frames:
            return
        
        fps = self._sprite_frames.get_animation_speed(self._animation)
        self._accumulated_time += delta * self._speed_scale
        
        frame_duration = 1.0 / fps if fps > 0 else 0.2
        frame_count = self._sprite_frames.get_frame_count(self._animation)
        
        if frame_count == 0:
            return
        
        # Advance frames
        frames_advanced = int(self._accumulated_time / frame_duration)
        if frames_advanced > 0:
            self._accumulated_time -= frames_advanced * frame_duration
            self._frame += frames_advanced
            
            if self._frame >= frame_count:
                if self._sprite_frames.get_animation_loop(self._animation):
                    self._frame %= frame_count
                else:
                    self._frame = frame_count - 1
                    self._playing = False
    
    def __repr__(self) -> str:
        return f"AnimatedSprite2D('{self.name}', anim='{self._animation}', frame={self._frame})"
