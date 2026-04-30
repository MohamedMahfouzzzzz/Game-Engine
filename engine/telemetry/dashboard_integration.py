# /**************************************************************************/
# /*  dashboard_integration.py                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Integration with external telemetry dashboard."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import logging

logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """Configuration for dashboard integration."""
    dashboard_url: str = ""
    project_id: str = ""
    api_key: str = ""
    refresh_interval: int = 300  # seconds


class DashboardIntegration:
    """Integrates with external telemetry dashboard."""

    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()
        self._last_update: float = 0

    def generate_dashboard_link(self, report_type: str = "overview") -> str:
        """Generate link to view project on dashboard."""
        if not self.config.dashboard_url:
            return ""

        return f"{self.config.dashboard_url}/projects/{self.config.project_id}/{report_type}"

    def prepare_summary_data(
        self,
        session_files: List[Path]
    ) -> Dict[str, Any]:
        """Prepare summary data for dashboard upload."""
        from telemetry.analyzer import TelemetryAnalyzer

        analyzer = TelemetryAnalyzer()
        comparison = analyzer.compare_sessions(session_files)

        return {
            "project_id": self.config.project_id,
            "timestamp": comparison.get("timestamp", 0),
            "summary": {
                "total_sessions": comparison.get("session_count", 0),
                "average_playtime": comparison.get("average_playtime", 0),
                "average_deaths": comparison.get("average_deaths", 0),
                "total_completions": comparison.get("total_completions", 0)
            },
            "highlights": {
                "best_time": comparison.get("best_time"),
                "most_deaths": comparison.get("most_deaths")
            }
        }

    def export_for_dashboard(
        self,
        session_files: List[Path],
        output_file: Path
    ) -> None:
        """Export data in dashboard-compatible format."""
        data = self.prepare_summary_data(session_files)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def generate_embed_code(self, report_type: str = "heatmap") -> str:
        """Generate HTML embed code for dashboard widget."""
        if not self.config.dashboard_url:
            return ""

        url = f"{self.config.dashboard_url}/embed/{self.config.project_id}/{report_type}"

        return f'''
<iframe
    src="{url}"
    width="100%"
    height="600"
    frameborder="0"
    allowfullscreen
></iframe>
'''.strip()

    def validate_connection(self) -> bool:
        """Validate dashboard connection."""
        if not self.config.dashboard_url or not self.config.api_key:
            return False

        # Placeholder - actual implementation would ping the dashboard API
        return True

    def get_available_reports(self) -> List[str]:
        """Get list of available report types."""
        return [
            "overview",
            "heatmap",
            "player_flow",
            "glitches",
            "performance",
            "comparisons"
        ]
