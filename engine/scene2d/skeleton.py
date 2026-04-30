# /**************************************************************************/
# /*  skeleton.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D skeletal animation system."""

import math
from typing import List, Optional, Tuple
from engine.core.nodes2d import Node2D, Vector2


class BoneTransform:
    """Transform data for a bone."""
    
    def __init__(self):
        self.position: Vector2 = Vector2()
        self.rotation: float = 0.0
        self.scale: Vector2 = Vector2(1.0, 1.0)


class Bone2D(Node2D):
    """A single bone in a skeleton hierarchy.
    
    Supports:
    - Parent/child bone relationships
    - Rest and pose transforms
    - Inverse kinematics (IK) targets
    """
    
    def __init__(self, name: str = "Bone2D"):
        super().__init__(name)
        self._rest_transform = BoneTransform()
        self._pose_transform = BoneTransform()
        self._length: float = 32.0
        
        self._parent_bone: Optional["Bone2D"] = None
        self._child_bones: List["Bone2D"] = []
        
        self._enabled: bool = True
        self._show_gizmo: bool = True
        
        self._ik_target: Optional[Node2D] = None
        self._ik_auto_calculate: bool = False
        self._ik_limit_top: float = -90.0
        self._ik_limit_bottom: float = 90.0
    
    def set_rest_pose(self, position: Vector2, rotation: float, length: float) -> None:
        """Set the rest (default) pose."""
        self._rest_transform.position = position
        self._rest_transform.rotation = rotation
        self._length = length
    
    def set_pose(self, position: Vector2 = None, rotation: float = None,
                 scale: Vector2 = None) -> None:
        """Set the current pose (relative to rest)."""
        if position:
            self._pose_transform.position = position
        if rotation is not None:
            self._pose_transform.rotation = rotation
        if scale:
            self._pose_transform.scale = scale
    
    def get_final_position(self) -> Vector2:
        """Get final world position including parent transform."""
        local_x = self._rest_transform.position.x + self._pose_transform.position.x
        local_y = self._rest_transform.position.y + self._pose_transform.position.y
        
        if self._parent_bone:
            parent_pos = self._parent_bone.get_final_position()
            parent_rot = math.radians(self._parent_bone.get_final_rotation())
            
            cos_r = math.cos(parent_rot)
            sin_r = math.sin(parent_rot)
            rot_x = local_x * cos_r - local_y * sin_r
            rot_y = local_x * sin_r + local_y * cos_r
            
            return Vector2(parent_pos.x + rot_x, parent_pos.y + rot_y)
        
        return Vector2(local_x, local_y)
    
    def get_final_rotation(self) -> float:
        """Get final world rotation in degrees."""
        local_rot = self._rest_transform.rotation + self._pose_transform.rotation
        if self._parent_bone:
            return self._parent_bone.get_final_rotation() + local_rot
        return local_rot
    
    def get_final_scale(self) -> Vector2:
        """Get final world scale."""
        local_scale = Vector2(
            self._rest_transform.scale.x * self._pose_transform.scale.x,
            self._rest_transform.scale.y * self._pose_transform.scale.y
        )
        if self._parent_bone:
            parent_scale = self._parent_bone.get_final_scale()
            return Vector2(parent_scale.x * local_scale.x, parent_scale.y * local_scale.y)
        return local_scale
    
    def get_tip_position(self) -> Vector2:
        """Get the tip/end position of the bone."""
        pos = self.get_final_position()
        rot = math.radians(self.get_final_rotation())
        return Vector2(
            pos.x + math.cos(rot) * self._length,
            pos.y + math.sin(rot) * self._length
        )
    
    def add_child_bone(self, bone: "Bone2D") -> None:
        """Add a child bone."""
        bone._parent_bone = self
        self._child_bones.append(bone)
    
    def remove_child_bone(self, bone: "Bone2D") -> None:
        """Remove a child bone."""
        if bone in self._child_bones:
            self._child_bones.remove(bone)
            bone._parent_bone = None
    
    def reset_to_rest(self) -> None:
        """Reset pose to rest pose."""
        self._pose_transform = BoneTransform()
    
    def look_at(self, target: Vector2) -> None:
        """Rotate bone to look at target position."""
        pos = self.get_final_position()
        dx = target.x - pos.x
        dy = target.y - pos.y
        angle = math.degrees(math.atan2(dy, dx))
        self._pose_transform.rotation = angle - self._rest_transform.rotation
    
    def apply_ik(self, target: Vector2, iterations: int = 10) -> bool:
        """Apply inverse kinematics to reach target."""
        chain = self._get_bone_chain()
        if len(chain) < 2:
            return False
        
        for _ in range(iterations):
            for bone in reversed(chain):
                tip = bone.get_tip_position()
                pos = bone.get_final_position()
                
                # Calculate angles
                target_dx = target.x - pos.x
                target_dy = target.y - pos.y
                target_angle = math.degrees(math.atan2(target_dy, target_dx))
                
                tip_dx = tip.x - pos.x
                tip_dy = tip.y - pos.y
                tip_angle = math.degrees(math.atan2(tip_dy, tip_dx))
                
                # Adjust rotation
                delta = target_angle - tip_angle
                bone._pose_transform.rotation += delta
        
        return True
    
    def _get_bone_chain(self) -> List["Bone2D"]:
        """Get chain of bones from root to this bone."""
        chain = []
        current = self
        while current:
            chain.insert(0, current)
            current = current._parent_bone
        return chain
    
    def __repr__(self) -> str:
        return f"Bone2D('{self.name}', length={self._length})"


class Skeleton2D(Node2D):
    """Container for a skeleton of bones.
    
    Manages bone hierarchy and IK calculations.
    """
    
    def __init__(self, name: str = "Skeleton2D"):
        super().__init__(name)
        self._bones: List[Bone2D] = []
        self._root_bones: List[Bone2D] = []
        self._show_bones: bool = True
        self._bone_color: Color = (0, 255, 255, 255)
    
    def add_bone(self, bone: Bone2D, parent: Optional[Bone2D] = None) -> None:
        """Add a bone to the skeleton."""
        self._bones.append(bone)
        
        if parent:
            parent.add_child_bone(bone)
        else:
            self._root_bones.append(bone)
    
    def remove_bone(self, bone: Bone2D) -> None:
        """Remove a bone from the skeleton."""
        if bone in self._bones:
            self._bones.remove(bone)
            
            # Remove from parent's children
            if bone._parent_bone:
                bone._parent_bone.remove_child_bone(bone)
            elif bone in self._root_bones:
                self._root_bones.remove(bone)
            
            # Orphan children
            for child in bone._child_bones:
                child._parent_bone = None
                self._root_bones.append(child)
    
    def get_bone(self, name: str) -> Optional[Bone2D]:
        """Get bone by name."""
        for bone in self._bones:
            if bone.name == name:
                return bone
        return None
    
    def reset_all_bones(self) -> None:
        """Reset all bones to rest pose."""
        for bone in self._bones:
            bone.reset_to_rest()
    
    def __repr__(self) -> str:
        return f"Skeleton2D('{self.name}', bones={len(self._bones)})"


class SkeletonModificationStack2D:
    """Stack of modifications applied to skeleton."""
    
    def __init__(self):
        self._enabled: bool = True
        self._strength: float = 1.0
        self._modifications: list = []
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_strength(self, strength: float) -> None:
        self._strength = max(0.0, min(1.0, strength))
    
    def get_strength(self) -> float:
        return self._strength
