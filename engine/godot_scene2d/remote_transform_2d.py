# /**************************************************************************/
# /*  remote_transform_2d.py                                                */
# /**************************************************************************/

"""Godot RemoteTransform2D port - Remote transform synchronization."""

from typing import Optional
from engine.core.nodes2d import Node2D


class RemoteTransform2D(Node2D):
    """Synchronizes transform to a remote node.
    
    Updates the transform of another node to match this one.
    """
    
    def __init__(self, name: str = "RemoteTransform2D"):
        super().__init__(name)
        self._remote_node: Optional[Node2D] = None
        self._remote_node_path: str = ""
        self._update_position: bool = True
        self._update_rotation: bool = True
        self._update_scale: bool = True
        self._use_global_coordinates: bool = True
    
    def set_remote_node(self, node: Optional[Node2D]) -> None:
        """Set the remote node to update."""
        self._remote_node = node
    
    def get_remote_node(self) -> Optional[Node2D]:
        """Get the remote node."""
        return self._remote_node
    
    def set_remote_node_path(self, path: str) -> None:
        """Set path to remote node."""
        self._remote_node_path = path
    
    def get_remote_node_path(self) -> str:
        """Get path to remote node."""
        return self._remote_node_path
    
    def set_update_position(self, update: bool) -> None:
        """Enable position updates."""
        self._update_position = update
    
    def get_update_position(self) -> bool:
        """Check if position updates enabled."""
        return self._update_position
    
    def set_update_rotation(self, update: bool) -> None:
        """Enable rotation updates."""
        self._update_rotation = update
    
    def get_update_rotation(self) -> bool:
        """Check if rotation updates enabled."""
        return self._update_rotation
    
    def set_update_scale(self, update: bool) -> None:
        """Enable scale updates."""
        self._update_scale = update
    
    def get_update_scale(self) -> bool:
        """Check if scale updates enabled."""
        return self._update_scale
    
    def set_use_global_coordinates(self, use_global: bool) -> None:
        """Use global coordinates for updates."""
        self._use_global_coordinates = use_global
    
    def get_use_global_coordinates(self) -> bool:
        """Check if using global coordinates."""
        return self._use_global_coordinates
    
    def force_update_cache(self) -> None:
        """Force update of remote node cache."""
        pass
    
    def __repr__(self) -> str:
        return f"RemoteTransform2D('{self.name}', remote={self._remote_node is not None}, pos={self._update_position}, rot={self._update_rotation}, scale={self._update_scale})"
