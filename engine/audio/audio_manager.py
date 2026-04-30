# /**************************************************************************/
# /*  audio_manager.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Audio manager for sound and music playback."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from collections import OrderedDict

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio system configuration."""
    master_volume: float = 1.0
    music_volume: float = 0.8
    sfx_volume: float = 1.0
    max_channels: int = 32
    sample_rate: int = 44100
    max_sound_cache: int = 50  # Maximum cached sounds to prevent memory leak
    max_active_sounds: int = 100  # Maximum concurrent playing sounds


class AudioManager:
    """Manages audio playback and resources."""

    _instance: Optional["AudioManager"] = None

    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        # Use OrderedDict for LRU cache behavior - prevents memory leaks
        self._sound_cache: OrderedDict[str, any] = OrderedDict()
        self._active_sounds: List["SoundEffect"] = []
        self._music_player: Optional["MusicPlayer"] = None

        self._muted: bool = False
        logger.info("AudioManager initialized with config: %s", self.config)
        self._paused: bool = False

        # Callbacks
        self._on_sound_finished: Optional[Callable[[str], None]] = None

    @classmethod
    def get_instance(cls) -> "AudioManager":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = AudioManager()
        return cls._instance

    def initialize(self) -> bool:
        """Initialize audio system."""
        # Placeholder - actual implementation would initialize Pygame/SDL mixer
        return True

    def shutdown(self) -> None:
        """Shutdown audio system."""
        self.stop_all()
        self._sound_cache.clear()

    def load_sound(self, path: str, cache: bool = True) -> Optional["SoundEffect"]:
        """Load a sound effect with LRU cache management."""
        # Move to end if already cached (LRU)
        if path in self._sound_cache:
            self._sound_cache.move_to_end(path)
            return self._sound_cache[path]

        # Create sound effect object
        from audio.sound_effect import SoundEffect
        sound = SoundEffect(path)

        if cache:
            # Enforce cache size limit to prevent memory leaks
            if len(self._sound_cache) >= self.config.max_sound_cache:
                # Remove oldest (first) item
                self._sound_cache.popitem(last=False)
            self._sound_cache[path] = sound

        return sound

    def unload_sound(self, path: str) -> None:
        """Unload a cached sound."""
        if path in self._sound_cache:
            del self._sound_cache[path]

    def _cleanup_finished_sounds(self) -> None:
        """Remove finished sounds from active list to prevent memory leak."""
        self._active_sounds = [s for s in self._active_sounds if s.is_playing()]

    def _enforce_active_sound_limit(self) -> None:
        """Ensure active sounds don't exceed limit by stopping oldest."""
        while len(self._active_sounds) > self.config.max_active_sounds:
            oldest = self._active_sounds.pop(0)
            oldest.stop()

    def play_sound(
        self,
        path: str,
        volume: float = 1.0,
        pitch: float = 1.0,
        loop: bool = False
    ) -> Optional["SoundEffect"]:
        """Play a sound effect with automatic cleanup."""
        # Cleanup finished sounds periodically
        self._cleanup_finished_sounds()

        sound = self.load_sound(path)
        if sound:
            sound.volume = volume * self.config.sfx_volume * self.config.master_volume
            sound.pitch = pitch
            sound.loop = loop
            sound.play()
            self._active_sounds.append(sound)
            # Enforce limit to prevent memory leak
            self._enforce_active_sound_limit()
        return sound

    def stop_sound(self, path: str) -> None:
        """Stop all instances of a sound."""
        for sound in self._active_sounds:
            if sound.path == path:
                sound.stop()

    def stop_all_sounds(self) -> None:
        """Stop all playing sounds."""
        for sound in self._active_sounds:
            sound.stop()
        self._active_sounds.clear()

    def play_music(self, path: str, volume: float = 1.0, loop: bool = True) -> None:
        """Play background music."""
        from audio.music_player import MusicPlayer

        if self._music_player is None:
            self._music_player = MusicPlayer()

        self._music_player.load(path)
        self._music_player.volume = volume * self.config.music_volume * self.config.master_volume
        self._music_player.loop = loop
        self._music_player.play()

    def stop_music(self) -> None:
        """Stop background music."""
        if self._music_player:
            self._music_player.stop()

    def pause_music(self) -> None:
        """Pause background music."""
        if self._music_player:
            self._music_player.pause()

    def resume_music(self) -> None:
        """Resume background music."""
        if self._music_player:
            self._music_player.resume()

    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 - 1.0)."""
        self.config.master_volume = max(0.0, min(1.0, volume))
        self._update_volumes()

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 - 1.0)."""
        self.config.music_volume = max(0.0, min(1.0, volume))
        if self._music_player:
            self._music_player.volume = volume * self.config.master_volume

    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 - 1.0)."""
        self.config.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self._active_sounds:
            sound.volume = sound.base_volume * volume * self.config.master_volume

    def mute(self) -> None:
        """Mute all audio."""
        self._muted = True
        self._update_volumes()

    def unmute(self) -> None:
        """Unmute all audio."""
        self._muted = False
        self._update_volumes()

    def toggle_mute(self) -> bool:
        """Toggle mute state. Returns new mute state."""
        if self._muted:
            self.unmute()
        else:
            self.mute()
        return self._muted

    def pause_all(self) -> None:
        """Pause all audio."""
        self._paused = True
        for sound in self._active_sounds:
            sound.pause()
        if self._music_player:
            self._music_player.pause()

    def resume_all(self) -> None:
        """Resume all audio."""
        self._paused = False
        for sound in self._active_sounds:
            sound.resume()
        if self._music_player:
            self._music_player.resume()

    def stop_all(self) -> None:
        """Stop all audio."""
        self.stop_all_sounds()
        self.stop_music()

    def _update_volumes(self) -> None:
        """Update all active audio volumes."""
        master = 0.0 if self._muted else self.config.master_volume

        for sound in self._active_sounds:
            sound.volume = sound.base_volume * self.config.sfx_volume * master

        if self._music_player:
            self._music_player.volume = self.config.music_volume * master

    def update(self, delta_time: float) -> None:
        """Update audio system (clean up finished sounds)."""
        # Remove finished sounds
        self._active_sounds = [s for s in self._active_sounds if s.is_playing]

    @property
    def is_muted(self) -> bool:
        return self._muted

    @property
    def is_paused(self) -> bool:
        return self._paused


def get_audio_manager() -> AudioManager:
    """Get global audio manager instance."""
    return AudioManager.get_instance()
