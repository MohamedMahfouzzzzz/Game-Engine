# /**************************************************************************/
# /*  skeleton2d.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D skeletal animation system."""

from typing import List, Optional, Tuple
from dataclasses import dataclass, field
import math

from engine.core.node_base import Node2D
from engine.core.types import NodeType

import logging

logger = logging.getLogger(__name__)


@dataclass
class BoneTransform:
    """Transform data for a bone."""
    position: Tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0
    scale: Tuple[float, float] = (1.0, 1.0)


class Bone2D(Node2D):
    """A single bone in a skeleton."""

    def __init__(self, name: str = "Bone2D"):
        super().__init__(name)
        self.node_type = NodeType.BONE2D

        self.rest_transform = BoneTransform()
        self.pose_transform = BoneTransform()
        self.length: float = 32.0

        self.parent_bone: Optional["Bone2D"] = None
        self.child_bones: List["Bone2D"] = []

        self.enabled: bool = True
        self.show_gizmo: bool = True

    def set_rest_pose(self, x: float, y: float, rotation: float, length: float) -> None:
        """Set the rest (default) pose."""
        self.rest_transform.position = (x, y)
        self.rest_transform.rotation = rotation
        self.length = length

    def set_pose(self, x: float = None, y: float = None, rotation: float = None,
                 scale_x: float = None, scale_y: float = None) -> None:
        """Set the current pose (relative to rest)."""
        if x is not None:
            self.pose_transform.position = (x, self.pose_transform.position[1])
        if y is not None:
            self.pose_transform.position = (self.pose_transform.position[0], y)
        if rotation is not None:
            self.pose_transform.rotation = rotation
        if scale_x is not None:
            self.pose_transform.scale = (scale_x, self.pose_transform.scale[1])
        if scale_y is not None:
            self.pose_transform.scale = (self.pose_transform.scale[0], scale_y)

    def get_final_position(self) -> Tuple[float, float]:
        """Get final world position including parent transform."""
        local_x = self.rest_transform.position[0] + self.pose_transform.position[0]
        local_y = self.rest_transform.position[1] + self.pose_transform.position[1]

        if self.parent_bone:
            parent_pos = self.parent_bone.get_final_position()
            parent_rot = self.parent_bone.get_final_rotation()

            # Apply parent rotation
            cos_r = math.cos(math.radians(parent_rot))
            sin_r = math.sin(math.radians(parent_rot))
            rot_x = local_x * cos_r - local_y * sin_r
            rot_y = local_x * sin_r + local_y * cos_r

            return (parent_pos[0] + rot_x, parent_pos[1] + rot_y)

        return (local_x, local_y)

    def get_final_rotation(self) -> float:
        """Get final world rotation."""
        local_rot = self.rest_transform.rotation + self.pose_transform.rotation
        if self.parent_bone:
            return self.parent_bone.get_final_rotation() + local_rot
        return local_rot

    def get_final_scale(self) -> Tuple[float, float]:
        """Get final world scale."""
        local_scale = (
            self.rest_transform.scale[0] * self.pose_transform.scale[0],
            self.rest_transform.scale[1] * self.pose_transform.scale[1]
        )
        if self.parent_bone:
            parent_scale = self.parent_bone.get_final_scale()
            return (parent_scale[0] * local_scale[0], parent_scale[1] * local_scale[1])
        return local_scale

    def get_tip_position(self) -> Tuple[float, float]:
        """Get the tip/end position of the bone."""
        pos = self.get_final_position()
        rot = math.radians(self.get_final_rotation())
        return (
            pos[0] + math.cos(rot) * self.length,
            pos[1] + math.sin(rot) * self.length
        )

    def add_child_bone(self, bone: "Bone2D") -> None:
        """Add a child bone."""
        bone.parent_bone = self
        self.child_bones.append(bone)

    def remove_child_bone(self, bone: "Bone2D") -> None:
        """Remove a child bone."""
        if bone in self.child_bones:
            self.child_bones.remove(bone)
            bone.parent_bone = None

    def reset_to_rest(self) -> None:
        """Reset pose to rest pose."""
        self.pose_transform = BoneTransform()

    def look_at(self, target_x: float, target_y: float) -> None:
        """Rotate bone to look at target position."""
        pos = self.get_final_position()
        dx = target_x - pos[0]
        dy = target_y - pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        self.set_pose(rotation=angle - self.rest_transform.rotation)


class Skeleton2D(Node2D):
    """Container for a skeleton of bones."""

    def __init__(self, name: str = "Skeleton2D"):
        super().__init__(name)
        self.node_type = NodeType.SKELETON2D

        self.bones: List[Bone2D] = []
        self.root_bones: List[Bone2D] = []

        self.show_bones: bool = True
        self.bone_color: Tuple[int, int, int, int] = (0, 255, 255, 255)

    def add_bone(self, bone: Bone2D, parent: Optional[Bone2D] = None) -> None:
        """Add a bone to the skeleton."""
        self.bones.append(bone)

        if parent:
            parent.add_child_bone(bone)
        else:
            self.root_bones.append(bone)

    def remove_bone(self, bone: Bone2D) -> None:
        """Remove a bone from the skeleton."""
        if bone in self.bones:
            self.bones.remove(bone)

            # Remove from parent's children
            if bone.parent_bone:
                bone.parent_bone.remove_child_bone(bone)
            elif bone in self.root_bones:
                self.root_bones.remove(bone)

            # Orphan children
            for child in bone.child_bones:
                child.parent_bone = None
                self.root_bones.append(child)

    def get_bone(self, name: str) -> Optional[Bone2D]:
        """Get bone by name."""
        for bone in self.bones:
            if bone.name == name:
                return bone
        return None

    def reset_all_bones(self) -> None:
        """Reset all bones to rest pose."""
        for bone in self.bones:
            bone.reset_to_rest()

    def get_bone_chain(self, bone: Bone2D) -> List[Bone2D]:
        """Get chain of bones from root to this bone."""
        chain = []
        current = bone

        while current:
            chain.insert(0, current)
            current = current.parent_bone

        return chain

    def apply_ik(self, target_bone: Bone2D, target_x: float, target_y: float,
                  iterations: int = 10) -> bool:
        """Apply inverse kinematics to reach target."""
        # Simple CCD IK implementation
        chain = self.get_bone_chain(target_bone)

        if len(chain) < 2:
            return False

        for _ in range(iterations):
            # Iterate backwards through chain
            for i in range(len(chain) - 1, -1, -1):
                bone = chain[i]
                tip = bone.get_tip_position()

                # Calculate angle to target
                pos = bone.get_final_position()
                dx = target_x - pos[0]
                dy = target_y - pos[1]
                target_angle = math.degrees(math.atan2(dy, dx))

                tip_dx = tip[0] - pos[0]
                tip_dy = tip[1] - pos[1]
                tip_angle = math.degrees(math.atan2(tip_dy, tip_dx))

                # Adjust rotation
                delta = target_angle - tip_angle
                bone.set_pose(rotation=bone.pose_transform.rotation + delta)

        return True

    def to_dict(self) -> dict:
        """Serialize skeleton."""
        return {
            "bones": [
                {
                    "name": b.name,
                    "parent": b.parent_bone.name if b.parent_bone else None,
                    "rest": {
                        "position": b.rest_transform.position,
                        "rotation": b.rest_transform.rotation,
                        "scale": b.rest_transform.scale,
                        "length": b.length
                    }
                }
                for b in self.bones
            ]
        }
