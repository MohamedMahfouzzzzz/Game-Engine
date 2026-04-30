# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Game Engine Editor - Python port of Godot's editor.

This module provides the complete editor interface for the game engine,
including scene editing, project management, asset import, and debugging.

Ported from Godot's C++ editor to Python with PySide6 UI framework.
"""

# Core editor components
from .editor_interface import EditorInterface
from .editor_node import EditorNode
from .project_manager import ProjectManager
from .editor_data import EditorData

# UI components
from .docks import SceneTreeDock, InspectorDock, FileSystemDock

# Scene editing
from .scene import SceneEditor

# Utilities
from .editor_log import EditorLog

__all__ = [
    # Core
    "EditorInterface",
    "EditorNode", 
    "ProjectManager",
    "EditorData",
    
    # UI
    "SceneTreeDock",
    "InspectorDock", 
    "FileSystemDock",
    
    # Scene editing
    "SceneEditor",
    
    # Utilities
    "EditorLog",
]
