# /**************************************************************************/
# /*  audio_controller.py                                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Native audio controller for engine."""

from typing import Dict, Optional, List
from enum import Enum

class SoundType(Enum):
    """Types of sounds."""
    MUSIC = "music"
    SFX = "sfx"
    VOICE = "voice"
    AMBIENT = "ambient"


class AudioController:
    """Native engine audio controller for managing game audio."""

    def __init__(self):
        self._sounds: Dict[str, Dict] = {}
        self._music_volume: float = 1.0
        self._sfx_volume: float = 1.0
        self._master_volume: float = 1.0
        self._muted: bool = False
        self._current_music: Optional[str] = None

    def load_sound(self, name: str, path: str, sound_type: SoundType = SoundType.SFX) -> bool:
        """Load a sound from file."""
        try:
            self._sounds[name] = {
                'path': path,
                'type': sound_type,
                'loaded': True
            }
            return True
        except Exception:
            return False

    def play_sound(self, name: str, volume: float = 1.0, loop: bool = False) -> bool:
        """Play a sound."""
        if name not in self._sounds or self._muted:
            return False

        sound = self._sounds[name]
        if not sound['loaded']:
            return False

        # Calculate volume based on type
        if sound['type'] == SoundType.MUSIC:
            final_volume = volume * self._music_volume * self._master_volume
        elif sound['type'] == SoundType.SFX:
            final_volume = volume * self._sfx_volume * self._master_volume
        else:
            final_volume = volume * self._master_volume

        # In a real implementation, this would use a sound library like pygame.mixer or similar
        # For now, we'll just track the state
        sound['playing'] = True
        sound['volume'] = final_volume
        sound['loop'] = loop

        if sound['type'] == SoundType.MUSIC:
            self._current_music = name

        return True

    def stop_sound(self, name: str) -> bool:
        """Stop a sound."""
        if name in self._sounds:
            self._sounds[name]['playing'] = False
            if self._current_music == name:
                self._current_music = None
            return True
        return False

    def stop_all_sounds(self) -> None:
        """Stop all sounds."""
        for name in self._sounds:
            self._sounds[name]['playing'] = False
        self._current_music = None

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self._music_volume = max(0.0, min(1.0, volume))

    def set_sfx_volume(self, volume: float) -> None:
        """Set SFX volume (0.0 to 1.0)."""
        self._sfx_volume = max(0.0, min(1.0, volume))

    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)."""
        self._master_volume = max(0.0, min(1.0, volume))

    def get_music_volume(self) -> float:
        """Get current music volume."""
        return self._music_volume

    def get_sfx_volume(self) -> float:
        """Get current SFX volume."""
        return self._sfx_volume

    def get_master_volume(self) -> float:
        """Get current master volume."""
        return self._master_volume

    def mute(self) -> None:
        """Mute all audio."""
        self._muted = True

    def unmute(self) -> None:
        """Unmute all audio."""
        self._muted = False

    def is_muted(self) -> bool:
        """Check if audio is muted."""
        return self._muted

    def is_playing(self, name: str) -> bool:
        """Check if a sound is playing."""
        if name in self._sounds:
            return self._sounds[name].get('playing', False)
        return False

    def get_current_music(self) -> Optional[str]:
        """Get currently playing music."""
        return self._current_music

    def unload_sound(self, name: str) -> bool:
        """Unload a sound from memory."""
        if name in self._sounds:
            del self._sounds[name]
            return True
        return False
