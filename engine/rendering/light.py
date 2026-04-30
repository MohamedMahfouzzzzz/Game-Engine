# /**************************************************************************/
# /*  light.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from dataclasses import dataclass
from enum import Enum
from typing import Tuple
import math

import logging


logger = logging.getLogger(__name__)



class LightType(Enum):
    DIRECTIONAL = "Directional"
    POINT = "Point"
    SPOT = "Spot"
    AREA = "Area"


@dataclass
class Light2D:
    position: Tuple[float, float]
    color: Tuple[int, int, int]
    intensity: float
    range: float
    light_type: LightType = LightType.POINT

    def get_influence(self, point: Tuple[float, float]) -> float:
        dx = point[0] - self.position[0]
        dy = point[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > self.range:
            return 0.0
        return self.intensity * (1.0 - distance / self.range)
