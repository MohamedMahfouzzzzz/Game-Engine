# /**************************************************************************/
# /*  animated_sprite.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Animated sprite node with frame-based animation."""

from typing import Dict, List, Optional, Tuple
from engine.core.nodes.sprite import Sprite
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Animation:
    """Animation data for AnimatedSprite."""

    def __init__(self, name: str, frames: List[int], fps: float = 12.0, loop: bool = True):
        self.name = name
        self.frames = frames  # List of frame indices in the spritesheet
        self.fps = fps
        self.loop = loop
        self.duration = len(frames) / fps if fps > 0 else 0


class AnimatedSprite(Sprite):
    """A sprite that can play frame-based animations."""

    def __init__(self, name: str = "AnimatedSprite"):
        super().__init__(name)
        self.node_type = NodeType.ANIMATED_SPRITE

        # Animation data
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[str] = None
        self.current_frame: int = 0
        self.frame_timer: float = 0.0
        self.playing: bool = False

        # Sprite sheet configuration
        self.spritesheet_columns: int = 1
        self.spritesheet_rows: int = 1
        self.frame_size: Tuple[int, int] = (32, 32)  # Size of each frame

    def add_animation(self, name: str, frames: List[int], fps: float = 12.0, loop: bool = True) -> None:
        """Add a new animation."""
        self.animations[name] = Animation(name, frames, fps, loop)

    def remove_animation(self, name: str) -> None:
        """Remove an animation."""
        if name in self.animations:
            del self.animations[name]
            if self.current_animation == name:
                self.current_animation = None
                self.playing = False

    def play(self, animation_name: str, restart: bool = False) -> None:
        """Play an animation."""
        if animation_name not in self.animations:
            return

        if self.current_animation != animation_name or restart:
            self.current_animation = animation_name
            self.current_frame = 0
            self.frame_timer = 0.0
            self.playing = True
            self._update_region()

    def stop(self) -> None:
        """Stop playback."""
        self.playing = False

    def pause(self) -> None:
        """Pause playback."""
        self.playing = False

    def resume(self) -> None:
        """Resume playback."""
        if self.current_animation:
            self.playing = True

    def update(self, delta_time: float) -> None:
        """Update animation frame."""
        if not self.playing or not self.current_animation:
            return

        anim = self.animations[self.current_animation]
        self.frame_timer += delta_time

        frame_duration = 1.0 / anim.fps if anim.fps > 0 else 0.1

        if self.frame_timer >= frame_duration:
            self.frame_timer -= frame_duration
            self.current_frame += 1

            if self.current_frame >= len(anim.frames):
                if anim.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(anim.frames) - 1
                    self.playing = False

            self._update_region()

    def _update_region(self) -> None:
        """Update texture region based on current frame."""
        if not self.current_animation:
            return

        anim = self.animations[self.current_animation]
        if self.current_frame < len(anim.frames):
            frame_idx = anim.frames[self.current_frame]
            col = frame_idx % self.spritesheet_columns
            row = frame_idx // self.spritesheet_columns

            x = col * self.frame_size[0]
            y = row * self.frame_size[1]

            self.set_region(x, y, self.frame_size[0], self.frame_size[1])

    def set_spritesheet(self, columns: int, rows: int, frame_width: int, frame_height: int) -> None:
        """Configure spritesheet layout."""
        self.spritesheet_columns = columns
        self.spritesheet_rows = rows
        self.frame_size = (frame_width, frame_height)

    def to_dict(self):
        """Serialize to dictionary."""
        data = super().to_dict()
        data.update({
            "animations": {
                name: {
                    "frames": anim.frames,
                    "fps": anim.fps,
                    "loop": anim.loop,
                }
                for name, anim in self.animations.items()
            },
            "current_animation": self.current_animation,
            "spritesheet_columns": self.spritesheet_columns,
            "spritesheet_rows": self.spritesheet_rows,
            "frame_size": self.frame_size,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary."""
        sprite = cls(data.get("name", "AnimatedSprite"))
        sprite.spritesheet_columns = data.get("spritesheet_columns", 1)
        sprite.spritesheet_rows = data.get("spritesheet_rows", 1)
        sprite.frame_size = tuple(data.get("frame_size", [32, 32]))

        # Load animations
        for name, anim_data in data.get("animations", {}).items():
            sprite.add_animation(
                name,
                anim_data.get("frames", []),
                anim_data.get("fps", 12.0),
                anim_data.get("loop", True)
            )

        current = data.get("current_animation")
        if current:
            sprite.play(current)

        return sprite
