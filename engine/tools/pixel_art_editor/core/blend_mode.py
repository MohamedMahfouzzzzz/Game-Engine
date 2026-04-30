# /**************************************************************************/
# /*  blend_mode.py                                                         */
# /**************************************************************************/

"""Blend modes for layer compositing (Aseprite-compatible)."""

from enum import IntEnum
from typing import Callable, Tuple


class BlendMode(IntEnum):
    """Layer blend modes.
    
    Uses IntEnum for binary serialization compatibility.
    Values are sequential starting from 0.
    """
    
    NORMAL = 0
    MULTIPLY = 1
    SCREEN = 2
    OVERLAY = 3
    DARKEN = 4
    LIGHTEN = 5
    COLOR_DODGE = 6
    COLOR_BURN = 7
    HARD_LIGHT = 8
    SOFT_LIGHT = 9
    DIFFERENCE = 10
    EXCLUSION = 11
    HSL_HUE = 12
    HSL_SATURATION = 13
    HSL_COLOR = 14
    HSL_LUMINOSITY = 15
    ADDITION = 16
    SUBTRACT = 17
    DIVIDE = 18


def blend_normal(src: Tuple[int, ...], dst: Tuple[int, ...]) -> Tuple[int, ...]:
    """Normal alpha blending."""
    sr, sg, sb, sa = src
    dr, dg, db, da = dst
    
    # Alpha compositing
    alpha = sa + da * (1 - sa / 255)
    if alpha == 0:
        return (0, 0, 0, 0)
    
    # Blend colors
    r = (sr * sa + dr * da * (1 - sa / 255)) / alpha
    g = (sg * sa + dg * da * (1 - sa / 255)) / alpha
    b = (sb * sa + db * da * (1 - sa / 255)) / alpha
    
    return (int(r), int(g), int(b), int(alpha))


def blend_multiply(src: Tuple[int, ...], dst: Tuple[int, ...]) -> Tuple[int, ...]:
    """Multiply blend mode."""
    sr, sg, sb, sa = src
    dr, dg, db, da = dst
    
    r = (sr * dr) // 255
    g = (sg * dg) // 255
    b = (sb * db) // 255
    a = max(sa, da)
    
    return (r, g, b, a)


def blend_screen(src: Tuple[int, ...], dst: Tuple[int, ...]) -> Tuple[int, ...]:
    """Screen blend mode."""
    sr, sg, sb, sa = src
    dr, dg, db, da = dst
    
    r = 255 - ((255 - sr) * (255 - dr)) // 255
    g = 255 - ((255 - sg) * (255 - dg)) // 255
    b = 255 - ((255 - sb) * (255 - db)) // 255
    a = max(sa, da)
    
    return (r, g, b, a)


BLEND_FUNCTIONS: dict[BlendMode, Callable] = {
    BlendMode.NORMAL: blend_normal,
    BlendMode.MULTIPLY: blend_multiply,
    BlendMode.SCREEN: blend_screen,
}


def apply_blend(src: Tuple[int, ...], dst: Tuple[int, ...], mode: BlendMode) -> Tuple[int, ...]:
    """Apply blend mode to two pixels."""
    if mode in BLEND_FUNCTIONS:
        return BLEND_FUNCTIONS[src, dst]
    return blend_normal(src, dst)
