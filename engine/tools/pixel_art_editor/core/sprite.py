# /**************************************************************************/
# /*  sprite.py                                                             */
# /**************************************************************************/

"""Sprite model - main container for pixel art document.

Equivalent to Aseprite's doc::Sprite class.
The Sprite is the main document that contains layers, frames, and metadata.
"""

from typing import List, Optional, Tuple, Dict
from .layer import Layer, LayerGroup
from .frame import Frame, FrameSequence
from .tag import Tag
from .slice import Slice
from .palette import Palette
from .image_buffer import ColorMode


class Sprite:
    """Main sprite/document container.
    
    A sprite contains:
    - Multiple layers (Layer, LayerGroup)
    - Multiple animation frames (Frame)
    - Frame tags for animation organization
    - Slices for 9-patch and regions
    - Color palette (for indexed mode)
    """
    
    _id_counter = 0
    
    def __init__(self, 
                 width: int = 64, 
                 height: int = 64,
                 color_mode: ColorMode = ColorMode.RGBA):
        Sprite._id_counter += 1
        self.id = Sprite._id_counter
        self.filename: Optional[str] = None
        
        # Canvas dimensions
        self.width = width
        self.height = height
        self.color_mode = color_mode
        
        # Layers (ordered from bottom to top)
        self._layers: List[Layer] = []
        
        # Animation frames
        self._frames = FrameSequence()
        
        # Frame tags
        self._tags: List[Tag] = []
        
        # Slices
        self._slices: List[Slice] = []
        
        # Palette (for indexed color mode)
        self._palette = Palette.default_palette()
        
        # Grid settings
        self.grid_bounds = (0, 0, 16, 16)  # x, y, w, h
        
        # Initialize with one frame and one layer
        self._frames.add_frame(Frame.default_frame(0))
        self.add_layer("Layer 1")
    
    @property
    def layer_count(self) -> int:
        """Get number of layers."""
        return len(self._layers)
    
    @property
    def frame_count(self) -> int:
        """Get number of frames."""
        return self._frames.count
    
    def add_layer(self, name: str, is_background: bool = False) -> Layer:
        """Add a new layer."""
        layer = Layer(name, is_background)
        layer._sprite = self
        self._layers.append(layer)
        
        # Add a cel for each frame
        for frame_idx in range(self.frame_count):
            from .cel import Cel
            cel = Cel(layer.id, frame_idx, self.width, self.height)
            layer.set_cel(frame_idx, cel)
        
        return layer
    
    def remove_layer(self, layer: Layer) -> None:
        """Remove a layer."""
        if layer in self._layers:
            layer._sprite = None
            self._layers.remove(layer)
    
    def get_layer(self, index: int) -> Optional[Layer]:
        """Get layer at index."""
        if 0 <= index < len(self._layers):
            return self._layers[index]
        return None
    
    def get_layer_by_name(self, name: str) -> Optional[Layer]:
        """Get layer by name."""
        for layer in self._layers:
            if layer.name == name:
                return layer
        return None
    
    def move_layer(self, from_index: int, to_index: int) -> None:
        """Move layer to new position."""
        if 0 <= from_index < len(self._layers) and 0 <= to_index < len(self._layers):
            layer = self._layers.pop(from_index)
            self._layers.insert(to_index, layer)
    
    def get_layers(self) -> List[Layer]:
        """Get all layers (bottom to top)."""
        return self._layers.copy()
    
    def get_visible_layers(self, frame: int = 0) -> List[Layer]:
        """Get visible layers at frame (bottom to top)."""
        return [l for l in self._layers if l.visible and l.get_cel(frame)]
    
    def add_frame(self, duration_ms: int = 100) -> Frame:
        """Add a new frame."""
        frame = Frame(self.frame_count, duration_ms)
        self._frames.add_frame(frame)
        
        # Add empty cels to all layers for this frame
        for layer in self._layers:
            from .cel import Cel
            cel = Cel(layer.id, frame.index, self.width, self.height)
            layer.set_cel(frame.index, cel)
        
        return frame
    
    def remove_frame(self, index: int) -> Optional[Frame]:
        """Remove frame at index."""
        if self.frame_count <= 1:
            return None  # Can't remove last frame
        
        frame = self._frames.remove_frame(index)
        
        # Remove cels from all layers
        if frame:
            for layer in self._layers:
                layer.remove_cel(index)
        
        return frame
    
    def get_frame(self, index: int) -> Optional[Frame]:
        """Get frame at index."""
        return self._frames.get_frame(index)
    
    def add_tag(self, tag: Tag) -> None:
        """Add a frame tag."""
        self._tags.append(tag)
    
    def remove_tag(self, tag: Tag) -> None:
        """Remove a frame tag."""
        if tag in self._tags:
            self._tags.remove(tag)
    
    def get_tags(self) -> List[Tag]:
        """Get all frame tags."""
        return self._tags.copy()
    
    def get_tags_at_frame(self, frame: int) -> List[Tag]:
        """Get tags that contain this frame."""
        return [t for t in self._tags if t.contains(frame)]
    
    def add_slice(self, slice_obj: Slice) -> None:
        """Add a slice."""
        self._slices.append(slice_obj)
    
    def remove_slice(self, slice_obj: Slice) -> None:
        """Remove a slice."""
        if slice_obj in self._slices:
            self._slices.remove(slice_obj)
    
    def get_slices(self) -> List[Slice]:
        """Get all slices."""
        return self._slices.copy()
    
    def get_slice(self, name: str) -> Optional[Slice]:
        """Get slice by name."""
        for s in self._slices:
            if s.name == name:
                return s
        return None
    
    @property
    def palette(self) -> Palette:
        """Get color palette."""
        return self._palette
    
    @palette.setter
    def palette(self, palette: Palette) -> None:
        """Set color palette."""
        self._palette = palette
    
    def resize(self, new_width: int, new_height: int) -> None:
        """Resize the sprite."""
        self.width = new_width
        self.height = new_height
        
        # Resize all layer cels
        for layer in self._layers:
            for cel in layer.get_cels():
                if cel.image:
                    cel.image.resize(new_width, new_height)
    
    def crop(self, x: int, y: int, width: int, height: int) -> None:
        """Crop the sprite to region."""
        # TODO: Implement crop
        pass
    
    def flatten(self, frame: int = 0) -> 'ImageBuffer':
        """Flatten all visible layers into one image.
        
        Returns a new ImageBuffer with the flattened result.
        """
        from .image_buffer import ImageBuffer
        from PIL import Image
        
        # Start with transparent background
        result = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        # Composite each visible layer
        for layer in self._layers:
            if not layer.visible:
                continue
            
            cel = layer.get_cel(frame)
            if not cel or not cel.image:
                continue
            
            # Convert to PIL for compositing
            cel_image = cel.image.to_pil()
            
            # Apply layer opacity
            if layer.opacity < 255:
                alpha = cel_image.split()[3]
                alpha = alpha.point(lambda p: int(p * layer.opacity / 255))
                cel_image.putalpha(alpha)
            
            # Composite
            result = Image.alpha_composite(result, cel_image)
        
        # Convert back to ImageBuffer
        buffer = ImageBuffer(self.width, self.height)
        buffer.from_pil(result)
        return buffer
    
    def copy(self) -> 'Sprite':
        """Create a copy of this sprite."""
        new_sprite = Sprite(self.width, self.height, self.color_mode)
        new_sprite._palette = self._palette.copy()
        new_sprite.grid_bounds = self.grid_bounds
        
        # Copy layers
        for layer in self._layers:
            new_layer = layer.copy()
            new_layer._sprite = new_sprite
            new_sprite._layers.append(new_layer)
        
        # Copy frames
        new_sprite._frames = self._frames.copy()
        
        # Copy tags
        new_sprite._tags = [t.copy() for t in self._tags]
        
        # Copy slices
        new_sprite._slices = [s.copy() for s in self._slices]
        
        return new_sprite
    
    def get_bounds(self, frame: int = 0) -> Tuple[int, int, int, int]:
        """Get bounding box of non-transparent content."""
        flat = self.flatten(frame)
        return flat.get_bounds()
    
    def is_empty(self) -> bool:
        """Check if sprite has no content."""
        for layer in self._layers:
            for cel in layer.get_cels():
                if cel.has_image():
                    return False
        return True
    
    def get_memory_size(self) -> int:
        """Estimate memory usage in bytes."""
        size = 0
        for layer in self._layers:
            for cel in layer.get_cels():
                if cel.image:
                    size += cel.image.get_memory_size()
        return size
