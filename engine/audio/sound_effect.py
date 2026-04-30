# /**************************************************************************/
# /*  sound_effect.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Sound effect playback."""

from typing import Optional, Callable
from pathlib import Path

import logging


logger = logging.getLogger(__name__)



class SoundEffect:
    """A sound effect that can be played."""

    def __init__(self, path: str):
        self.path = path
        self._loaded = False
        self._playing = False
        self._paused = False

        # Properties
        self.base_volume: float = 1.0
        self._volume: float = 1.0
        self.pitch: float = 1.0
        self.loop: bool = False
        self.position: float = 0.0  # Playback position in seconds

        # Callbacks
        self._on_finished: Optional[Callable[[], None]] = None

    def load(self) -> bool:
        """Load sound data from file."""
        # Placeholder - actual implementation would load with Pygame/SDL
        if Path(self.path).exists():
            self._loaded = True
            return True
        return False

    def play(self) -> bool:
        """Start playback."""
        if not self._loaded and not self.load():
            return False

        self._playing = True
        self._paused = False
        self.position = 0.0
        return True

    def stop(self) -> None:
        """Stop playback."""
        self._playing = False
        self._paused = False
        self.position = 0.0

        if self._on_finished:
            self._on_finished()

    def pause(self) -> None:
        """Pause playback."""
        if self._playing:
            self._paused = True

    def resume(self) -> None:
        """Resume playback."""
        if self._paused:
            self._paused = False
            self._playing = True

    def seek(self, position: float) -> None:
        """Seek to position in seconds."""
        self.position = max(0.0, position)

    @property
    def volume(self) -> float:
        """Get current volume."""
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        """Set volume (0.0 - 1.0)."""
        self._volume = max(0.0, min(1.0, value))

    @property
    def is_playing(self) -> bool:
        """Check if sound is currently playing."""
        return self._playing and not self._paused

    @property
    def is_paused(self) -> bool:
        return self._paused

    def connect_finished(self, callback: Callable[[], None]) -> None:
        """Connect callback for when sound finishes."""
        self._on_finished = callback
