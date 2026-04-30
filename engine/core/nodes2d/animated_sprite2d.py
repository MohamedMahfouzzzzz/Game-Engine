# /**************************************************************************/
# /*  animated_sprite2d.py                                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""AnimatedSprite2D - Sprite animation node with frame-based playback."""

from __future__ import annotations

from typing import Optional, Dict, List
from dataclasses import dataclass, field

from .node2d import Node2D
from .types import Vector2, Texture2D
from engine.core.types import NodeType

@dataclass
class AnimationFrame:
    """Single frame of animation."""
    texture: Optional[Texture2D] = None
    duration: float = 1.0  # Duration in seconds


@dataclass
class SpriteAnimation:
    """Animation data with frames."""
    name: str = ""
    frames: List[AnimationFrame] = field(default_factory=list)
    loop: bool = True
    speed_scale: float = 1.0


class SpriteFrames:
    """Resource containing multiple animations."""
    
    def __init__(self):
        self._animations: Dict[str, SpriteAnimation] = {}
    
    def add_animation(self, name: str, frames: List[AnimationFrame], loop: bool = True) -> None:
        """Add animation with frames."""
        self._animations[name] = SpriteAnimation(
            name=name,
            frames=frames,
            loop=loop
        )
    
    def get_animation(self, name: str) -> Optional[SpriteAnimation]:
        """Get animation by name."""
        return self._animations.get(name)
    
    def has_animation(self, name: str) -> bool:
        """Check if animation exists."""
        return name in self._animations
    
    def get_animation_names(self) -> List[str]:
        """Get all animation names."""
        return list(self._animations.keys())


class AnimatedSprite2D(Node2D):
    """Sprite node with animation support.
    
    Properties:
        sprite_frames: SpriteFrames resource with animations
        animation: Current animation name (String)
        autoplay: Animation to play on ready (String)
        frame: Current frame index (int)
        frame_progress: Progress through current frame 0.0-1.0 (float)
        speed_scale: Playback speed multiplier (float)
        centered: Center sprite on position (bool)
        offset: Drawing offset from position (Vector2)
        flip_h: Horizontal flip (bool)
        flip_v: Vertical flip (bool)
    
    Signals:
        animation_finished: When animation completes (if not looping)
        animation_changed: When animation changes
        animation_looped: When animation loops
        frame_changed: When frame index changes
    """
    
    __slots__ = [
        "sprite_frames",
        "_animation",
        "autoplay",
        "_frame",
        "frame_progress",
        "speed_scale",
        "centered",
        "offset",
        "flip_h",
        "flip_v",
        "_playing",
        "_accumulated_time"
    ]
    
    _SIGNALS = [
        "animation_finished",
        "animation_changed",
        "animation_looped",
        "frame_changed"
    ]
    
    def __init__(self, name: str = "AnimatedSprite2D"):
        super().__init__(name)
        self.node_type = NodeType.ANIMATED_SPRITE
        
        # Animation resource
        self.sprite_frames: Optional[SpriteFrames] = None
        
        # Animation properties
        self._animation: str = ""
        self.autoplay: str = ""
        self._frame: int = 0
        self.frame_progress: float = 0.0
        self.speed_scale: float = 1.0
        
        # Visual properties
        self.centered: bool = True
        self.offset: Vector2 = Vector2(0, 0)
        self.flip_h: bool = False
        self.flip_v: bool = False
        
        # Playback state
        self._playing: bool = False
        self._accumulated_time: float = 0.0
    
    @property
    def animation(self) -> str:
        """Current animation name."""
        return self._animation
    
    @animation.setter
    def animation(self, value: str) -> None:
        if value != self._animation:
            old_animation = self._animation
            self._animation = value
            self._frame = 0
            self.frame_progress = 0.0
            self._accumulated_time = 0.0
            self.signals.emit("animation_changed", old_animation, value)
    
    @property
    def frame(self) -> int:
        """Current frame index."""
        return self._frame
    
    @frame.setter
    def frame(self, value: int) -> None:
        if value != self._frame:
            self._frame = value
            self.frame_progress = 0.0
            self.signals.emit("frame_changed", value)
    
    def play(self, animation: str = "", custom_speed: float = 1.0, from_end: bool = False) -> None:
        """Play animation."""
        if animation:
            self.animation = animation
        
        self._playing = True
        self.speed_scale = custom_speed
        
        if from_end and self.sprite_frames:
            anim = self.sprite_frames.get_animation(self._animation)
            if anim:
                self._frame = len(anim.frames) - 1
    
    def pause(self) -> None:
        """Pause playback."""
        self._playing = False
    
    def stop(self) -> None:
        """Stop playback and reset."""
        self._playing = False
        self._frame = 0
        self.frame_progress = 0.0
    
    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self._playing
    
    def _process(self, delta: float) -> None:
        """Update animation."""
        if not self._playing or not self.sprite_frames:
            return
        
        anim = self.sprite_frames.get_animation(self._animation)
        if not anim or not anim.frames:
            return
        
        # Advance time
        self._accumulated_time += delta * self.speed_scale * anim.speed_scale
        
        # Get current frame duration
        current_frame = anim.frames[self._frame]
        frame_duration = current_frame.duration
        
        # Update progress
        self.frame_progress = min(1.0, self._accumulated_time / frame_duration)
        
        # Advance frame if needed
        while self._accumulated_time >= frame_duration:
            self._accumulated_time -= frame_duration
            self._frame += 1
            
            # Check for loop or finish
            if self._frame >= len(anim.frames):
                if anim.loop:
                    self._frame = 0
                    self.signals.emit("animation_looped")
                else:
                    self._frame = len(anim.frames) - 1
                    self._playing = False
                    self.signals.emit("animation_finished")
                    break
            
            self.signals.emit("frame_changed", self._frame)
            
            # Update for next frame
            if self._frame < len(anim.frames):
                current_frame = anim.frames[self._frame]
                frame_duration = current_frame.duration
    
    def _draw(self, renderer) -> None:
        """Draw current frame."""
        if not self.sprite_frames or not self._animation:
            return
        
        anim = self.sprite_frames.get_animation(self._animation)
        if not anim or self._frame >= len(anim.frames):
            return
        
        frame = anim.frames[self._frame]
        if not frame.texture:
            return
        
        # Calculate draw position
        pos = self.position + self.offset
        
        if self.centered:
            pos = pos - Vector2(frame.texture.width / 2, frame.texture.height / 2)
        
        # Draw via renderer
        # renderer.draw_texture(frame.texture, pos, flip_h=self.flip_h, flip_v=self.flip_v)


__all__ = ["AnimatedSprite2D", "SpriteFrames", "SpriteAnimation", "AnimationFrame"]
