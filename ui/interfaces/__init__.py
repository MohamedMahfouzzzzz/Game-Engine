# /**************************************************************************/
# /*  ui/interfaces/__init__.py                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""UI Interfaces - Abstract base classes for UI components.

Following SOLID principles, particularly Interface Segregation Principle (ISP).
Each interface has a single, focused responsibility.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Callable, Any
from engine.core.node_base import Node
from engine.core.scene import Scene


class IViewport(ABC):
    """Interface for viewport widgets.
    
    Responsibility: Display the game scene and handle viewport interactions.
    """
    
    @abstractmethod
    def set_scene(self, scene: Scene) -> None:
        """Set the scene to display."""
        pass
    
    @abstractmethod
    def get_selected_node(self) -> Optional[Node]:
        """Get the currently selected node."""
        pass
    
    @abstractmethod
    def zoom_in(self) -> None:
        """Zoom in the viewport."""
        pass
    
    @abstractmethod
    def zoom_out(self) -> None:
        """Zoom out the viewport."""
        pass
    
    @abstractmethod
    def reset_view(self) -> None:
        """Reset viewport to default view."""
        pass


class ISceneTree(ABC):
    """Interface for scene tree widgets.
    
    Responsibility: Display scene hierarchy and handle node selection.
    """
    
    @abstractmethod
    def set_scene(self, scene: Scene) -> None:
        """Set the scene to display."""
        pass
    
    @abstractmethod
    def select_node(self, node: Node) -> None:
        """Select a node in the tree."""
        pass
    
    @abstractmethod
    def add_node(self, parent: Node, node: Node) -> None:
        """Add a node to the tree."""
        pass
    
    @abstractmethod
    def remove_node(self, node: Node) -> None:
        """Remove a node from the tree."""
        pass
    
    @abstractmethod
    def on_node_selected(self, callback: Callable[[Node], None]) -> None:
        """Register callback for node selection."""
        pass


class IInspector(ABC):
    """Interface for inspector widgets.
    
    Responsibility: Display and edit node properties.
    """
    
    @abstractmethod
    def inspect_node(self, node: Node) -> None:
        """Inspect a node's properties."""
        pass
    
    @abstractmethod
    def clear_inspection(self) -> None:
        """Clear the inspector."""
        pass
    
    @abstractmethod
    def on_property_changed(self, callback: Callable[[str, Any], None]) -> None:
        """Register callback for property changes."""
        pass


class IFileBrowser(ABC):
    """Interface for file browser widgets.
    
    Responsibility: Display and manage project files.
    """
    
    @abstractmethod
    def set_project_root(self, path: str) -> None:
        """Set the project root directory."""
        pass
    
    @abstractmethod
    def refresh(self) -> None:
        """Refresh the file list."""
        pass
    
    @abstractmethod
    def on_file_double_clicked(self, callback: Callable[[str], None]) -> None:
        """Register callback for file double-clicks."""
        pass


class IConsole(ABC):
    """Interface for console widgets.
    
    Responsibility: Display logs and accept commands.
    """
    
    @abstractmethod
    def log(self, message: str, level: str = "info") -> None:
        """Log a message."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear the console."""
        pass
    
    @abstractmethod
    def on_command(self, callback: Callable[[str], None]) -> None:
        """Register callback for command input."""
        pass


class IProfiler(ABC):
    """Interface for profiler widgets.
    
    Responsibility: Display performance metrics.
    """
    
    @abstractmethod
    def update_fps(self, fps: float) -> None:
        """Update FPS display."""
        pass
    
    @abstractmethod
    def update_memory(self, used_mb: float, total_mb: float) -> None:
        """Update memory display."""
        pass
    
    @abstractmethod
    def update_node_count(self, count: int) -> None:
        """Update node count display."""
        pass


__all__ = [
    "IViewport",
    "ISceneTree", 
    "IInspector",
    "IFileBrowser",
    "IConsole",
    "IProfiler",
]
