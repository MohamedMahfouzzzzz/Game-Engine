# /**************************************************************************/
# /*  particles.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Dict, List, Tuple

from PySide6.QtGui import QColor, QPainter

from engine.rendering.renderer2d import Renderer2D

import logging


logger = logging.getLogger(__name__)


MAX_PARTICLES = 10000


class ParticleRenderer:
    def __init__(self, renderer: Renderer2D):
        self.renderer = renderer
        self.particles: List[Dict] = []

    def add_particle(
        self,
        position: Tuple[float, float],
        velocity: Tuple[float, float],
        lifetime: float,
        color: Tuple[int, int, int],
    ) -> None:
        if len(self.particles) >= MAX_PARTICLES:
            self.particles.pop(0)
        self.particles.append(
            {
                "position": position,
                "velocity": velocity,
                "lifetime": lifetime,
                "max_lifetime": lifetime,
                "color": color,
            }
        )

    def update(self, delta_time: float) -> None:
        # Update all particles
        for particle in self.particles:
            particle["lifetime"] -= delta_time
            particle["position"] = (
                particle["position"][0] + particle["velocity"][0] * delta_time,
                particle["position"][1] + particle["velocity"][1] * delta_time,
            )
        # O(n) removal using list comprehension instead of O(n²) with remove()
        self.particles = [p for p in self.particles if p["lifetime"] > 0]

    def render(self, painter: QPainter) -> None:
        for particle in self.particles:
            alpha = int(255 * (particle["lifetime"] / particle["max_lifetime"]))
            color = QColor(*particle["color"], alpha)
            screen_x, screen_y = self.renderer._world_to_screen(particle["position"])
            painter.fillRect(int(screen_x), int(screen_y), 2, 2, color)
