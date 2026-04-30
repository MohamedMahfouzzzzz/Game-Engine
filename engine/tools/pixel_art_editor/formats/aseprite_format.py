# /**************************************************************************/
# /*  aseprite_format.py                                                    */
# /**************************************************************************/

"""Aseprite (.ase/.aseprite) file format reader/writer.

Supports:
- Loading/saving .ase and .aseprite files
- Layer import/export with opacity and visibility
- RGBA pixel data
- Basic metadata

Based on Aseprite file format specification:
https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, BinaryIO, Dict
from pathlib import Path
from io import BytesIO

import logging

logger = logging.getLogger(__name__)


@dataclass
class AseLayer:
    """Aseprite layer data."""
    flags: int = 0
    layer_type: int = 0
    layer_child_level: int = 0
    blend_mode: int = 0
    opacity: int = 255
    name: str = ""
    visible: bool = True
    data: Optional[bytes] = None


@dataclass
class AseCel:
    """Aseprite cel (cell) data containing pixel data."""
    layer_index: int = 0
    x: int = 0
    y: int = 0
    opacity: int = 255
    width: int = 0
    height: int = 0
    pixel_data: bytes = field(default_factory=bytes)
    linked_frame: int = -1  # For linked cels


@dataclass
class AseFrame:
    """Aseprite frame data."""
    bytes: int = 0
    duration: int = 100  # ms
    cels: List[AseCel] = field(default_factory=list)


@dataclass
class AseHeader:
    """Aseprite file header."""
    file_size: int = 0
    magic_number: int = 0xA5E0
    frames: int = 1
    width: int = 0
    height: int = 0
    depth: int = 32
    flags: int = 1  # 1 = layer opacity valid
    speed: int = 100  # DEPRECATED
    transparent_index: int = 0
    num_colors: int = 0
    pixel_width: int = 1
    pixel_height: int = 1
    grid_x: int = 0
    grid_y: int = 0
    grid_width: int = 0
    grid_height: int = 0


class AsepriteFormat:
    """Read and write Aseprite (.ase/.aseprite) files."""
    
    # Chunk types
    CHUNK_OLD_PALETTE = 0x0004
    CHUNK_OLD_PALETTE2 = 0x0011
    CHUNK_LAYER = 0x2004
    CHUNK_CEL = 0x2005
    CHUNK_CEL_EXTRA = 0x2006
    CHUNK_COLOR_PROFILE = 0x2007
    CHUNK_EXTERNAL_FILES = 0x2008
    CHUNK_MASK = 0x2016  # DEPRECATED
    CHUNK_PATH = 0x2017  # NEVER USED
    CHUNK_TAGS = 0x2018
    CHUNK_PALETTE = 0x2019
    CHUNK_USER_DATA = 0x2020
    CHUNK_SLICES = 0x2022
    CHUNK_TILESET = 0x2023
    
    # Layer flags
    LAYER_FLAG_VISIBLE = 1
    LAYER_FLAG_EDITABLE = 2
    LAYER_FLAG_LOCK_MOVEMENT = 4
    LAYER_FLAG_BACKGROUND = 8
    LAYER_FLAG_PREFER_LINKED_CELS = 16
    LAYER_FLAG_COLLAPSED = 32
    LAYER_FLAG_REFERENCE = 64
    
    @classmethod
    def read(cls, filepath: str) -> Optional[Tuple[AseHeader, List[AseLayer], List[AseFrame]]]:
        """Read an Aseprite file and return header, layers, and frames."""
        path = Path(filepath)
        if not path.exists():
            return None
        
        try:
            with open(path, 'rb') as f:
                return cls._read_file(f)
        except Exception as e:
            print(f"Error reading Aseprite file: {e}")
            return None
    
    @classmethod
    def _read_file(cls, f: BinaryIO) -> Tuple[AseHeader, List[AseLayer], List[AseFrame]]:
        """Read file contents."""
        # Read header
        header = cls._read_header(f)
        
        layers: List[AseLayer] = []
        frames: List[AseFrame] = []
        
        # Read frames
        for _ in range(header.frames):
            frame, frame_layers = cls._read_frame(f, header)
            frames.append(frame)
            # Collect unique layers
            for layer in frame_layers:
                if layer not in layers:
                    layers.append(layer)
        
        return header, layers, frames
    
    @classmethod
    def _read_header(cls, f: BinaryIO) -> AseHeader:
        """Read file header."""
        h = AseHeader()
        h.file_size = struct.unpack('<I', f.read(4))[0]
        h.magic_number = struct.unpack('<H', f.read(2))[0]
        
        if h.magic_number != 0xA5E0:
            raise ValueError("Invalid Aseprite file magic number")
        
        h.frames = struct.unpack('<H', f.read(2))[0]
        h.width = struct.unpack('<H', f.read(2))[0]
        h.height = struct.unpack('<H', f.read(2))[0]
        h.depth = struct.unpack('<H', f.read(2))[0]  # bits per pixel
        h.flags = struct.unpack('<I', f.read(4))[0]
        h.speed = struct.unpack('<H', f.read(2))[0]  # DEPRECATED
        
        f.read(4)  # Set to 0
        f.read(4)  # Set to 0
        
        h.transparent_index = struct.unpack('<B', f.read(1))[0]
        f.read(3)  # Ignore
        
        h.num_colors = struct.unpack('<H', f.read(2))[0]
        h.pixel_width = struct.unpack('<B', f.read(1))[0]
        h.pixel_height = struct.unpack('<B', f.read(1))[0]
        h.grid_x = struct.unpack('<h', f.read(2))[0]  # signed
        h.grid_y = struct.unpack('<h', f.read(2))[0]  # signed
        h.grid_width = struct.unpack('<H', f.read(2))[0]
        h.grid_height = struct.unpack('<H', f.read(2))[0]
        
        # Skip to frame 1 (header is 128 bytes)
        f.read(84)
        
        return h
    
    @classmethod
    def _read_frame(cls, f: BinaryIO, header: AseHeader) -> Tuple[AseFrame, List[AseLayer]]:
        """Read a single frame."""
        frame = AseFrame()
        layers: List[AseLayer] = []
        
        # Frame header
        frame.bytes = struct.unpack('<I', f.read(4))[0]
        magic = struct.unpack('<H', f.read(2))[0]
        
        if magic != 0xF1FA:
            raise ValueError("Invalid frame magic number")
        
        chunk_count_old = struct.unpack('<H', f.read(2))[0]
        frame.duration = struct.unpack('<H', f.read(2))[0]  # ms
        
        f.read(2)  # Set to 0
        
        # New chunk count (if chunk_count_old == 0xFFFF)
        chunk_count = chunk_count_old
        if chunk_count_old == 0xFFFF:
            chunk_count = struct.unpack('<I', f.read(4))[0]
        
        # Read chunks
        for _ in range(chunk_count):
            chunk_size = struct.unpack('<I', f.read(4))[0]
            chunk_type = struct.unpack('<H', f.read(2))[0]
            chunk_data = f.read(chunk_size - 6)
            
            if chunk_type == cls.CHUNK_LAYER:
                layer = cls._parse_layer_chunk(chunk_data)
                layers.append(layer)
            elif chunk_type == cls.CHUNK_CEL:
                cel = cls._parse_cel_chunk(chunk_data, header)
                frame.cels.append(cel)
            # Ignore other chunk types for now
        
        return frame, layers
    
    @classmethod
    def _parse_layer_chunk(cls, data: bytes) -> AseLayer:
        """Parse layer chunk."""
        layer = AseLayer()
        f = BytesIO(data)
        
        layer.flags = struct.unpack('<H', f.read(2))[0]
        layer.layer_type = struct.unpack('<H', f.read(2))[0]
        layer.layer_child_level = struct.unpack('<H', f.read(2))[0]
        
        # Default layer width/height (ignored)
        f.read(2)
        f.read(2)
        
        layer.blend_mode = struct.unpack('<H', f.read(2))[0]
        layer.opacity = struct.unpack('<B', f.read(1))[0]
        
        f.read(3)  # Skip
        
        # Layer name (length + string)
        name_len = struct.unpack('<H', f.read(2))[0]
        layer.name = f.read(name_len).decode('utf-8', errors='ignore')
        
        # Visibility from flags
        layer.visible = bool(layer.flags & cls.LAYER_FLAG_VISIBLE)
        
        return layer
    
    @classmethod
    def _parse_cel_chunk(cls, data: bytes, header: AseHeader) -> AseCel:
        """Parse cel chunk."""
        cel = AseCel()
        f = BytesIO(data)
        
        cel.layer_index = struct.unpack('<H', f.read(2))[0]
        cel.x = struct.unpack('<h', f.read(2))[0]  # signed
        cel.y = struct.unpack('<h', f.read(2))[0]  # signed
        cel.opacity = struct.unpack('<B', f.read(1))[0]
        
        cel_type = struct.unpack('<H', f.read(2))[0]
        f.read(7)  # For future use (set to 0)
        
        if cel_type == 0:
            # Raw cel
            cel.width = struct.unpack('<H', f.read(2))[0]
            cel.height = struct.unpack('<H', f.read(2))[0]
            
            # Read pixel data based on color depth
            pixel_bytes = cel.width * cel.height * (header.depth // 8)
            cel.pixel_data = f.read(pixel_bytes)
            
        elif cel_type == 1:
            # Linked cel
            cel.linked_frame = struct.unpack('<H', f.read(2))[0]
            
        elif cel_type == 2:
            # Compressed image (zlib/deflate)
            import zlib
            cel.width = struct.unpack('<H', f.read(2))[0]
            cel.height = struct.unpack('<H', f.read(2))[0]
            
            compressed_data = f.read()
            cel.pixel_data = zlib.decompress(compressed_data)
        
        return cel
    
    @classmethod
    def write(cls, filepath: str, width: int, height: int, 
              layers: List[Dict], pixel_data: List[bytes]) -> bool:
        """Write canvas data to Aseprite file.
        
        Args:
            filepath: Output path
            width: Canvas width
            height: Canvas height
            layers: List of layer dicts with 'name', 'visible', 'opacity'
            pixel_data: List of pixel data for each layer (RGBA)
        """
        try:
            path = Path(filepath)
            with open(path, 'wb') as f:
                return cls._write_file(f, width, height, layers, pixel_data)
        except Exception as e:
            print(f"Error writing Aseprite file: {e}")
            return False
    
    @classmethod
    def _write_file(cls, f: BinaryIO, width: int, height: int,
                    layers: List[Dict], pixel_data: List[bytes]) -> bool:
        """Write Aseprite file contents."""
        import zlib
        
        num_layers = len(layers)
        num_frames = 1  # Single frame for now
        
        # Calculate file size (will update later)
        header_pos = f.tell()
        
        # Write header
        cls._write_header(f, width, height, num_frames, len(pixel_data))
        
        # Write frame
        frame_pos = f.tell()
        
        # Frame size placeholder
        frame_size_pos = f.tell()
        f.write(struct.pack('<I', 0))  # Will update
        f.write(struct.pack('<H', 0xF1FA))  # Magic
        
        # Chunk count = layers + cels
        total_chunks = num_layers + len(pixel_data)
        if total_chunks > 0xFFFF:
            f.write(struct.pack('<H', 0xFFFF))
        else:
            f.write(struct.pack('<H', total_chunks))
        
        f.write(struct.pack('<H', 100))  # Duration
        f.write(struct.pack('<H', 0))  # Reserved
        
        if total_chunks > 0xFFFF:
            f.write(struct.pack('<I', total_chunks))
        
        # Write layer chunks
        for i, layer in enumerate(layers):
            cls._write_layer_chunk(f, layer, i)
        
        # Write cel chunks
        for i, pixels in enumerate(pixel_data):
            cls._write_cel_chunk(f, i, width, height, pixels)
        
        # Update frame size
        frame_end = f.tell()
        f.seek(frame_size_pos)
        f.write(struct.pack('<I', frame_end - frame_pos))
        f.seek(frame_end)
        
        # Update file size
        file_end = f.tell()
        f.seek(header_pos)
        f.write(struct.pack('<I', file_end))
        f.seek(file_end)
        
        return True
    
    @classmethod
    def _write_header(cls, f: BinaryIO, width: int, height: int, 
                      frames: int, num_colors: int) -> None:
        """Write file header."""
        f.write(struct.pack('<I', 0))  # File size (update later)
        f.write(struct.pack('<H', 0xA5E0))  # Magic
        f.write(struct.pack('<H', frames))
        f.write(struct.pack('<H', width))
        f.write(struct.pack('<H', height))
        f.write(struct.pack('<H', 32))  # 32-bit depth
        f.write(struct.pack('<I', 1))  # Flags
        f.write(struct.pack('<H', 100))  # Speed (deprecated)
        f.write(struct.pack('<I', 0))  # Set 0
        f.write(struct.pack('<I', 0))  # Set 0
        f.write(struct.pack('<B', 0))  # Transparent index
        f.write(struct.pack('<B', 0))  # Ignore
        f.write(struct.pack('<B', 0))  # Ignore
        f.write(struct.pack('<B', 0))  # Ignore
        f.write(struct.pack('<H', num_colors))
        f.write(struct.pack('<B', 1))  # Pixel width
        f.write(struct.pack('<B', 1))  # Pixel height
        f.write(struct.pack('<h', 0))  # Grid X
        f.write(struct.pack('<h', 0))  # Grid Y
        f.write(struct.pack('<H', 0))  # Grid width
        f.write(struct.pack('<H', 0))  # Grid height
        f.write(b'\x00' * 84)  # Padding to 128 bytes
    
    @classmethod
    def _write_layer_chunk(cls, f: BinaryIO, layer: Dict, index: int) -> None:
        """Write layer chunk."""
        chunk_start = f.tell()
        
        # Calculate chunk size
        name = layer.get('name', f'Layer {index}')
        name_bytes = name.encode('utf-8')
        name_len = len(name_bytes)
        
        chunk_size = 6 + 16 + 2 + name_len  # header + layer data + name length + name
        
        f.write(struct.pack('<I', chunk_size))
        f.write(struct.pack('<H', cls.CHUNK_LAYER))
        
        # Layer flags
        flags = cls.LAYER_FLAG_VISIBLE if layer.get('visible', True) else 0
        flags |= cls.LAYER_FLAG_EDITABLE
        f.write(struct.pack('<H', flags))
        
        f.write(struct.pack('<H', 0))  # Type (normal)
        f.write(struct.pack('<H', 0))  # Child level
        f.write(struct.pack('<H', 0))  # Default layer width
        f.write(struct.pack('<H', 0))  # Default layer height
        f.write(struct.pack('<H', 0))  # Blend mode (normal)
        f.write(struct.pack('<B', layer.get('opacity', 255)))
        f.write(b'\x00\x00\x00')  # Padding
        f.write(struct.pack('<H', name_len))
        f.write(name_bytes)
    
    @classmethod
    def _write_cel_chunk(cls, f: BinaryIO, layer_index: int, 
                         width: int, height: int, pixel_data: bytes) -> None:
        """Write cel chunk."""
        import zlib
        
        chunk_start = f.tell()
        
        # Compress pixel data
        compressed = zlib.compress(pixel_data)
        
        chunk_size = 6 + 26 + len(compressed)  # header + cel header + compressed data
        
        f.write(struct.pack('<I', chunk_size))
        f.write(struct.pack('<H', cls.CHUNK_CEL))
        
        f.write(struct.pack('<H', layer_index))  # Layer index
        f.write(struct.pack('<h', 0))  # X position
        f.write(struct.pack('<h', 0))  # Y position
        f.write(struct.pack('<B', 255))  # Opacity
        f.write(struct.pack('<H', 2))  # Cel type (compressed)
        f.write(b'\x00' * 7)  # For future
        f.write(struct.pack('<H', width))
        f.write(struct.pack('<H', height))
        f.write(compressed)
    
    @classmethod
    def load_to_canvas(cls, filepath: str, canvas) -> bool:
        """Load Aseprite file into canvas.
        
        Args:
            filepath: Path to .ase/.aseprite file
            canvas: Canvas object to populate
        
        Returns:
            True if successful
        """
        result = cls.read(filepath)
        if not result:
            return False
        
        header, layers, frames = result
        
        # Resize canvas
        canvas.width = header.width
        canvas.height = header.height
        canvas.layers.clear()
        
        # Create layers
        layer_map: Dict[int, 'Layer'] = {}
        for i, ase_layer in enumerate(layers):
            from engine.tools.pixel_art_editor.canvas import Layer
            layer = Layer(header.width, header.height, ase_layer.name)
            layer.visible = ase_layer.visible
            layer.opacity = ase_layer.opacity / 255.0
            canvas.layers.append(layer)
            layer_map[i] = layer
        
        # If no layers found, create default layer
        if not layers:
            from engine.tools.pixel_art_editor.canvas import Layer
            layer = Layer(header.width, header.height, "Layer 1")
            canvas.layers.append(layer)
            layer_map[0] = layer
        
        # Process cels from first frame
        if frames:
            for cel in frames[0].cels:
                if cel.layer_index in layer_map and cel.pixel_data:
                    layer = layer_map[cel.layer_index]
                    cls._apply_cel_to_layer(cel, layer, header)
        
        return True
    
    @classmethod
    def _apply_cel_to_layer(cls, cel: AseCel, layer, header: AseHeader) -> None:
        """Apply cel pixel data to layer."""
        from PIL import Image
        
        if cel.pixel_data:
            # Create image from pixel data
            if header.depth == 32:
                # RGBA
                mode = 'RGBA'
            elif header.depth == 16:
                # Grayscale + Alpha
                mode = 'LA'
            else:
                # Indexed
                mode = 'P'
            
            try:
                # For RGBA data
                if mode == 'RGBA' and len(cel.pixel_data) >= cel.width * cel.height * 4:
                    img = Image.frombytes('RGBA', (cel.width, cel.height), cel.pixel_data)
                    
                    # Paste into layer at cel position
                    layer.paste_image(img, cel.x, cel.y)
            except Exception as e:
                print(f"Error applying cel: {e}")
    
    @classmethod
    def save_from_canvas(cls, filepath: str, canvas) -> bool:
        """Save canvas to Aseprite file.
        
        Args:
            filepath: Output path
            canvas: Canvas to save
        
        Returns:
            True if successful
        """
        layers = []
        pixel_data = []
        
        for layer in canvas.layers:
            layer_info = {
                'name': layer.name,
                'visible': layer.visible,
                'opacity': int(layer.opacity * 255)
            }
            layers.append(layer_info)
            
            # Get pixel data from layer
            img = layer.get_image()
            if img:
                pixel_data.append(img.tobytes('raw', 'RGBA'))
            else:
                # Empty layer
                pixel_data.append(b'\x00' * (canvas.width * canvas.height * 4))
        
        return cls.write(filepath, canvas.width, canvas.height, layers, pixel_data)


__all__ = ["AsepriteFormat"]
