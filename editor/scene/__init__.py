# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Scene editing components - Python port of Godot's scene editing system.

Provides scene editing functionality including:
- Scene editor widget with viewport
- Node editing tools
- Viewport rendering and gizmos
"""

from .scene_editor import SceneEditor

__all__ = [
    "SceneEditor",
]
