# /**************************************************************************/
# /*  service.py                                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Dict, List

from engine.core.project import Project
from engine.export.build_pipeline import BuildPipeline, ExportProfile

import logging


logger = logging.getLogger(__name__)



SUPPORTED_TARGETS: List[str] = ["windows", "linux", "web", "android"]


class ExportService:
    def __init__(self) -> None:
        self.pipeline = BuildPipeline()

    def export_project(self, project: Project, output_dir: str, target: str, project_file: str | None = None) -> str:
        if target not in SUPPORTED_TARGETS:
            raise ValueError(f"Unsupported target: {target}")
        profile = ExportProfile(target=target, output_name=f"{project.name}_{target}")
        return self.pipeline.build(project.name, output_dir, profile=profile, project_file=project_file)

    def export_all(self, project: Project, output_dir: str, project_file: str | None = None) -> Dict[str, str]:
        return {
            t: self.export_project(project, output_dir, t, project_file=project_file)
            for t in SUPPORTED_TARGETS
        }
