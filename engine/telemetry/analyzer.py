# /**************************************************************************/
# /*  analyzer.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Telemetry data analyzer for insights and heatmaps."""

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

import logging

logger = logging.getLogger(__name__)


@dataclass
class HeatmapCell:
    """A cell in the heatmap grid."""
    x: int
    y: int
    count: int
    intensity: float


@dataclass
class AnalyticsReport:
    """Complete analytics report for a playtest session."""
    total_playtime: float
    action_count: int
    death_count: int
    level_completions: int
    interactions: int
    most_active_area: Optional[Tuple[float, float]]
    average_session_time: float


class TelemetryAnalyzer:
    """Analyzes playtest data to generate insights and heatmaps."""

    def __init__(self):
        self.heatmap_resolution = 32  # pixels per cell

    def analyze_session(self, playtest_file: Path) -> AnalyticsReport:
        """Generate analytics report from a playtest file."""
        with open(playtest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        actions = data.get("actions", [])
        duration = data.get("duration", 0)

        # Detect and trim idle periods
        idle_time = self._detect_idle_time(actions)
        active_playtime = duration - idle_time

        # Count events
        death_count = sum(1 for a in actions if a.get("type") == "death")
        completions = sum(1 for a in actions if a.get("type") == "level_complete")
        interactions = sum(1 for a in actions if a.get("type") == "interaction")

        # Calculate most active area
        positions = [a.get("position") for a in actions if a.get("position")]
        most_active = self._calculate_centroid(positions) if positions else None

        return AnalyticsReport(
            total_playtime=duration,
            action_count=len(actions),
            death_count=death_count,
            level_completions=completions,
            interactions=interactions,
            most_active_area=most_active,
            average_session_time=active_playtime  # Use active playtime instead of total
        )

    def generate_heatmap(
        self,
        playtest_file: Path,
        bounds: Optional[Tuple[float, float, float, float]] = None
    ) -> List[HeatmapCell]:
        """Generate position heatmap from movement data."""
        with open(playtest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Collect positions
        positions = []
        for action in data.get("actions", []):
            if action.get("type") == "movement":
                pos = action.get("position")
                if pos:
                    positions.append((pos[0], pos[1]))

        if not positions:
            return []

        # Calculate bounds if not provided
        if bounds is None:
            xs = [p[0] for p in positions]
            ys = [p[1] for p in positions]
            padding = 100
            bounds = (min(xs) - padding, min(ys) - padding,
                     max(xs) + padding, max(ys) + padding)

        min_x, min_y, max_x, max_y = bounds
        width = int((max_x - min_x) / self.heatmap_resolution)
        height = int((max_y - min_y) / self.heatmap_resolution)

        # Count positions in each cell
        cell_counts = defaultdict(int)
        for x, y in positions:
            cell_x = int((x - min_x) / self.heatmap_resolution)
            cell_y = int((y - min_y) / self.heatmap_resolution)
            if 0 <= cell_x < width and 0 <= cell_y < height:
                cell_counts[(cell_x, cell_y)] += 1

        # Find max for normalization
        max_count = max(cell_counts.values()) if cell_counts else 1

        # Create heatmap cells
        heatmap = []
        for (cell_x, cell_y), count in cell_counts.items():
            intensity = count / max_count
            heatmap.append(HeatmapCell(
                x=cell_x,
                y=cell_y,
                count=count,
                intensity=intensity
            ))

        return heatmap

    def save_heatmap_image(
        self,
        heatmap: List[HeatmapCell],
        output_file: Path,
        width: int = 512,
        height: int = 512
    ) -> None:
        """Save heatmap as a PNG image."""
        # This is a placeholder - actual implementation would use PIL/Pillow
        # to generate a heatmap visualization
        data = {
            "width": width,
            "height": height,
            "resolution": self.heatmap_resolution,
            "cells": [
                {"x": c.x, "y": c.y, "count": c.count, "intensity": c.intensity}
                for c in heatmap
            ]
        }

        # Save as JSON for now (can be rendered by external tools)
        json_file = output_file.with_suffix(".heatmap.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def analyze_player_flow(self, playtest_file: Path) -> Dict[str, Any]:
        """Analyze player movement flow through the level."""
        with open(playtest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        actions = data.get("actions", [])

        # Track movement segments
        segments = []
        current_segment = []

        for action in actions:
            action_type = action.get("type")

            if action_type == "movement":
                pos = action.get("position")
                if pos:
                    current_segment.append((pos[0], pos[1]))
            elif action_type in ("death", "checkpoint", "level_complete"):
                if current_segment:
                    segments.append({
                        "type": action_type,
                        "path": current_segment.copy(),
                        "length": len(current_segment)
                    })
                    current_segment = []

        # Calculate path statistics
        total_path_length = 0
        for segment in segments:
            path = segment["path"]
            for i in range(1, len(path)):
                dx = path[i][0] - path[i-1][0]
                dy = path[i][1] - path[i-1][1]
                total_path_length += math.sqrt(dx*dx + dy*dy)

        return {
            "segment_count": len(segments),
            "total_path_length": total_path_length,
            "segments": segments
        }

    def compare_sessions(
        self,
        session_files: List[Path]
    ) -> Dict[str, Any]:
        """Compare multiple playtest sessions."""
        reports = [self.analyze_session(f) for f in session_files]

        if not reports:
            return {}

        # Calculate averages
        avg_playtime = sum(r.total_playtime for r in reports) / len(reports)
        avg_deaths = sum(r.death_count for r in reports) / len(reports)
        avg_actions = sum(r.action_count for r in reports) / len(reports)

        # Find best and worst
        best_time = min(reports, key=lambda r: r.total_playtime if r.level_completions > 0 else float('inf'))
        most_deaths = max(reports, key=lambda r: r.death_count)

        return {
            "session_count": len(reports),
            "average_playtime": avg_playtime,
            "average_deaths": avg_deaths,
            "average_actions": avg_actions,
            "best_time": {
                "file": str(session_files[reports.index(best_time)]),
                "time": best_time.total_playtime
            } if best_time.level_completions > 0 else None,
            "most_deaths": {
                "file": str(session_files[reports.index(most_deaths)]),
                "count": most_deaths.death_count
            },
            "total_completions": sum(r.level_completions for r in reports)
        }

    def _detect_idle_time(self, actions: List[Dict]) -> float:
        """Detect and calculate total idle time from actions."""
        if not actions:
            return 0.0

        idle_threshold = 10.0  # Seconds of inactivity to consider idle
        idle_time = 0.0
        last_activity_time = None
        idle_start = None

        for action in actions:
            timestamp = action.get("timestamp", 0)
            action_type = action.get("type")
            window_focused = action.get("window_focused", True)

            # Check if action represents activity
            is_activity = (
                action_type in ("movement", "input", "interaction", "death", "level_complete") or
                (action_type == "heartbeat" and window_focused)
            )

            if is_activity and window_focused:
                if last_activity_time is not None:
                    time_since_last = timestamp - last_activity_time
                    if time_since_last > idle_threshold:
                        idle_time += time_since_last
                last_activity_time = timestamp

        # Also check for idle period at the end of session
        if actions and last_activity_time is not None:
            final_time = actions[-1].get("timestamp", 0)
            if final_time - last_activity_time > idle_threshold:
                idle_time += final_time - last_activity_time

        return idle_time

    def _calculate_centroid(self, positions: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate geometric center of positions."""
        if not positions:
            return (0.0, 0.0)
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def generate_full_report(
        self,
        playtest_file: Path,
        output_file: Optional[Path] = None
    ) -> Path:
        """Generate comprehensive analysis report."""
        with open(playtest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        actions = data.get("actions", [])
        duration = data.get("duration", 0)

        report = self.analyze_session(playtest_file)
        heatmap = self.generate_heatmap(playtest_file)
        flow = self.analyze_player_flow(playtest_file)
        idle_time = self._detect_idle_time(actions)

        data = {
            "summary": {
                "total_playtime": duration,
                "active_playtime": duration - idle_time,
                "idle_time": idle_time,
                "idle_percentage": (idle_time / duration * 100) if duration > 0 else 0,
                "actions": report.action_count,
                "deaths": report.death_count,
                "completions": report.level_completions,
                "interactions": report.interactions,
            },
            "heatmap": {
                "resolution": self.heatmap_resolution,
                "cells": len(heatmap),
                "most_active": max(heatmap, key=lambda c: c.intensity).intensity if heatmap else 0
            },
            "flow": flow,
            "insights": self._generate_insights(report, heatmap, flow)
        }

        if output_file is None:
            output_file = playtest_file.with_suffix(".analysis.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return output_file

    def _generate_insights(
        self,
        report: AnalyticsReport,
        heatmap: List[HeatmapCell],
        flow: Dict[str, Any]
    ) -> List[str]:
        """Generate human-readable insights."""
        insights = []

        if report.death_count > 5:
            insights.append(f"High death count ({report.death_count}) suggests difficulty issues")

        if report.level_completions == 0:
            insights.append("Session ended without completion - possible rage quit or soft lock")

        if flow.get("segment_count", 0) > 10:
            insights.append("Many path segments suggest backtracking or confusion")

        if heatmap:
            max_intensity = max(c.intensity for c in heatmap)
            if max_intensity > 0.8:
                insights.append("Strong clustering in one area - check for difficulty spike or interesting feature")

        if report.interactions < 3:
            insights.append("Low interaction count - players may be missing interactive elements")

        return insights
