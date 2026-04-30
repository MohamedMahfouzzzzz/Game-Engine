# /**************************************************************************/
# /*  audio_stream.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Real-time audio streaming for procedural audio."""

from typing import Optional, Callable, List

import logging


logger = logging.getLogger(__name__)

try:
    import numpy as np
except ImportError:
    np = None


class AudioStream:
    """Real-time audio stream for custom audio generation."""

    def __init__(self, sample_rate: int = 44100, channels: int = 2):
        self.sample_rate = sample_rate
        self.channels = channels
        self._buffer_size = 1024

        self._playing = False
        self._paused = False

        # Callback for generating samples
        self._generate_callback: Optional[Callable[[int], np.ndarray]] = None

    def set_generator(self, callback: Callable[[int], any]) -> None:
        """Set callback that generates audio samples.

        Callback receives number of frames to generate and should return
        an array of shape (frames, channels) with float32 values.
        """
        self._generate_callback = callback

    def play(self) -> None:
        """Start the stream."""
        self._playing = True
        self._paused = False

    def stop(self) -> None:
        """Stop the stream."""
        self._playing = False
        self._paused = False

    def pause(self) -> None:
        """Pause the stream."""
        if self._playing:
            self._paused = True

    def resume(self) -> None:
        """Resume the stream."""
        if self._paused:
            self._paused = False
            self._playing = True

    def generate_silence(self, frames: int) -> List[List[float]]:
        """Generate silence (zeros)."""
        if np:
            return np.zeros((frames, self.channels), dtype=np.float32).tolist()
        return [[0.0] * self.channels for _ in range(frames)]

    def generate_sine(self, frames: int, frequency: float, amplitude: float = 0.5) -> List[List[float]]:
        """Generate sine wave."""
        import math
        result = []
        for i in range(frames):
            t = i / self.sample_rate
            sample = amplitude * math.sin(2 * math.pi * frequency * t)
            result.append([sample] * self.channels)
        return result

    def generate_noise(self, frames: int, amplitude: float = 0.1) -> List[List[float]]:
        """Generate white noise."""
        import random
        result = []
        for _ in range(frames):
            sample = random.uniform(-amplitude, amplitude)
            result.append([sample] * self.channels)
        return result

    @property
    def is_playing(self) -> bool:
        return self._playing and not self._paused
