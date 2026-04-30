# /**************************************************************************/
# /*  brushes/__init__.py                                                   */
# /**************************************************************************/

"""Brush presets and brush management.

Provides a collection of pre-defined brushes and utilities
for creating custom brushes.
"""

from .brush_manager import BrushManager
from .brush_presets import BrushPresets
from .pressure_curve import PressureCurve

__all__ = [
    "BrushManager",
    "BrushPresets",
    "PressureCurve",
]
