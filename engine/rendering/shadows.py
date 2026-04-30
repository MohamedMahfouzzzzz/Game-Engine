# /**************************************************************************/
# /*  shadows.py                                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import List, Optional

from PySide6.QtGui import QColor, QPainter

from engine.rendering.light import Light2D
from engine.rendering.renderer2d import Renderer2D

import logging


logger = logging.getLogger(__name__)



class ShadowRenderer:
    def __init__(self, renderer: Renderer2D):
        self.renderer = renderer
        self.shadow_quality = 2

    def render_shadows(self, painter: QPainter, light: Light2D, occluders: List) -> None:
        painter.setPen(QColor(0, 0, 0, 100))
        for occluder in occluders:
            shadow_points = self._calculate_shadow(light, occluder)
            if shadow_points:
                painter.fillPolygon(shadow_points)

    def _calculate_shadow(self, light: Light2D, occluder) -> Optional[List]:
        return None
