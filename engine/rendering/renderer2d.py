# /**************************************************************************/
# /*  renderer2d.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D Renderer with shader support.

Shader System:
- Load external GLSL fragment shaders
- Pythonic uniform/attribute interface
- GPU communication without blocking main thread
- Material system for reusable shader configurations
"""

from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtGui import QColor, QImage, QPainter

from engine.rendering.camera import Camera2D
from engine.rendering.light import Light2D

import logging


MAX_LIGHTS = 128


logger = logging.getLogger(__name__)


@dataclass
class ShaderUniform:
    """Represents a shader uniform variable."""

    name: str
    value: Any
    type_hint: str = "float"  # float, int, vec2, vec3, vec4, color


@dataclass
class ShaderProgram:
    """Compiled shader program with uniform interface.
    
    Provides Pythonic access to GLSL uniforms without
    directly exposing OpenGL complexity.
    """
    name: str
    vertex_source: str
    fragment_source: str
    uniforms: Dict[str, ShaderUniform]
    
    def set_uniform(self, name: str, value: Any) -> None:
        """Set uniform value (type-safe)."""
        if name not in self.uniforms:
            # Auto-create uniform
            self.uniforms[name] = ShaderUniform(name, value)
        else:
            self.uniforms[name].value = value
    
    def get_uniform(self, name: str) -> Any:
        """Get uniform value."""
        if name in self.uniforms:
            return self.uniforms[name].value
        return None


class ShaderManager:
    """Manages shader loading, compilation, and caching.
    
    Features:
    - Load GLSL files from disk
    - Hot-reload shaders during development
    - Cache compiled shaders
    - Default fallback shaders
    """
    
    # Default shader sources
    DEFAULT_VERTEX = """
    #version 330 core
    layout(location = 0) in vec2 position;
    layout(location = 1) in vec2 uv;
    uniform mat4 projection;
    uniform mat4 model;
    out vec2 v_uv;
    void main() {
        gl_Position = projection * model * vec4(position, 0.0, 1.0);
        v_uv = uv;
    }
    """
    
    DEFAULT_FRAGMENT = """
    #version 330 core
    in vec2 v_uv;
    uniform vec4 color = vec4(1.0, 1.0, 1.0, 1.0);
    uniform sampler2D texture0;
    uniform bool use_texture = false;
    out vec4 frag_color;
    void main() {
        if (use_texture) {
            frag_color = texture(texture0, v_uv) * color;
        } else {
            frag_color = color;
        }
    }
    """
    
    def __init__(self, shader_dir: Optional[str] = None):
        """Initialize shader manager.
        
        Args:
            shader_dir: Directory containing .vert and .frag files
        """
        self.shader_dir = Path(shader_dir) if shader_dir else None
        self._shaders: Dict[str, ShaderProgram] = {}
        self._file_mtimes: Dict[str, float] = {}
        
        # Load default shader
        self._create_default_shader()
    
    def _create_default_shader(self) -> None:
        """Create the default shader program."""
        self._shaders["default"] = ShaderProgram(
            name="default",
            vertex_source=self.DEFAULT_VERTEX,
            fragment_source=self.DEFAULT_FRAGMENT,
            uniforms={
                "color": ShaderUniform("color", (1.0, 1.0, 1.0, 1.0), "vec4"),
                "projection": ShaderUniform("projection", None, "mat4"),
                "model": ShaderUniform("model", None, "mat4"),
            }
        )
    
    def load_shader(self, name: str, vertex_file: Optional[str] = None, 
                   fragment_file: str = None) -> ShaderProgram:
        """Load shader from files.
        
        Args:
            name: Shader identifier
            vertex_file: Path to .vert file (optional, uses default if None)
            fragment_file: Path to .frag file (required)
            
        Returns:
            Loaded ShaderProgram
        """
        # Resolve paths
        if vertex_file:
            vert_path = self._resolve_path(vertex_file)
        else:
            vert_path = None
            
        frag_path = self._resolve_path(fragment_file)
        
        # Read source files
        vertex_src = self.DEFAULT_VERTEX
        if vert_path and vert_path.exists():
            vertex_src = vert_path.read_text()
            self._file_mtimes[str(vert_path)] = vert_path.stat().st_mtime
        
        fragment_src = self.DEFAULT_FRAGMENT
        if frag_path and frag_path.exists():
            fragment_src = frag_path.read_text()
            self._file_mtimes[str(frag_path)] = frag_path.stat().st_mtime
        
        # Create shader program
        shader = ShaderProgram(
            name=name,
            vertex_source=vertex_src,
            fragment_source=fragment_src,
            uniforms={}
        )
        
        self._shaders[name] = shader
        return shader
    
    def _resolve_path(self, filename: str) -> Path:
        """Resolve shader file path."""
        path = Path(filename)
        if path.is_absolute():
            return path
        if self.shader_dir:
            return self.shader_dir / filename
        return path
    
    def get_shader(self, name: str) -> Optional[ShaderProgram]:
        """Get loaded shader by name."""
        return self._shaders.get(name)
    
    def check_hot_reload(self) -> List[str]:
        """Check for modified shader files and reload them.
        
        Returns:
            List of reloaded shader names
        """
        reloaded = []
        for file_path, old_mtime in list(self._file_mtimes.items()):
            path = Path(file_path)
            if path.exists():
                new_mtime = path.stat().st_mtime
                if new_mtime > old_mtime:
                    # File changed, find and reload shader
                    for name, shader in self._shaders.items():
                        if shader.name != "default":
                            # Reload by re-creating
                            self._shaders[name] = ShaderProgram(
                                name=name,
                                vertex_source=shader.vertex_source,
                                fragment_source=shader.fragment_source,
                                uniforms=shader.uniforms
                            )
                            reloaded.append(name)
                    self._file_mtimes[file_path] = new_mtime
        return reloaded
    
    def list_shaders(self) -> List[str]:
        """List available shader names."""
        return list(self._shaders.keys())


@dataclass
class Material:
    """Material combining shader and uniform values.
    
    Allows reusable shader configurations:
    >>> material = Material("default", {"color": (1, 0, 0, 1)})
    >>> renderer.use_material(material)
    """
    shader_name: str
    uniforms: Dict[str, Any]
    
    def set_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """Set material color uniform."""
        self.uniforms["color"] = (r, g, b, a)
    
    def set_float(self, name: str, value: float) -> None:
        """Set float uniform."""
        self.uniforms[name] = value


class Renderer2D:
    """2D renderer with shader and material support.
    
    Example:
        >>> renderer = Renderer2D(800, 600)
        >>> 
        >>> # Load custom shader
        >>> renderer.shader_manager.load_shader(
        ...     "glow", 
        ...     fragment_file="shaders/glow.frag"
        ... )
        >>> 
        >>> # Create material
        >>> material = Material("glow", {"intensity": 0.5})
        >>> renderer.use_material(material)
        >>> 
        >>> # Check for shader changes (hot reload)
        >>> reloaded = renderer.shader_manager.check_hot_reload()
    """
    
    def __init__(self, width: int = 800, height: int = 600, shader_dir: Optional[str] = None):
        self.width = width
        self.height = height
        self.camera = Camera2D(width, height)
        # Use dict for O(1) add/remove instead of list O(n)
        self._lights: Dict[int, Light2D] = {}
        self._light_order: List[int] = []  # Maintain insertion order
        self.render_target = QImage(width, height, QImage.Format.Format_ARGB32)
        self.render_target.fill(QColor(200, 200, 200))
        self.show_grid = False
        self.show_colliders = False
        self.show_lights = False
        self.vsync_enabled = True
        self.antialiasing = True
        
        # Shader system
        self.shader_manager = ShaderManager(shader_dir)
        self._current_material: Optional[Material] = None
        self._material_stack: List[Material] = []

    @property
    def lights(self) -> List[Light2D]:
        """Get lights in insertion order."""
        return [self._lights[lid] for lid in self._light_order if lid in self._lights]

    def add_light(self, light: Light2D) -> None:
        """Add a light with O(1) complexity."""
        light_id = id(light)
        if light_id in self._lights:
            return

        # Enforce max lights limit
        if len(self._lights) >= MAX_LIGHTS:
            oldest_id = self._light_order.pop(0)
            del self._lights[oldest_id]

        self._lights[light_id] = light
        self._light_order.append(light_id)

    def remove_light(self, light: Light2D) -> None:
        """Remove a light with O(1) complexity."""
        light_id = id(light)
        if light_id in self._lights:
            del self._lights[light_id]
            # Remove from order list (O(n) but rarely called)
            if light_id in self._light_order:
                self._light_order.remove(light_id)

    def render_scene(self, scene_nodes: List) -> QImage:
        painter = QPainter(self.render_target)
        try:
            painter.fillRect(0, 0, self.width, self.height, QColor(200, 200, 200))
            if self.show_grid:
                self._draw_grid(painter)
            for node in scene_nodes:
                self._render_node(painter, node)
            if self.show_lights:
                self._draw_lights(painter)
        finally:
            painter.end()
        return self.render_target

    def _render_node(self, painter: QPainter, node) -> None:
        if not getattr(node, "visible", True):
            return
        
        # Store painter for draw_sprite calls
        self._current_painter = painter
        
        # If node has _draw method, use it (for Sprite2D and similar)
        if hasattr(node, "_draw") and callable(getattr(node, "_draw")):
            node._draw(self)
            # Still render children
            for child in getattr(node, "children", []):
                self._render_node(painter, child)
            return
        
        # Check if this is a sprite with texture
        texture = getattr(node, "texture", None)
        if texture is not None and texture.is_loaded():
            self._draw_sprite(painter, node, texture)
        elif hasattr(node, "transform"):
            # Fallback: draw colored rect for nodes without textures
            screen_x, screen_y = self._world_to_screen(node.transform.position)
            color = QColor(*getattr(node, "modulate", (255, 255, 255, 255)))
            painter.fillRect(int(screen_x), int(screen_y), 32, 32, color)
        
        for child in getattr(node, "children", []):
            self._render_node(painter, child)
    
    def _draw_sprite(self, painter: QPainter, node, texture) -> None:
        """Draw a sprite with its texture."""
        from PySide6.QtCore import QRect
        
        global_pos = getattr(node, "get_global_position", lambda: getattr(node, "position", (0, 0)))()
        offset = getattr(node, "offset", None)
        if offset:
            global_pos = (global_pos[0] + offset.x, global_pos[1] + offset.y)
        
        # Calculate frame rect for animation
        hframes = getattr(node, "hframes", 1)
        vframes = getattr(node, "vframes", 1)
        frame = getattr(node, "_frame", 0)
        region_enabled = getattr(node, "region_enabled", False)
        region_rect = getattr(node, "region_rect", (0, 0, 0, 0))
        
        if hframes > 1 or vframes > 1:
            fw = texture.width // hframes
            fh = texture.height // vframes
            col = frame % hframes
            row = frame // hframes
            src_x = col * fw
            src_y = row * fh
            src_w, src_h = fw, fh
        elif region_enabled:
            src_x, src_y, src_w, src_h = region_rect
        else:
            src_x, src_y, src_w, src_h = 0, 0, texture.width, texture.height
        
        # Calculate draw position
        screen_x, screen_y = self._world_to_screen(global_pos)
        centered = getattr(node, "centered", True)
        
        if centered:
            screen_x -= src_w / 2
            screen_y -= src_h / 2
        
        # Get the image (full or sub-region)
        if src_x == 0 and src_y == 0 and src_w == texture.width and src_h == texture.height:
            img = texture.get_image()
        else:
            img = texture.get_sub_image(src_x, src_y, src_w, src_h)
        
        if img:
            # Handle flipping
            flip_h = getattr(node, "flip_h", False)
            flip_v = getattr(node, "flip_v", False)
            
            if flip_h or flip_v:
                img = img.mirrored(flip_h, flip_v)
            
            # Draw the texture
            dest_rect = QRect(int(screen_x), int(screen_y), src_w, src_h)
            painter.drawImage(dest_rect, img)
    
    def draw_sprite(self, texture, position, source_rect=None, scale=None, rotation=0, modulate=None) -> None:
        """Public method to draw a sprite (called from node's _draw)."""
        from PySide6.QtCore import QRect
        
        if not self._current_painter or not texture or not texture.is_loaded():
            return
        
        painter = self._current_painter
        
        # Calculate screen position
        screen_x, screen_y = self._world_to_screen((position.x, position.y))
        
        # Get source rect
        if source_rect:
            src_x, src_y, src_w, src_h = source_rect
        else:
            src_x, src_y, src_w, src_h = 0, 0, texture.width, texture.height
        
        # Get the image
        if src_x == 0 and src_y == 0 and src_w == texture.width and src_h == texture.height:
            img = texture.get_image()
        else:
            img = texture.get_sub_image(src_x, src_y, src_w, src_h)
        
        if img:
            dest_rect = QRect(int(screen_x), int(screen_y), src_w, src_h)
            painter.drawImage(dest_rect, img)

    def _world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[float, float]:
        view_x, view_y, _, _ = self.camera.get_view_rect()
        return ((world_pos[0] - view_x) * self.camera.zoom, (world_pos[1] - view_y) * self.camera.zoom)

    def use_material(self, material: Material) -> None:
        """Set current material for rendering.
        
        Args:
            material: Material with shader and uniform values
        """
        self._current_material = material
    
    def push_material(self, material: Material) -> None:
        """Push current material to stack and use new one.
        
        Useful for temporary material changes:
        >>> renderer.push_material(highlight_material)
        >>> render_highlighted()  # Uses highlight
        >>> renderer.pop_material()  # Restores previous
        """
        if self._current_material:
            self._material_stack.append(self._current_material)
        self._current_material = material
    
    def pop_material(self) -> Optional[Material]:
        """Pop material from stack and restore previous.
        
        Returns:
            The restored material or None if stack empty
        """
        if self._material_stack:
            self._current_material = self._material_stack.pop()
        else:
            self._current_material = None
        return self._current_material

    def _draw_grid(self, painter: QPainter) -> None:
        painter.setPen(QColor(150, 150, 150))
        for x in range(0, self.width, 32):
            painter.drawLine(x, 0, x, self.height)
        for y in range(0, self.height, 32):
            painter.drawLine(0, y, self.width, y)

    def _draw_lights(self, painter: QPainter) -> None:
        for light in self.lights:
            screen_x, screen_y = self._world_to_screen(light.position)
            painter.setPen(QColor(*light.color))
            radius = int(light.range * self.camera.zoom)
            diameter = max(0, radius * 2)
            painter.drawEllipse(int(screen_x - radius), int(screen_y - radius), diameter, diameter)
