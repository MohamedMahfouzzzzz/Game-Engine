# /**************************************************************************/
# /*  replay_system.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Replay system for debugging from playtest recordings."""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple

import logging

logger = logging.getLogger(__name__)


@dataclass
class ReplayFrame:
    """A single frame in the replay."""
    timestamp: float
    action: Dict[str, Any]
    state: Optional[Dict[str, Any]] = None


class ReplaySystem:
    """Replays recorded playtest sessions."""

    def __init__(self):
        self._frames: List[ReplayFrame] = []
        self._current_frame: int = 0
        self._is_playing: bool = False
        self._speed: float = 1.0
        self._start_time: float = 0

        # Callbacks
        self.on_frame: Optional[Callable[[ReplayFrame], None]] = None
        self.on_complete: Optional[Callable[[], None]] = None

    def load_playtest(self, playtest_file: Path) -> bool:
        """Load a playtest file for replay."""
        try:
            with open(playtest_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._frames.clear()
            start_time = data.get("start_time", 0)

            for action in data.get("actions", []):
                frame = ReplayFrame(
                    timestamp=action.get("timestamp", 0) - start_time,
                    action=action
                )
                self._frames.append(frame)

            self._current_frame = 0
            return True

        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def play(self, speed: float = 1.0) -> None:
        """Start replay playback."""
        self._speed = speed
        self._is_playing = True
        self._start_time = time.time()

    def pause(self) -> None:
        """Pause replay."""
        self._is_playing = False

    def stop(self) -> None:
        """Stop replay and reset to beginning."""
        self._is_playing = False
        self._current_frame = 0

    def step_forward(self, count: int = 1) -> None:
        """Advance by specified number of frames."""
        self._current_frame = min(self._current_frame + count, len(self._frames) - 1)
        if self._frames:
            frame = self._frames[self._current_frame]
            if self.on_frame:
                self.on_frame(frame)

    def step_backward(self, count: int = 1) -> None:
        """Go back by specified number of frames."""
        self._current_frame = max(self._current_frame - count, 0)
        if self._frames:
            frame = self._frames[self._current_frame]
            if self.on_frame:
                self.on_frame(frame)

    def update(self) -> None:
        """Update replay state (call regularly when playing)."""
        if not self._is_playing or not self._frames:
            return

        elapsed = (time.time() - self._start_time) * self._speed

        # Find and emit all frames that should have played by now
        while (self._current_frame < len(self._frames) and
               self._frames[self._current_frame].timestamp <= elapsed):
            if self.on_frame:
                self.on_frame(self._frames[self._current_frame])
            self._current_frame += 1

        if self._current_frame >= len(self._frames):
            self._is_playing = False
            if self.on_complete:
                self.on_complete()

    def seek_to_time(self, seconds: float) -> None:
        """Jump to a specific time in the replay."""
        # Find closest frame
        for i, frame in enumerate(self._frames):
            if frame.timestamp >= seconds:
                self._current_frame = i
                break
        else:
            self._current_frame = len(self._frames) - 1

    def seek_to_action(self, action_type: str) -> bool:
        """Jump to next occurrence of action type."""
        for i in range(self._current_frame + 1, len(self._frames)):
            if self._frames[i].action.get("type") == action_type:
                self._current_frame = i
                return True
        return False

    def get_current_time(self) -> float:
        """Get current replay time in seconds."""
        if not self._frames or self._current_frame >= len(self._frames):
            return 0.0
        return self._frames[self._current_frame].timestamp

    def get_total_duration(self) -> float:
        """Get total replay duration."""
        if not self._frames:
            return 0.0
        return self._frames[-1].timestamp

    def get_action_summary(self) -> Dict[str, int]:
        """Get count of each action type."""
        counts = {}
        for frame in self._frames:
            action_type = frame.action.get("type", "unknown")
            counts[action_type] = counts.get(action_type, 0) + 1
        return counts

    def get_player_positions(self) -> List[Tuple[float, float, float]]:
        """Get list of (time, x, y) positions from movement actions."""
        positions = []
        for frame in self._frames:
            if frame.action.get("type") == "movement":
                pos = frame.action.get("position")
                if pos:
                    positions.append((frame.timestamp, pos[0], pos[1]))
        return positions

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def current_frame(self) -> int:
        return self._current_frame

    @property
    def total_frames(self) -> int:
        return len(self._frames)

    @property
    def progress(self) -> float:
        """Get playback progress as percentage (0-1)."""
        if not self._frames:
            return 0.0
        return self._current_frame / len(self._frames)
