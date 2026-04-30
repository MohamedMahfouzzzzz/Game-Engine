# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Editor dock widgets - Python port of Godot's dock system.

Provides all dock widgets for the editor including:
- Scene tree dock
- Inspector dock  
- File system dock
- Asset library dock
- Debugger dock
"""

from .scene_tree_dock import SceneTreeDock
from .inspector_dock import InspectorDock
from .file_system_dock import FileSystemDock

__all__ = [
    "SceneTreeDock",
    "InspectorDock", 
    "FileSystemDock",
]
