# /**************************************************************************/
# /*  node_registry.py                                                      */
# /**************************************************************************/

"""Node type registry for engine internal use."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto

import logging



logger = logging.getLogger(__name__)

class NodeCategory(Enum):
    """Categories for organizing node types."""
    BASE = "Base Nodes"
    VISUAL = "Visual Nodes"
    PHYSICS = "Physics Nodes"
    UI = "UI Nodes"
    AUDIO = "Audio Nodes"
    INPUT = "Input Nodes"
    EFFECTS = "Effects & Particles"
    UTILITY = "Utility Nodes"


@dataclass
class NodeProperty:
    """Documentation for a node property."""
    name: str
    type_name: str
    default_value: Any
    description: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class NodeMethod:
    """Documentation for a node method."""
    name: str
    signature: str
    description: str
    example: str = ""


@dataclass
class NodeTypeDoc:
    """Complete documentation for a node type."""
    type_name: str
    category: NodeCategory
    icon: str
    description: str
    brief: str
    properties: List[NodeProperty] = field(default_factory=list)
    methods: List[NodeMethod] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)
    parent_types: List[str] = field(default_factory=list)
    example_code: str = ""
    use_cases: List[str] = field(default_factory=list)


class NodeTypesRegistry:
    """Registry of all documented node types."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._nodes: Dict[str, NodeTypeDoc] = {}
            cls._instance._register_default_nodes()
        return cls._instance
    
    def _register_default_nodes(self) -> None:
        """Register built-in node types."""
        # Base nodes
        self.register(NodeTypeDoc(
            type_name="Node",
            category=NodeCategory.BASE,
            icon="📦",
            brief="Base node class",
            description="The base class for all nodes in the engine.",
            properties=[
                NodeProperty("name", "String", "Node", "Node name"),
                NodeProperty("visible", "bool", True, "Visibility"),
            ],
            methods=[],
            signals=["child_entered_tree", "child_exited_tree"],
            parent_types=[],
            example_code="node = Node(\"MyNode\")",
            use_cases=["Base for all nodes"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="Node2D",
            category=NodeCategory.BASE,
            icon="📍",
            brief="2D base node",
            description="Base class for all 2D nodes with position, rotation and scale.",
            properties=[
                NodeProperty("position", "Vector2", "(0, 0)", "Position in 2D space"),
                NodeProperty("rotation", "float", 0.0, "Rotation in degrees"),
                NodeProperty("scale", "Vector2", "(1, 1)", "Scale factor"),
            ],
            methods=[],
            signals=[],
            parent_types=["Node"],
            example_code="node = Node2D()\nnode.position = Vector2(100, 200)",
            use_cases=["2D game objects"]
        ))
        
        # Visual nodes
        self.register(NodeTypeDoc(
            type_name="Sprite2D",
            category=NodeCategory.VISUAL,
            icon="🖼️",
            brief="2D sprite node",
            description="Displays a 2D texture.",
            properties=[
                NodeProperty("texture", "Texture2D", None, "Texture to display"),
                NodeProperty("flip_h", "bool", False, "Flip horizontally"),
                NodeProperty("flip_v", "bool", False, "Flip vertically"),
            ],
            methods=[],
            signals=[],
            parent_types=["Node2D"],
            example_code="sprite = Sprite2D()\nsprite.texture = load_texture(\"player.png\")",
            use_cases=["Characters", "Backgrounds", "UI elements"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="AnimatedSprite2D",
            category=NodeCategory.VISUAL,
            icon="🎬",
            brief="Animated sprite",
            description="Sprite with frame-based animation support.",
            properties=[
                NodeProperty("sprite_frames", "SpriteFrames", None, "Animation frames"),
                NodeProperty("animation", "String", "\"default\"", "Current animation"),
                NodeProperty("frame", "int", 0, "Current frame"),
                NodeProperty("playing", "bool", True, "Is playing"),
            ],
            methods=[
                NodeMethod("play", "play(animation)", "Play animation", "play(\"run\")"),
                NodeMethod("stop", "stop()", "Stop animation"),
            ],
            signals=["animation_finished", "frame_changed"],
            parent_types=["Node2D"],
            example_code="anim = AnimatedSprite2D()\nanim.play(\"walk\")",
            use_cases=["Animated characters", "Effects"]
        ))
        
        # Physics nodes
        self.register(NodeTypeDoc(
            type_name="CharacterBody2D",
            category=NodeCategory.PHYSICS,
            icon="🏃",
            brief="Character controller",
            description="Kinematic body for player-controlled characters.",
            properties=[
                NodeProperty("velocity", "Vector2", "(0, 0)", "Current velocity"),
                NodeProperty("floor_max_angle", "float", 45.0, "Max floor angle"),
            ],
            methods=[
                NodeMethod("move_and_slide", "move_and_slide()", "Move with collision"),
                NodeMethod("is_on_floor", "is_on_floor() -> bool", "Check if on floor"),
            ],
            signals=[],
            parent_types=["Node2D"],
            example_code="player = CharacterBody2D()\nplayer.move_and_slide()",
            use_cases=["Player characters", "NPCs"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="RigidBody2D",
            category=NodeCategory.PHYSICS,
            icon="⚖️",
            brief="Dynamic physics body",
            description="Body affected by physics simulation.",
            properties=[
                NodeProperty("mass", "float", 1.0, "Body mass"),
                NodeProperty("gravity_scale", "float", 1.0, "Gravity multiplier"),
                NodeProperty("linear_velocity", "Vector2", "(0, 0)", "Linear velocity"),
            ],
            methods=[
                NodeMethod("apply_force", "apply_force(force)", "Apply force"),
                NodeMethod("apply_impulse", "apply_impulse(impulse)", "Apply impulse"),
            ],
            signals=["body_entered", "body_exited"],
            parent_types=["Node2D"],
            example_code="body = RigidBody2D()\nbody.apply_impulse(Vector2(100, 0))",
            use_cases=["Physics objects", "Projectiles"]
        ))
        
        # UI nodes
        self.register(NodeTypeDoc(
            type_name="Control",
            category=NodeCategory.UI,
            icon="🎛️",
            brief="Base UI control",
            description="Base class for all UI controls.",
            properties=[
                NodeProperty("anchor_left", "float", 0.0, "Left anchor"),
                NodeProperty("anchor_right", "float", 0.0, "Right anchor"),
                NodeProperty("margin_left", "int", 0, "Left margin"),
                NodeProperty("margin_right", "int", 0, "Right margin"),
            ],
            methods=[],
            signals=["resized", "focus_entered", "focus_exited"],
            parent_types=["Node"],
            example_code="control = Control()",
            use_cases=["UI elements"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="Button",
            category=NodeCategory.UI,
            icon="🔘",
            brief="Button control",
            description="Clickable button with text.",
            properties=[
                NodeProperty("text", "String", "\"Button\"", "Button text"),
                NodeProperty("disabled", "bool", False, "Is disabled"),
            ],
            methods=[],
            signals=["pressed", "button_down", "button_up"],
            parent_types=["Control"],
            example_code="btn = Button(\"Click Me\")\nbtn.connect(\"pressed\", on_click)",
            use_cases=["UI buttons", "Menu items"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="Label",
            category=NodeCategory.UI,
            icon="🏷️",
            brief="Text label",
            description="Displays text.",
            properties=[
                NodeProperty("text", "String", "\"\"", "Label text"),
                NodeProperty("align", "int", 0, "Text alignment"),
            ],
            methods=[],
            signals=[],
            parent_types=["Control"],
            example_code="label = Label(\"Score: 0\")",
            use_cases=["Text display", "Scores", "UI labels"]
        ))
        
        # Audio nodes
        self.register(NodeTypeDoc(
            type_name="AudioStreamPlayer2D",
            category=NodeCategory.AUDIO,
            icon="🔊",
            brief="2D positional audio",
            description="Plays audio with 2D positioning.",
            properties=[
                NodeProperty("stream", "AudioStream", None, "Audio stream"),
                NodeProperty("volume_db", "float", 0.0, "Volume in dB"),
                NodeProperty("playing", "bool", False, "Is playing"),
            ],
            methods=[
                NodeMethod("play", "play()", "Start playback"),
                NodeMethod("stop", "stop()", "Stop playback"),
            ],
            signals=["finished"],
            parent_types=["Node2D"],
            example_code="audio = AudioStreamPlayer2D()\naudio.stream = load_sound(\"jump.wav\")\naudio.play()",
            use_cases=["Sound effects", "Music"]
        ))
        
        # Additional Scene2D nodes
        self.register(NodeTypeDoc(
            type_name="StaticBody2D",
            category=NodeCategory.PHYSICS,
            icon="🧱",
            brief="Static physics body",
            description="Immovable physics body.",
            properties=[
                NodeProperty("collision_layer", "int", 1, "Collision layers"),
                NodeProperty("collision_mask", "int", 1, "Collision mask"),
            ],
            methods=[],
            signals=["body_entered", "body_exited"],
            parent_types=["Node2D"],
            example_code="wall = StaticBody2D()",
            use_cases=["Walls", "Platforms", "Static objects"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="CollisionShape2D",
            category=NodeCategory.PHYSICS,
            icon="⭕",
            brief="Collision shape",
            description="Defines collision shape for physics body.",
            properties=[
                NodeProperty("shape", "Shape2D", None, "Collision shape"),
                NodeProperty("disabled", "bool", False, "Is disabled"),
            ],
            methods=[],
            signals=[],
            parent_types=["Node2D"],
            example_code="shape = CollisionShape2D()\nshape.shape = CircleShape2D(10)",
            use_cases=["Physics collision"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="Camera2D",
            category=NodeCategory.VISUAL,
            icon="📷",
            brief="2D camera",
            description="Controls viewport for 2D scenes.",
            properties=[
                NodeProperty("zoom", "Vector2", "(1, 1)", "Camera zoom"),
                NodeProperty("offset", "Vector2", "(0, 0)", "Camera offset"),
                NodeProperty("anchor_mode", "int", 0, "Anchor mode"),
            ],
            methods=[],
            signals=[],
            parent_types=["Node2D"],
            example_code="camera = Camera2D()\ncamera.zoom = Vector2(2, 2)",
            use_cases=["View control", "Follow player"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="TileMap",
            category=NodeCategory.VISUAL,
            icon="🗺️",
            brief="Tile-based map",
            description="Displays tiles on a grid.",
            properties=[
                NodeProperty("tile_set", "TileSet", None, "Tile set to use"),
                NodeProperty("cell_size", "Vector2", "(16, 16)", "Tile size"),
            ],
            methods=[
                NodeMethod("set_cell", "set_cell(x, y, tile_id)", "Set tile at position"),
            ],
            signals=[],
            parent_types=["Node2D"],
            example_code="tilemap = TileMap()\ntilemap.tile_set = load_tileset(\"tiles.tsx\")",
            use_cases=["Level design", "Backgrounds"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="Light2D",
            category=NodeCategory.EFFECTS,
            icon="💡",
            brief="2D light",
            description="Emits light in 2D scene.",
            properties=[
                NodeProperty("enabled", "bool", True, "Is enabled"),
                NodeProperty("color", "Color", "white", "Light color"),
                NodeProperty("energy", "float", 1.0, "Light intensity"),
            ],
            methods=[],
            signals=[],
            parent_types=["Node2D"],
            example_code="light = Light2D()\nlight.color = Color(1, 0.8, 0.4)",
            use_cases=["Dynamic lighting", "Atmosphere"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="CPUParticles2D",
            category=NodeCategory.EFFECTS,
            icon="✨",
            brief="CPU particles",
            description="CPU-based particle system.",
            properties=[
                NodeProperty("emitting", "bool", False, "Is emitting"),
                NodeProperty("amount", "int", 100, "Particle count"),
                NodeProperty("lifetime", "float", 1.0, "Particle lifetime"),
            ],
            methods=[
                NodeMethod("restart", "restart()", "Restart particles"),
            ],
            signals=["finished"],
            parent_types=["Node2D"],
            example_code="particles = CPUParticles2D()\nparticles.emitting = True",
            use_cases=["Effects", "Explosions", "Atmosphere"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="Path2D",
            category=NodeCategory.UTILITY,
            icon="〰️",
            brief="2D path",
            description="Curve for path following.",
            properties=[
                NodeProperty("curve", "Curve2D", None, "Path curve"),
            ],
            methods=[],
            signals=[],
            parent_types=["Node2D"],
            example_code="path = Path2D()\npath.curve = Curve2D()",
            use_cases=["Enemy paths", "Camera tracks"]
        ))
        
        self.register(NodeTypeDoc(
            type_name="Skeleton2D",
            category=NodeCategory.UTILITY,
            icon="🦴",
            brief="2D skeleton",
            description="2D skeletal animation system.",
            properties=[
                NodeProperty("bones", "int", 0, "Bone count"),
            ],
            methods=[
                NodeMethod("add_bone", "add_bone(bone)", "Add bone"),
            ],
            signals=[],
            parent_types=["Node2D"],
            example_code="skeleton = Skeleton2D()",
            use_cases=["Character animation", "Ragdoll"]
        ))
    
    def register(self, node_doc: NodeTypeDoc) -> None:
        """Register a node type."""
        self._nodes[node_doc.type_name] = node_doc
    
    def get_node_doc(self, type_name: str) -> Optional[NodeTypeDoc]:
        """Get documentation for a node type."""
        return self._nodes.get(type_name)
    
    def get_categories(self) -> List[NodeCategory]:
        """Get all categories."""
        return list(NodeCategory)
    
    def get_nodes_by_category(self, category: NodeCategory) -> List[NodeTypeDoc]:
        """Get all nodes in a category."""
        return [n for n in self._nodes.values() if n.category == category]
    
    def get_all_nodes(self) -> Dict[str, NodeTypeDoc]:
        """Get all registered nodes."""
        return self._nodes.copy()


# Singleton instance
_registry_instance = None

def get_node_types_registry() -> NodeTypesRegistry:
    """Get the global node types registry."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = NodeTypesRegistry()
    return _registry_instance


# Constants for easy access
NODE = "Node"
NODE2D = "Node2D"
SPRITE = "Sprite2D"
ANIMATED_SPRITE = "AnimatedSprite2D"
RIGID_BODY2D = "RigidBody2D"
STATIC_BODY2D = "StaticBody2D"
CONTROL = "Control"
LABEL = "Label"
BUTTON = "Button"
AUDIO_STREAM_PLAYER = "AudioStreamPlayer2D"


__all__ = [
    "NodeCategory",
    "NodeProperty",
    "NodeMethod",
    "NodeTypeDoc",
    "NodeTypesRegistry",
    "get_node_types_registry",
    "NODE",
    "NODE2D",
    "SPRITE",
    "ANIMATED_SPRITE",
    "RIGID_BODY2D",
    "STATIC_BODY2D",
    "CONTROL",
    "LABEL",
    "BUTTON",
    "AUDIO_STREAM_PLAYER",
]
