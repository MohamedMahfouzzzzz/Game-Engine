# /**************************************************************************/
# /*  remote_transform.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Remote transform node for mirroring transform to another node."""

from typing import Optional
from engine.core.nodes2d import Node2D, Vector2


class RemoteTransform2D(Node2D):
    """Copies this node's transform to a remote node.
    
    Useful for:
    - Camera following player
    - UI elements tracking world objects
    - Synchronizing transforms between scenes
    """
    
    def __init__(self, name: str = "RemoteTransform2D"):
        super().__init__(name)
        self._remote_path: str = ""
        self._use_global_coordinates: bool = True
        self._update_scale: bool = True
        self._update_rotation: bool = True
        self._update_position: bool = True
        self._remote_node: Optional[Node2D] = None
    
    def set_remote_node(self, path: str) -> None:
        """Set path to node that receives transform."""
        self._remote_path = path
    
    def get_remote_node(self) -> str:
        return self._remote_path
    
    def set_use_global_coordinates(self, use_global: bool) -> None:
        """Use global or local coordinates."""
        self._use_global_coordinates = use_global
    
    def is_using_global_coordinates(self) -> bool:
        return self._use_global_coordinates
    
    def set_update_position(self, update: bool) -> None:
        """Update remote position."""
        self._update_position = update
    
    def get_update_position(self) -> bool:
        return self._update_position
    
    def set_update_rotation(self, update: bool) -> None:
        """Update remote rotation."""
        self._update_rotation = update
    
    def get_update_rotation(self) -> bool:
        return self._update_rotation
    
    def set_update_scale(self, update: bool) -> None:
        """Update remote scale."""
        self._update_scale = update
    
    def get_update_scale(self) -> bool:
        return self._update_scale
    
    def force_update_cache(self) -> None:
        """Force refresh of remote node reference."""
        pass
    
    def _update_remote(self) -> None:
        """Apply transform to remote node."""
        if not self._remote_node:
            return
        
        if self._use_global_coordinates:
            if self._update_position:
                self._remote_node.position = self.position
            if self._update_rotation:
                self._remote_node.rotation = self.rotation
            if self._update_scale:
                self._remote_node.scale = self.scale
    
    def __repr__(self) -> str:
        return f"RemoteTransform2D('{self.name}', remote='{self._remote_path}')"
