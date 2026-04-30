# /**************************************************************************/
# /*  skeleton_2d.py                                                        */
# /**************************************************************************/

"""Godot Skeleton2D port - 2D skeleton for animation."""

from typing import List, Optional, Dict
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2


class Bone2D(Node2D):
    """Single bone in a 2D skeleton."""
    
    def __init__(self, name: str = "Bone2D"):
        super().__init__(name)
        self._rest_transform: any = None
        self._default_length: float = 10.0
        self._auto_calculate_length: bool = True
        self._enabled: bool = True
        self._bone_idx: int = -1
        self._children: List['Bone2D'] = []
        self._parent_bone: Optional['Bone2D'] = None
    
    def set_rest(self, rest: any) -> None:
        self._rest_transform = rest
    
    def get_rest(self) -> any:
        return self._rest_transform
    
    def apply_rest(self) -> None:
        pass
    
    def get_index(self) -> int:
        return self._bone_idx
    
    def get_skeleton(self) -> Optional['Skeleton2D']:
        parent = self.parent
        while parent:
            if isinstance(parent, Skeleton2D):
                return parent
            parent = parent.parent
        return None
    
    def set_default_length(self, length: float) -> None:
        self._default_length = max(0.01, length)
    
    def get_default_length(self) -> float:
        return self._default_length
    
    def set_autocalculate_length(self, enabled: bool) -> None:
        self._auto_calculate_length = enabled
    
    def is_autocalculate_length_enabled(self) -> bool:
        return self._auto_calculate_length
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def __repr__(self) -> str:
        return f"Bone2D('{self.name}', idx={self._bone_idx}, enabled={self._enabled})"


class Skeleton2D(Node2D):
    """2D skeleton container."""
    
    def __init__(self, name: str = "Skeleton2D"):
        super().__init__(name)
        self._bones: List[Bone2D] = []
        self._bone_setup_dirty: bool = False
    
    def add_bone(self, bone: Bone2D) -> None:
        self._bones.append(bone)
        bone._bone_idx = len(self._bones) - 1
        if bone not in self.children:
            self.add_child(bone)
    
    def get_bone(self, idx: int) -> Optional[Bone2D]:
        if 0 <= idx < len(self._bones):
            return self._bones[idx]
        return None
    
    def get_bone_count(self) -> int:
        return len(self._bones)
    
    def get_skeleton(self) -> 'Skeleton2D':
        return self
    
    def local_pose_to_global_pose(self, bone_idx: int, local_pose: any) -> any:
        return local_pose
    
    def global_pose_to_local_pose(self, bone_idx: int, global_pose: any) -> any:
        return global_pose
    
    def set_bone_local_pose_override(self, bone_idx: int, override: any, strength: float, persistent: bool) -> None:
        pass
    
    def get_bone_local_pose_override(self, bone_idx: int) -> any:
        return None
    
    def clear_bones_local_pose_override(self) -> None:
        pass
    
    def __repr__(self) -> str:
        return f"Skeleton2D('{self.name}', bones={len(self._bones)})"
