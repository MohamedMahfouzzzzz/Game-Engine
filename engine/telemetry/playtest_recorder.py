# /**************************************************************************/
# /*  playtest_recorder.py                                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Records playtest sessions for analysis."""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

import logging

logger = logging.getLogger(__name__)


@dataclass
class PlayerAction:
    """A single player action/event."""
    timestamp: float
    action_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    position: Optional[tuple] = None
    window_focused: bool = True  # Track if game window had focus


@dataclass
class PlaytestSession:
    """Complete playtest session data."""
    session_id: str
    project_id: str
    player_id: str
    start_time: float
    end_time: Optional[float] = None
    actions: List[PlayerAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PlaytestRecorder:
    """Records and manages playtest sessions."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("telemetry/playtests")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._active_session: Optional[PlaytestSession] = None
        self._is_recording = False
        self._action_buffer: List[PlayerAction] = []
        self._buffer_size = 100
        self._window_focused = True
        self._last_heartbeat: float = 0
        self._heartbeat_interval = 5.0  # Heartbeat every 5 seconds

        # Callbacks
        self.on_action_recorded: Optional[Callable[[PlayerAction], None]] = None
        self.on_session_saved: Optional[Callable[[Path], None]] = None

    def start_session(
        self,
        project_id: str,
        player_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new recording session."""
        if self._is_recording:
            self.stop_session()

        session_id = str(uuid.uuid4())
        self._active_session = PlaytestSession(
            session_id=session_id,
            project_id=project_id,
            player_id=player_id or f"anonymous_{int(time.time())}",
            start_time=time.time(),
            metadata=metadata or {}
        )
        self._is_recording = True
        self._action_buffer.clear()

        return session_id

    def stop_session(self) -> Optional[Path]:
        """Stop recording and save session."""
        if not self._is_recording or not self._active_session:
            return None

        # Flush buffer
        self._flush_buffer()

        self._active_session.end_time = time.time()
        self._is_recording = False

        # Save to file
        file_path = self._save_session()

        self._active_session = None
        return file_path

    def record_action(
        self,
        action_type: str,
        data: Optional[Dict[str, Any]] = None,
        position: Optional[tuple] = None
    ) -> None:
        """Record a player action."""
        if not self._is_recording:
            return

        action = PlayerAction(
            timestamp=time.time(),
            action_type=action_type,
            data=data or {},
            position=position,
            window_focused=self._window_focused
        )

        self._action_buffer.append(action)

        if len(self._action_buffer) >= self._buffer_size:
            self._flush_buffer()

        if self.on_action_recorded:
            self.on_action_recorded(action)

    def record_movement(self, x: float, y: float, velocity: Optional[tuple] = None) -> None:
        """Record player movement."""
        data = {"velocity": velocity} if velocity else {}
        self.record_action("movement", data, (x, y))

    def record_death(self, cause: str, position: tuple) -> None:
        """Record player death."""
        self.record_action("death", {"cause": cause}, position)

    def record_level_complete(self, level_id: str, time_taken: float) -> None:
        """Record level completion."""
        self.record_action("level_complete", {
            "level_id": level_id,
            "time_taken": time_taken
        })

    def record_interaction(self, object_id: str, interaction_type: str, position: tuple) -> None:
        """Record object interaction."""
        self.record_action("interaction", {
            "object_id": object_id,
            "interaction_type": interaction_type
        }, position)

    def record_input(self, input_type: str, input_data: Optional[Dict[str, Any]] = None) -> None:
        """Record user input (key press, controller button, mouse click)."""
        self.record_action("input", {
            "input_type": input_type,
            **(input_data or {})
        })

    def set_window_focus(self, focused: bool) -> None:
        """Set whether the game window is currently focused."""
        self._window_focused = focused

    def update_heartbeat(self) -> None:
        """Update heartbeat - call regularly in game loop."""
        if not self._is_recording:
            return

        current_time = time.time()
        if current_time - self._last_heartbeat >= self._heartbeat_interval:
            self.record_action("heartbeat", {
                "window_focused": self._window_focused
            })
            self._last_heartbeat = current_time

    def _flush_buffer(self) -> None:
        """Write buffered actions to session."""
        if self._active_session and self._action_buffer:
            self._active_session.actions.extend(self._action_buffer)
            self._action_buffer.clear()

    def _save_session(self) -> Path:
        """Save session to file."""
        if not self._active_session:
            raise RuntimeError("No active session to save")

        timestamp = datetime.fromtimestamp(self._active_session.start_time)
        filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{self._active_session.session_id[:8]}.playtest"
        file_path = self.output_dir / filename

        # Convert to serializable format
        data = {
            "session_id": self._active_session.session_id,
            "project_id": self._active_session.project_id,
            "player_id": self._active_session.player_id,
            "start_time": self._active_session.start_time,
            "end_time": self._active_session.end_time,
            "duration": (self._active_session.end_time or time.time()) - self._active_session.start_time,
            "action_count": len(self._active_session.actions),
            "metadata": self._active_session.metadata,
            "actions": [
                {
                    "timestamp": a.timestamp,
                    "relative_time": a.timestamp - self._active_session.start_time,
                    "type": a.action_type,
                    "data": a.data,
                    "position": a.position,
                    "window_focused": a.window_focused
                }
                for a in self._active_session.actions
            ]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        if self.on_session_saved:
            self.on_session_saved(file_path)

        return file_path

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    @property
    def action_count(self) -> int:
        if not self._active_session:
            return 0
        return len(self._active_session.actions) + len(self._action_buffer)

    def get_session_duration(self) -> float:
        """Get current session duration in seconds."""
        if not self._active_session:
            return 0.0
        return time.time() - self._active_session.start_time
