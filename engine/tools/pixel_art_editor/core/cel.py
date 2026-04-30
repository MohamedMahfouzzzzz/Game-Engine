# /**************************************************************************/
# /*  cel.py                                                                */
# /**************************************************************************/

"""Cel model - image data for a specific layer at a specific frame.

Equivalent to Aseprite's doc::Cel class.
A cel represents the image content of a layer at a specific frame.
"""

from typing import Optional, Tuple
from .image_buffer import ImageBuffer, ColorMode


class Cel:
    """A cel contains the image data for a layer at a specific frame.
    
    In animation, each frame can have different cels per layer.
    """
    
    def __init__(self, 
                 layer_id: int, 
                 frame: int, 
                 width: int, 
                 height: int,
                 x: int = 0,
                 y: int = 0,
                 opacity: float = 1.0):
        self.layer_id = layer_id      # Parent layer
        self.frame = frame            # Frame number
        self.x = x                    # X position in sprite
        self.y = y                    # Y position in sprite
        self.opacity = opacity        # Opacity (0.0 - 1.0)
        
        # Image data
        self._image: Optional[ImageBuffer] = ImageBuffer(width, height, ColorMode.RGBA)
    
    @property
    def image(self) -> Optional[ImageBuffer]:
        """Get image buffer."""
        return self._image
    
    @image.setter
    def image(self, image: ImageBuffer) -> None:
        """Set image buffer."""
        self._image = image
    
    def has_image(self) -> bool:
        """Check if cel has image data."""
        return self._image is not None and not self._image.is_empty()
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get bounding box of this cel."""
        if not self._image:
            return (self.x, self.y, 0, 0)
        
        bounds = self._image.get_bounds()
        return (self.x + bounds[0], self.y + bounds[1], bounds[2], bounds[3])
    
    def is_empty(self) -> bool:
        """Check if cel has no visible content."""
        return not self.has_image()
    
    def copy(self) -> 'Cel':
        """Create a copy of this cel."""
        if self._image:
            new_cel = Cel(
                self.layer_id,
                self.frame,
                self._image.width,
                self._image.height,
                self.x,
                self.y,
                self.opacity
            )
            new_cel._image = self._image.copy()
        else:
            new_cel = Cel(
                self.layer_id,
                self.frame,
                0, 0,
                self.x,
                self.y,
                self.opacity
            )
        return new_cel
    
    def move(self, dx: int, dy: int) -> None:
        """Move cel by delta."""
        self.x += dx
        self.y += dy


class LinkedCel(Cel):
    """A cel that links to another cel's image data.
    
    This allows multiple frames to share the same image data,
    saving memory for static layers.
    """
    
    def __init__(self, layer_id: int, frame: int, linked_cel: Cel):
        super().__init__(layer_id, frame, 0, 0)
        self._linked_cel = linked_cel
    
    @property
    def image(self) -> Optional[ImageBuffer]:
        """Get linked image buffer."""
        return self._linked_cel.image if self._linked_cel else None
    
    def has_image(self) -> bool:
        """Check if linked cel has image."""
        return self._linked_cel.has_image() if self._linked_cel else False
    
    def unlink(self) -> Cel:
        """Convert to regular cel by copying linked data."""
        if self._linked_cel and self._linked_cel.image:
            new_cel = Cel(
                self.layer_id,
                self.frame,
                self._linked_cel.image.width,
                self._linked_cel.image.height,
                self.x,
                self.y,
                self.opacity
            )
            new_cel._image = self._linked_cel.image.copy()
            return new_cel
        return Cel(self.layer_id, self.frame, 0, 0, self.x, self.y, self.opacity)
