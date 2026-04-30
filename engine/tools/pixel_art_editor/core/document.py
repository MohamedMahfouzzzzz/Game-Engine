# /**************************************************************************/
# /*  document.py                                                           */
# /**************************************************************************/

"""Document model - high-level container for a sprite project.

This is the main document class that the editor works with.
It wraps a Sprite and adds document-level metadata like
modification state, GUID, etc.
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from .sprite import Sprite


class Document:
    """A pixel art document.
    
    This is the top-level object that the editor manipulates.
    It contains a Sprite (the actual pixel data) and metadata.
    """
    
    def __init__(self, 
                 width: int = 64, 
                 height: int = 64,
                 name: str = "Untitled"):
        self._guid = uuid.uuid4()
        self.name = name
        self.filename: Optional[Path] = None
        
        # The actual sprite data
        self._sprite = Sprite(width, height)
        
        # Document state
        self._modified = False
        self._read_only = False
        
        # Metadata
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.author = ""
        self.description = ""
        self.custom_data: Dict[str, Any] = {}
        
        # View state (not saved)
        self._zoom = 1.0
        self._scroll_x = 0
        self._scroll_y = 0
        self._active_layer_index = 0
        self._active_frame_index = 0
    
    @property
    def guid(self) -> uuid.UUID:
        """Get document unique identifier."""
        return self._guid
    
    @property
    def sprite(self) -> Sprite:
        """Get the underlying sprite."""
        return self._sprite
    
    @property
    def modified(self) -> bool:
        """Check if document has unsaved changes."""
        return self._modified
    
    def mark_modified(self) -> None:
        """Mark document as modified."""
        self._modified = True
        self.modified_at = datetime.now()
    
    def mark_saved(self) -> None:
        """Mark document as saved."""
        self._modified = False
    
    @property
    def read_only(self) -> bool:
        """Check if document is read-only."""
        return self._read_only
    
    def set_read_only(self, value: bool) -> None:
        """Set read-only state."""
        self._read_only = value
    
    @property
    def width(self) -> int:
        """Get document width."""
        return self._sprite.width
    
    @property
    def height(self) -> int:
        """Get document height."""
        return self._sprite.height
    
    def resize(self, new_width: int, new_height: int) -> None:
        """Resize the document."""
        self._sprite.resize(new_width, new_height)
        self.mark_modified()
    
    @property
    def active_layer_index(self) -> int:
        """Get/set active layer index."""
        return self._active_layer_index
    
    @active_layer_index.setter
    def active_layer_index(self, index: int) -> None:
        if 0 <= index < self._sprite.layer_count:
            self._active_layer_index = index
    
    @property
    def active_frame_index(self) -> int:
        """Get/set active frame index."""
        return self._active_frame_index
    
    @active_frame_index.setter
    def active_frame_index(self, index: int) -> None:
        if 0 <= index < self._sprite.frame_count:
            self._active_frame_index = index
    
    def get_active_layer(self):
        """Get the currently active layer."""
        return self._sprite.get_layer(self._active_layer_index)
    
    def get_active_frame(self):
        """Get the currently active frame."""
        return self._sprite.get_frame(self._active_frame_index)
    
    @property
    def zoom(self) -> float:
        """Get view zoom level."""
        return self._zoom
    
    @zoom.setter
    def zoom(self, value: float) -> None:
        self._zoom = max(0.1, min(50.0, value))
    
    @property
    def scroll(self) -> tuple:
        """Get view scroll position."""
        return (self._scroll_x, self._scroll_y)
    
    def set_scroll(self, x: int, y: int) -> None:
        """Set view scroll position."""
        self._scroll_x = x
        self._scroll_y = y
    
    def get_display_title(self) -> str:
        """Get title for display in UI."""
        if self.filename:
            return self.filename.stem
        return self.name
    
    def get_window_title(self) -> str:
        """Get title for window with modification indicator."""
        title = self.get_display_title()
        if self._modified:
            title = f"*{title}"
        return title
    
    def copy(self) -> 'Document':
        """Create a copy of this document."""
        new_doc = Document(self.width, self.height, f"{self.name} copy")
        new_doc._sprite = self._sprite.copy()
        new_doc.author = self.author
        new_doc.description = self.description
        new_doc.custom_data = self.custom_data.copy()
        return new_doc
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get document metadata for saving."""
        return {
            'guid': str(self._guid),
            'name': self.name,
            'author': self.author,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'custom_data': self.custom_data,
        }
    
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Set document metadata from loaded data."""
        if 'guid' in metadata:
            self._guid = uuid.UUID(metadata['guid'])
        if 'name' in metadata:
            self.name = metadata['name']
        if 'author' in metadata:
            self.author = metadata['author']
        if 'description' in metadata:
            self.description = metadata['description']
        if 'custom_data' in metadata:
            self.custom_data = metadata['custom_data']
    
    def __repr__(self) -> str:
        return f"Document({self.name}, {self.width}x{self.height}, {self._sprite.layer_count} layers, {self._sprite.frame_count} frames)"
