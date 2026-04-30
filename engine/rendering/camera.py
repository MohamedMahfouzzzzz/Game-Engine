# /**************************************************************************/
# /*  camera.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Optional, Tuple

import logging


logger = logging.getLogger(__name__)



class Camera2D:
    def __init__(self, width: int = 800, height: int = 600):
        self.position: Tuple[float, float] = (0.0, 0.0)
        self.zoom: float = 1.0
        self.rotation: float = 0.0
        self.width = width
        self.height = height
        self.smoothing: float = 0.1
        self.target_position: Optional[Tuple[float, float]] = None

    def set_position(self, x: float, y: float) -> None:
        self.position = (x, y)

    def follow_target(self, target_pos: Tuple[float, float]) -> None:
        current_x, current_y = self.position
        target_x, target_y = target_pos
        self.position = (
            current_x + (target_x - current_x) * self.smoothing,
            current_y + (target_y - current_y) * self.smoothing,
        )

    def get_view_rect(self) -> Tuple[float, float, float, float]:
        half_width = (self.width / 2) / self.zoom
        half_height = (self.height / 2) / self.zoom
        x = self.position[0] - half_width
        y = self.position[1] - half_height
        return (x, y, self.width / self.zoom, self.height / self.zoom)
