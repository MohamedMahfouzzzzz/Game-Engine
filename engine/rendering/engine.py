# /**************************************************************************/
# /*  engine.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Compatibility exports for rendering subsystems."""

from engine.rendering.camera import Camera2D
from engine.rendering.light import Light2D, LightType
from engine.rendering.particles import ParticleRenderer
from engine.rendering.renderer2d import Renderer2D
from engine.rendering.shadows import ShadowRenderer

import logging


logger = logging.getLogger(__name__)


__all__ = ["Camera2D", "Light2D", "LightType", "Renderer2D", "ShadowRenderer", "ParticleRenderer"]
