# /**************************************************************************/
# /*  music_player.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Music player for background music."""

from typing import Optional, Callable, List
from pathlib import Path

import logging


logger = logging.getLogger(__name__)



class MusicPlayer:
    """Player for background music with playlist support."""

    def __init__(self):
        self._current_track: Optional[str] = None
        self._playlist: List[str] = []
        self._playlist_index: int = 0

        self._playing: bool = False
        self._paused: bool = False
        self._loop: bool = False

        self._volume: float = 1.0
        self.position: float = 0.0
        self.duration: float = 0.0

        self._on_track_finished: Optional[Callable[[], None]] = None
        self._on_playlist_finished: Optional[Callable[[], None]] = None

    def load(self, path: str) -> bool:
        """Load a music track."""
        if Path(path).exists():
            self._current_track = path
            self.position = 0.0
            return True
        return False

    def play(self) -> None:
        """Start or resume playback."""
        if self._current_track:
            self._playing = True
            self._paused = False

    def stop(self) -> None:
        """Stop playback."""
        self._playing = False
        self._paused = False
        self.position = 0.0

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
        """Seek to position."""
        self.position = max(0.0, min(position, self.duration))

    def set_playlist(self, tracks: List[str]) -> None:
        """Set the playlist."""
        self._playlist = tracks
        self._playlist_index = 0
        if tracks:
            self.load(tracks[0])

    def next_track(self) -> bool:
        """Play next track in playlist."""
        if not self._playlist:
            return False

        self._playlist_index = (self._playlist_index + 1) % len(self._playlist)
        self.load(self._playlist[self._playlist_index])
        self.play()
        return True

    def previous_track(self) -> bool:
        """Play previous track in playlist."""
        if not self._playlist:
            return False

        self._playlist_index = (self._playlist_index - 1) % len(self._playlist)
        self.load(self._playlist[self._playlist_index])
        self.play()
        return True

    def shuffle_playlist(self) -> None:
        """Shuffle the playlist."""
        import random
        if self._playlist:
            random.shuffle(self._playlist)
            self._playlist_index = 0
            self.load(self._playlist[0])

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = max(0.0, min(1.0, value))

    @property
    def loop(self) -> bool:
        return self._loop

    @loop.setter
    def loop(self, value: bool) -> None:
        self._loop = value

    @property
    def is_playing(self) -> bool:
        return self._playing and not self._paused

    @property
    def current_track(self) -> Optional[str]:
        return self._current_track

    @property
    def playlist(self) -> List[str]:
        return self._playlist.copy()

    @property
    def playlist_position(self) -> int:
        return self._playlist_index

    def connect_track_finished(self, callback: Callable[[], None]) -> None:
        """Connect callback for when track finishes."""
        self._on_track_finished = callback

    def connect_playlist_finished(self, callback: Callable[[], None]) -> None:
        """Connect callback for when playlist finishes."""
        self._on_playlist_finished = callback
