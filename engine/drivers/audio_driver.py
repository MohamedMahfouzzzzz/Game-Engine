# /**************************************************************************/
# /*  audio_driver.py                                                       */
# /**************************************************************************/

"""Audio driver abstraction - Cross-platform audio output.

Simplified Python port of Godot audio drivers (wasapi, pulseaudio, alsa, coreaudio).
Uses pygame/SDL2 as the backend for actual audio output.
"""

from enum import IntEnum
from typing import Optional, Callable, List, Dict
from dataclasses import dataclass
import threading
import queue


class AudioFormat(IntEnum):
    """Audio sample formats."""
    AUDIO_FORMAT_8 = 0
    AUDIO_FORMAT_16 = 1
    AUDIO_FORMAT_32 = 2
    AUDIO_FORMAT_FLOAT = 3
    AUDIO_FORMAT_MAX = 4


class SpeakerMode(IntEnum):
    """Speaker configurations."""
    SPEAKER_MODE_STEREO = 0
    SPEAKER_SURROUND_31 = 1
    SPEAKER_SURROUND_51 = 2
    SPEAKER_SURROUND_71 = 3
    SPEAKER_MODE_MAX = 4


@dataclass
class AudioConfig:
    """Audio configuration."""
    sample_rate: int = 48000
    channels: int = 2
    format: AudioFormat = AudioFormat.AUDIO_FORMAT_FLOAT
    buffer_size: int = 512
    period_size: int = 1024


class AudioDriver:
    """Abstract audio driver interface."""
    
    def __init__(self, name: str = "AudioDriver"):
        self._name = name
        self._config = AudioConfig()
        self._active: bool = False
        self._paused: bool = False
        self._output_latency: float = 0.0
        self._input_latency: float = 0.0
        self._buffer: queue.Queue = queue.Queue(maxsize=4)
        self._mix_callback: Optional[Callable[[bytes], None]] = None
        self._thread: Optional[threading.Thread] = None
    
    def get_name(self) -> str:
        return self._name
    
    def initialize(self) -> bool:
        """Initialize the audio driver."""
        return False
    
    def start(self) -> bool:
        """Start audio processing."""
        self._active = True
        return True
    
    def stop(self) -> None:
        """Stop audio processing."""
        self._active = False
        self._paused = False
    
    def pause(self) -> None:
        """Pause audio."""
        self._paused = True
    
    def resume(self) -> None:
        """Resume audio."""
        self._paused = False
    
    def is_active(self) -> bool:
        return self._active
    
    def is_paused(self) -> bool:
        return self._paused
    
    def get_output_latency(self) -> float:
        """Get output latency in seconds."""
        return self._output_latency
    
    def get_input_latency(self) -> float:
        """Get input latency in seconds."""
        return self._input_latency
    
    def set_mix_callback(self, callback: Callable[[bytes], None]) -> None:
        """Set callback for audio mixing."""
        self._mix_callback = callback
    
    def get_sample_rate(self) -> int:
        return self._config.sample_rate
    
    def get_channels(self) -> int:
        return self._config.channels
    
    def get_buffer_size(self) -> int:
        return self._config.buffer_size
    
    def set_config(self, config: AudioConfig) -> None:
        self._config = config
    
    def get_config(self) -> AudioConfig:
        return self._config


class SDL2AudioDriver(AudioDriver):
    """SDL2-based audio driver."""
    
    def __init__(self):
        super().__init__("SDL2")
        self._sdl_initialized = False
    
    def initialize(self) -> bool:
        try:
            import pygame
            pygame.mixer.init(
                frequency=self._config.sample_rate,
                channels=self._config.channels,
                buffer=self._config.buffer_size
            )
            self._sdl_initialized = True
            return True
        except ImportError:
            return False
    
    def start(self) -> bool:
        if not self._sdl_initialized:
            return False
        self._active = True
        return True
    
    def stop(self) -> None:
        super().stop()
        try:
            import pygame
            pygame.mixer.quit()
        except:
            pass


class AudioDriverManager:
    """Manages available audio drivers."""
    
    def __init__(self):
        self._drivers: Dict[str, AudioDriver] = {}
        self._current: Optional[AudioDriver] = None
        self._register_builtin_drivers()
    
    def _register_builtin_drivers(self) -> None:
        """Register built-in drivers."""
        sdl = SDL2AudioDriver()
        self._drivers[sdl.get_name()] = sdl
    
    def get_driver(self, name: str) -> Optional[AudioDriver]:
        return self._drivers.get(name)
    
    def get_available_drivers(self) -> List[str]:
        return list(self._drivers.keys())
    
    def initialize_driver(self, name: str) -> bool:
        driver = self._drivers.get(name)
        if driver and driver.initialize():
            self._current = driver
            return True
        return False
    
    def get_current_driver(self) -> Optional[AudioDriver]:
        return self._current
    
    def shutdown(self) -> None:
        if self._current:
            self._current.stop()
            self._current = None
