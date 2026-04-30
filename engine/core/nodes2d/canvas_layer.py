# /**************************************************************************/
# /*  nodes2d/canvas_layer.py                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""CanvasLayer - Layered 2D rendering context."""

from __future__ import annotations

from .node2d import Node2D
from .types import Vector2

import logging


logger = logging.getLogger(__name__)



class CanvasLayer(Node2D):
    """Layer for organizing 2D rendering.
    
    Use CanvasLayer to:
        - Separate background, game world, foreground, UI
        - Apply different transforms to layers
        - Control parallax scrolling
        - Manage layer visibility
    
    Properties:
        layer_value: Rendering order, higher = on top
        follow_viewport: Whether to move with camera
        follow_viewport_scale: Parallax scale (0-1)
        offset: Additional position offset
        rotation: Layer rotation
        scale_value: Layer scale
    
    Signals:
        layer_changed: When layer order changes
    """
    
    __slots__ = [
        "layer_value", "offset", "rotation", "scale_value",
        "follow_viewport", "follow_viewport_scale"
    ]
    
    _SIGNALS = ["layer_changed"]
    
    def __init__(self, name: str = "CanvasLayer"):
        super().__init__(name)
        
        self.layer_value = 1
        self.offset = Vector2(0, 0)
        self.rotation = 0.0
        self.scale_value = Vector2(1, 1)
        
        self.follow_viewport = False
        self.follow_viewport_scale = 1.0
    
    def set_layer(self, layer: int) -> None:
        """Set layer order."""
        if layer != self.layer_value:
            self.layer_value = layer
            self.signals.emit("layer_changed", layer)
