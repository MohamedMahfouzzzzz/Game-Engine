# /**************************************************************************/
# /*  glitch_detector.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Automatic glitch detection for playtest recordings."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

import logging



logger = logging.getLogger(__name__)

class GlitchType(Enum):
    """Types of detected glitches."""
    PLAYER_STUCK = "player_stuck"
    RAPID_DEATH = "rapid_death"
    OUT_OF_BOUNDS = "out_of_bounds"
    INFINITE_FALL = "infinite_fall"
    CLIPPING = "clipping"
    SOFT_LOCK = "soft_lock"
    FPS_DROP = "fps_drop"
    MEMORY_LEAK = "memory_leak"
    IDLE_AFK = "idle_afk"  # Not a glitch, but detected idle period


@dataclass
class GlitchReport:
    """Report of a detected glitch."""
    glitch_type: GlitchType
    timestamp: float
    severity: int  # 1-5
    description: str
    position: Optional[tuple] = None
    evidence: Dict[str, Any] = None


class GlitchDetector:
    """Analyzes playtest data for glitches and anomalies."""

    def __init__(self):
        self.thresholds = {
            "stuck_time": 5.0,  # Seconds without movement
            "death_window": 10.0,  # Time window for rapid deaths
            "max_deaths": 3,  # Deaths in window to trigger
            "bounds_buffer": 1000,  # Distance past bounds to trigger
            "min_fps": 30,  # Minimum acceptable FPS
            "soft_lock_time": 60.0,  # Time without progress
        }

        self._on_glitch_found: Optional[Callable[[GlitchReport], None]] = None

    def analyze_playtest(self, playtest_file: Path) -> List[GlitchReport]:
        """Analyze a playtest file for glitches."""
        with open(playtest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        actions = data.get("actions", [])
        reports: List[GlitchReport] = []

        # Run all detection methods
        reports.extend(self._detect_player_stuck(actions))
        reports.extend(self._detect_rapid_deaths(actions))
        reports.extend(self._detect_out_of_bounds(actions))
        reports.extend(self._detect_soft_lock(actions))
        reports.extend(self._detect_fps_issues(actions))

        # Sort by timestamp
        reports.sort(key=lambda r: r.timestamp)

        return reports

    def _detect_player_stuck(self, actions: List[Dict]) -> List[GlitchReport]:
        """Detect when player is stuck without movement (input-aware)."""
        reports = []
        stuck_start = None
        last_pos = None
        last_input_time = None
        idle_reports = []  # Separate idle/AFK reports

        for action in actions:
            action_type = action.get("type")
            timestamp = action.get("timestamp", 0)
            window_focused = action.get("window_focused", True)

            # Track input events (key presses, controller input, mouse clicks)
            if action_type == "input":
                last_input_time = timestamp

            if action_type == "movement":
                pos = action.get("position")
                if pos and last_pos:
                    distance = ((pos[0] - last_pos[0]) ** 2 + (pos[1] - last_pos[1]) ** 2) ** 0.5
                    if distance < 1.0:  # Not moving
                        if stuck_start is None:
                            stuck_start = timestamp
                        elif timestamp - stuck_start > self.thresholds["stuck_time"]:
                            # Check if there was active input during this period
                            has_input = (last_input_time is not None and
                                        last_input_time >= stuck_start)

                            if has_input and window_focused:
                                # Active input but no movement = PLAYER_STUCK
                                reports.append(GlitchReport(
                                    glitch_type=GlitchType.PLAYER_STUCK,
                                    timestamp=stuck_start,
                                    severity=3,
                                    description=f"Player stuck for {self.thresholds['stuck_time']}s (input detected)",
                                    position=pos,
                                    evidence={"duration": timestamp - stuck_start, "has_input": True}
                                ))
                            elif not has_input and window_focused:
                                # No input and no movement = IDLE/AFK
                                idle_reports.append(GlitchReport(
                                    glitch_type=GlitchType.IDLE_AFK,
                                    timestamp=stuck_start,
                                    severity=1,
                                    description=f"Player idle for {self.thresholds['stuck_time']}s",
                                    position=pos,
                                    evidence={"duration": timestamp - stuck_start, "has_input": False}
                                ))
                            stuck_start = None
                    else:
                        stuck_start = None
                last_pos = pos

        # Combine reports (idle reports first, then actual glitches)
        return idle_reports + reports

    def _detect_rapid_deaths(self, actions: List[Dict]) -> List[GlitchReport]:
        """Detect rapid successive deaths (possible difficulty spike)."""
        reports = []
        deaths = []

        for action in actions:
            if action.get("type") == "death":
                deaths.append(action)

        # Check for death clusters
        for i, death in enumerate(deaths):
            window_start = death.get("timestamp", 0)
            deaths_in_window = [
                d for d in deaths
                if window_start <= d.get("timestamp", 0) <= window_start + self.thresholds["death_window"]
            ]

            if len(deaths_in_window) >= self.thresholds["max_deaths"]:
                reports.append(GlitchReport(
                    glitch_type=GlitchType.RAPID_DEATH,
                    timestamp=window_start,
                    severity=4,
                    description=f"{len(deaths_in_window)} deaths in {self.thresholds['death_window']}s",
                    position=death.get("position"),
                    evidence={"death_count": len(deaths_in_window)}
                ))
                break  # Only report once per cluster

        return reports

    def _detect_out_of_bounds(self, actions: List[Dict]) -> List[GlitchReport]:
        """Detect player going out of expected bounds."""
        reports = []

        # Calculate expected bounds from movement data
        positions = [a.get("position") for a in actions if a.get("position")]
        if not positions:
            return reports

        xs = [p[0] for p in positions if p]
        ys = [p[1] for p in positions if p]

        if not xs or not ys:
            return reports

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Add buffer for expected bounds
        buffer = self.thresholds["bounds_buffer"]

        for action in actions:
            if action.get("type") in ("movement", "death"):
                pos = action.get("position")
                if not pos:
                    continue

                x, y = pos
                if (x < min_x - buffer or x > max_x + buffer or
                    y < min_y - buffer or y > max_y + buffer):
                    reports.append(GlitchReport(
                        glitch_type=GlitchType.OUT_OF_BOUNDS,
                        timestamp=action.get("timestamp", 0),
                        severity=4,
                        description=f"Player out of bounds at ({x:.1f}, {y:.1f})",
                        position=pos,
                        evidence={"bounds": (min_x, max_x, min_y, max_y)}
                    ))
                    break  # Only report once

        return reports

    def _detect_soft_lock(self, actions: List[Dict]) -> List[GlitchReport]:
        """Detect potential soft locks (no progress for extended time with active movement)."""
        reports = []
        last_progress = 0
        last_progress_time = 0

        progress_actions = {"level_complete", "checkpoint", "collectible", "interaction"}

        for action in actions:
            if action.get("type") in progress_actions:
                last_progress += 1
                last_progress_time = action.get("timestamp", 0)

        # Check if session ended without recent progress
        if actions:
            final_time = actions[-1].get("timestamp", 0)
            time_without_progress = final_time - last_progress_time

            if time_without_progress > self.thresholds["soft_lock_time"]:
                # Calculate total movement distance during the no-progress period
                movement_distance = 0.0
                for action in actions:
                    timestamp = action.get("timestamp", 0)
                    if timestamp >= last_progress_time and action.get("type") == "movement":
                        pos = action.get("position")
                        if pos:
                            # Add distance from origin (simplified - actual would track consecutive positions)
                            movement_distance += (pos[0]**2 + pos[1]**2)**0.5

                # Only trigger soft-lock if player was actively moving (distance > threshold)
                # This distinguishes between soft-lock and AFK/idle
                movement_threshold = 500.0  # Minimum movement to consider "active"
                if movement_distance > movement_threshold:
                    reports.append(GlitchReport(
                        glitch_type=GlitchType.SOFT_LOCK,
                        timestamp=last_progress_time,
                        severity=3,
                        description=f"No progress for {time_without_progress:.0f}s while actively moving",
                        evidence={
                            "last_progress_count": last_progress,
                            "movement_distance": movement_distance
                        }
                    ))
                else:
                    # Low movement during no-progress period = likely idle/AFK
                    # Could log as IDLE_AFK instead
                    pass

        return reports

    def _detect_fps_issues(self, actions: List[Dict]) -> List[GlitchReport]:
        """Detect FPS drops from performance data."""
        reports = []

        for action in actions:
            if action.get("type") == "fps_drop":
                fps = action.get("data", {}).get("fps", 60)
                if fps < self.thresholds["min_fps"]:
                    reports.append(GlitchReport(
                        glitch_type=GlitchType.FPS_DROP,
                        timestamp=action.get("timestamp", 0),
                        severity=2,
                        description=f"FPS dropped to {fps:.1f}",
                        evidence={"fps": fps}
                    ))

        return reports

    def generate_report_file(self, playtest_file: Path, output_file: Optional[Path] = None) -> Path:
        """Generate a glitch report file for a playtest."""
        reports = self.analyze_playtest(playtest_file)

        if output_file is None:
            output_file = playtest_file.with_suffix(".glitch_report.json")

        data = {
            "source_file": str(playtest_file),
            "glitch_count": len(reports),
            "severity_counts": self._count_by_severity(reports),
            "type_counts": self._count_by_type(reports),
            "glitches": [
                {
                    "type": r.glitch_type.value,
                    "timestamp": r.timestamp,
                    "severity": r.severity,
                    "description": r.description,
                    "position": r.position,
                    "evidence": r.evidence
                }
                for r in reports
            ]
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return output_file

    def _count_by_severity(self, reports: List[GlitchReport]) -> Dict[int, int]:
        """Count glitches by severity level."""
        counts = {}
        for r in reports:
            counts[r.severity] = counts.get(r.severity, 0) + 1
        return counts

    def _count_by_type(self, reports: List[GlitchReport]) -> Dict[str, int]:
        """Count glitches by type."""
        counts = {}
        for r in reports:
            counts[r.glitch_type.value] = counts.get(r.glitch_type.value, 0) + 1
        return counts

    def on_glitch_found(self, callback: Callable[[GlitchReport], None]) -> None:
        """Register callback for when glitch is found."""
        self._on_glitch_found = callback
