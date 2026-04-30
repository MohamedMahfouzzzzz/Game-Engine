# /**************************************************************************/
# /*  mapping_registry.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from dataclasses import dataclass, field
from typing import Dict

import logging


logger = logging.getLogger(__name__)



@dataclass
class MappingRegistry:
    node_type_map: Dict[str, str] = field(
        default_factory=lambda: {
            "Node": "Node",
            "Node2D": "Node2D",
            "Sprite2D": "Node2D",
            "AnimatedSprite2D": "Node2D",
            "Camera2D": "Node2D",
            "Light2D": "Node2D",
            "Area2D": "Node2D",
            "CollisionShape2D": "Node2D",
            "TileMap": "Node2D",
            "Parallax2D": "Node2D",
            "AnimationPlayer": "Node",
            "Tween": "Node",
            "Label": "Node",
            "Button": "Node",
            "Panel": "Node",
        }
    )
    property_map: Dict[str, str] = field(
        default_factory=lambda: {
            "position": "transform.position",
            "rotation": "transform.rotation",
            "scale": "transform.scale",
            "z_index": "z_index",
            "visible": "visible",
            "modulate": "modulate",
        }
    )
    resource_map: Dict[str, str] = field(default_factory=dict)
    signal_map: Dict[str, str] = field(default_factory=dict)

    def compatibility_report(self) -> Dict[str, int]:
        return {
            "node_types": len(self.node_type_map),
            "properties": len(self.property_map),
            "resources": len(self.resource_map),
            "signals": len(self.signal_map),
        }
