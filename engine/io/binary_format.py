# /**************************************************************************/
# /*  binary_format.py                                                      */
# /**************************************************************************/

"""Native binary format (.ges) for Game Engine Studio pixel art.

The GES format is a fast, compact binary format inspired by PNG and Aseprite.
It uses a chunk-based structure with compression and integrity checking.

Format structure:
    GES\0 (magic) + version (4 bytes)
    [chunks...]
    END chunk

Each chunk:
    [type: 4 bytes][size: 4 bytes][crc32: 4 bytes][data: size bytes]
"""

import struct
import io
from typing import Optional, BinaryIO, List, Dict, Any
from pathlib import Path

from engine.tools.pixel_art_editor.core import (
    Document, Sprite, Layer, LayerGroup, Cel, LinkedCel,
    ImageBuffer, Palette, Tag, Slice, Frame, BlendMode
)
from engine.tools.pixel_art_editor.core.image_buffer import ColorMode

from .chunk_types import (
    ChunkType, ChunkHeader, GES_MAGIC,
    GES_VERSION_MAJOR, GES_VERSION_MINOR, GES_VERSION_PATCH,
    ColorModeID
)
from .compression import compress_data, decompress_data, auto_compress


class GESWriter:
    """Writer for GES binary format."""
    
    def __init__(self, compression: str = "auto"):
        self.compression = compression
    
    def write(self, document: Document, filepath: str) -> bool:
        """Write document to GES file.
        
        Args:
            document: Document to save
            filepath: Output file path
        
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'wb') as f:
                self._write_header(f)
                self._write_document(f, document)
                self._write_end(f)
            return True
        except Exception as e:
            print(f"Error writing GES file: {e}")
            return False
    
    def _write_header(self, f: BinaryIO) -> None:
        """Write file header."""
        # Magic number
        f.write(GES_MAGIC)
        
        # Version (major, minor, patch, reserved)
        f.write(struct.pack('<BBBB',
            GES_VERSION_MAJOR,
            GES_VERSION_MINOR,
            GES_VERSION_PATCH,
            0
        ))
    
    def _write_chunk(self, f: BinaryIO, chunk_type: ChunkType, data: bytes) -> None:
        """Write a chunk to file."""
        header = ChunkHeader.from_type(chunk_type, data)
        f.write(header.to_bytes())
        f.write(data)
    
    def _write_document(self, f: BinaryIO, document: Document) -> None:
        """Write document data."""
        sprite = document.sprite
        
        # Write document info
        self._write_document_info(f, document)
        
        # Write palette
        self._write_palette(f, sprite.palette)
        
        # Write layers
        for layer in sprite.get_layers():
            self._write_layer(f, layer)
        
        # Write frames
        for i in range(sprite.frame_count):
            frame = sprite.get_frame(i)
            if frame:
                self._write_frame(f, frame)
        
        # Write cels
        for layer in sprite.get_layers():
            for cel in layer.get_cels():
                self._write_cel(f, cel)
        
        # Write tags
        for tag in sprite.get_tags():
            self._write_tag(f, tag)
        
        # Write slices
        for slice_obj in sprite.get_slices():
            self._write_slice(f, slice_obj)
    
    def _write_document_info(self, f: BinaryIO, document: Document) -> None:
        """Write document info chunk."""
        sprite = document.sprite
        
        # Build document info
        data = struct.pack('<IIII',
            sprite.width,
            sprite.height,
            sprite.layer_count,
            sprite.frame_count
        )
        
        # Color mode
        color_mode_id = {
            ColorMode.RGBA: ColorModeID.RGBA,
            ColorMode.GRAYSCALE: ColorModeID.GRAYSCALE,
            ColorMode.INDEXED: ColorModeID.INDEXED,
        }.get(sprite.color_mode, ColorModeID.RGBA)
        
        data += struct.pack('<I', int(color_mode_id))
        
        # Grid bounds
        data += struct.pack('<iiii', *sprite.grid_bounds)
        
        # Metadata
        meta = document.get_metadata()
        name_bytes = document.name.encode('utf-8')
        data += struct.pack('<I', len(name_bytes))
        data += name_bytes
        
        # Custom data
        import json
        custom_json = json.dumps(document.custom_data).encode('utf-8')
        data += struct.pack('<I', len(custom_json))
        data += custom_json
        
        # Compress document info
        compressed, method = auto_compress(data)
        data = struct.pack('<I', int(method)) + compressed
        
        self._write_chunk(f, ChunkType.DOCS, data)
    
    def _write_palette(self, f: BinaryIO, palette: Palette) -> None:
        """Write palette chunk."""
        count = palette.color_count
        data = struct.pack('<I', count)
        
        for i in range(count):
            entry = palette.get_entry(i)
            if entry:
                data += struct.pack('<BBBB',
                    entry.red,
                    entry.green,
                    entry.blue,
                    entry.alpha
                )
                # Name (optional)
                name = (entry.name or '').encode('utf-8')
                data += struct.pack('<H', len(name)) + name
            else:
                data += struct.pack('<BBBB', 0, 0, 0, 255) + struct.pack('<H', 0)
        
        self._write_chunk(f, ChunkType.PALT, data)
    
    def _write_layer(self, f: BinaryIO, layer: Layer) -> None:
        """Write layer chunk."""
        if isinstance(layer, LayerGroup):
            # Layer group
            name = layer.name.encode('utf-8')
            data = struct.pack('<I', layer.id)
            data += struct.pack('<H', len(name)) + name
            data += struct.pack('<BBBB',
                int(layer.visible),
                int(layer.editable),
                int(layer.is_background),
                int(layer.collapsed if hasattr(layer, 'collapsed') else False)
            )
            data += struct.pack('<B', layer.opacity)
            data += struct.pack('<I', layer.blend_mode.value)
            data += struct.pack('<I', len(layer.children))
            
            self._write_chunk(f, ChunkType.LGRP, data)
        else:
            # Regular layer
            name = layer.name.encode('utf-8')
            data = struct.pack('<I', layer.id)
            data += struct.pack('<H', len(name)) + name
            data += struct.pack('<BBBB',
                int(layer.visible),
                int(layer.editable),
                int(layer.is_background),
                0  # Reserved
            )
            data += struct.pack('<B', layer.opacity)
            data += struct.pack('<I', layer.blend_mode.value)
            
            self._write_chunk(f, ChunkType.LAYR, data)
    
    def _write_frame(self, f: BinaryIO, frame: Frame) -> None:
        """Write frame chunk."""
        data = struct.pack('<II',
            frame.index,
            frame.duration_ms
        )
        self._write_chunk(f, ChunkType.FRAME, data)
    
    def _write_cel(self, f: BinaryIO, cel: Cel) -> None:
        """Write cel chunk."""
        if isinstance(cel, LinkedCel):
            # Linked cel
            data = struct.pack('<IIIff',
                cel.layer_id,
                cel.frame,
                cel._linked_cel.frame if cel._linked_cel else 0,
                cel.x,
                cel.y
            )
            self._write_chunk(f, ChunkType.LNKD, data)
        else:
            # Regular cel with image
            data = struct.pack('<IIIff',
                cel.layer_id,
                cel.frame,
                int(cel.opacity * 255),
                cel.x,
                cel.y
            )
            
            # Image data
            if cel.image:
                img = cel.image.to_pil()
                img_bytes = img.tobytes()
                data += struct.pack('<II', img.width, img.height)
                
                # Compress pixel data
                compressed, method = auto_compress(img_bytes)
                data += struct.pack('<I', int(method))
                data += struct.pack('<I', len(compressed))
                data += compressed
            else:
                data += struct.pack('<II', 0, 0)
            
            self._write_chunk(f, ChunkType.CEL, data)
    
    def _write_tag(self, f: BinaryIO, tag: Tag) -> None:
        """Write tag chunk."""
        name = tag.name.encode('utf-8')
        data = struct.pack('<H', len(name)) + name
        data += struct.pack('<III',
            tag.from_frame,
            tag.to_frame,
            int(tag.repeat)
        )
        data += struct.pack('<BBB', *tag.color)
        self._write_chunk(f, ChunkType.TAGS, data)
    
    def _write_slice(self, f: BinaryIO, slice_obj: Slice) -> None:
        """Write slice chunk."""
        name = slice_obj.name.encode('utf-8')
        data = struct.pack('<H', len(name)) + name
        
        # Number of keys
        keys = list(slice_obj._keys.values())
        data += struct.pack('<I', len(keys))
        
        for key in keys:
            data += struct.pack('<iiii',
                key.frame,
                key.x,
                key.y,
                key.width,
                key.height
            )
            # Center (9-patch)
            has_center = key.center_x is not None
            data += struct.pack('<B', int(has_center))
            if has_center:
                data += struct.pack('<iiii',
                    key.center_x,
                    key.center_y,
                    key.center_width,
                    key.center_height
                )
        
        self._write_chunk(f, ChunkType.SLCE, data)
    
    def _write_end(self, f: BinaryIO) -> None:
        """Write end chunk."""
        self._write_chunk(f, ChunkType.END, b'')


class GESReader:
    """Reader for GES binary format."""
    
    def __init__(self):
        self._warnings: List[str] = []
    
    @property
    def warnings(self) -> List[str]:
        """Get list of warnings from last read."""
        return self._warnings.copy()
    
    def read(self, filepath: str) -> Optional[Document]:
        """Read document from GES file.
        
        Args:
            filepath: Input file path
        
        Returns:
            Document or None if failed
        """
        self._warnings.clear()
        
        try:
            with open(filepath, 'rb') as f:
                return self._read(f)
        except Exception as e:
            print(f"Error reading GES file: {e}")
            return None
    
    def _read(self, f: BinaryIO) -> Optional[Document]:
        """Read document from file stream."""
        # Read header
        if not self._read_header(f):
            return None
        
        # Read chunks
        chunks = self._read_chunks(f)
        
        # Build document from chunks
        return self._build_document(chunks)
    
    def _read_header(self, f: BinaryIO) -> bool:
        """Read and validate file header."""
        magic = f.read(4)
        if magic != GES_MAGIC:
            print(f"Invalid magic number: {magic}")
            return False
        
        version = f.read(4)
        major, minor, patch, _ = struct.unpack('<BBBB', version)
        
        if major > GES_VERSION_MAJOR:
            print(f"Warning: File version {major}.{minor} > reader version")
        
        return True
    
    def _read_chunks(self, f: BinaryIO) -> List[tuple]:
        """Read all chunks from file."""
        chunks = []
        
        while True:
            header_data = f.read(ChunkHeader.SIZE)
            if len(header_data) < ChunkHeader.SIZE:
                break
            
            header = ChunkHeader.from_bytes(header_data)
            data = f.read(header.size)
            
            if len(data) < header.size:
                self._warnings.append(f"Truncated chunk: {header.type_name}")
                break
            
            # Verify CRC
            if not header.verify_crc(data):
                self._warnings.append(f"CRC mismatch: {header.type_name}")
            
            chunks.append((header.type_code, data))
            
            # Stop at END chunk
            if header.type_code == int(ChunkType.END):
                break
        
        return chunks
    
    def _build_document(self, chunks: List[tuple]) -> Optional[Document]:
        """Build document from chunks."""
        # Find document info
        doc_data = None
        for type_code, data in chunks:
            if type_code == int(ChunkType.DOCS):
                doc_data = data
                break
        
        if not doc_data:
            print("No document info chunk found")
            return None
        
        # Parse document info
        document = self._parse_document_info(doc_data)
        if not document:
            return None
        
        sprite = document.sprite
        
        # Clear default layer and frame that were created during initialization
        # (we'll load the actual layers and frames from file)
        sprite._layers.clear()
        sprite._frames._frames.clear()
        
        # Parse palette
        for type_code, data in chunks:
            if type_code == int(ChunkType.PALT):
                palette = self._parse_palette(data)
                if palette:
                    sprite.palette = palette
                break
        
        # Parse layers
        layers_by_id = {}
        for type_code, data in chunks:
            if type_code == int(ChunkType.LAYR):
                layer = self._parse_layer(data, sprite)
                if layer:
                    layers_by_id[layer.id] = layer
            elif type_code == int(ChunkType.LGRP):
                layer = self._parse_layer_group(data, sprite)
                if layer:
                    layers_by_id[layer.id] = layer
        
        # Parse frames
        for type_code, data in chunks:
            if type_code == int(ChunkType.FRAME):
                frame = self._parse_frame(data)
                if frame:
                    sprite._frames.add_frame(frame)
        
        # Parse cels
        for type_code, data in chunks:
            if type_code == int(ChunkType.CEL):
                cel = self._parse_cel(data)
                if cel and cel.layer_id in layers_by_id:
                    layers_by_id[cel.layer_id].set_cel(cel.frame, cel)
            elif type_code == int(ChunkType.LNKD):
                cel = self._parse_linked_cel(data)
                if cel and cel.layer_id in layers_by_id:
                    layers_by_id[cel.layer_id].set_cel(cel.frame, cel)
        
        # Parse tags
        for type_code, data in chunks:
            if type_code == int(ChunkType.TAGS):
                tag = self._parse_tag(data)
                if tag:
                    sprite.add_tag(tag)
        
        # Parse slices
        for type_code, data in chunks:
            if type_code == int(ChunkType.SLCE):
                slice_obj = self._parse_slice(data)
                if slice_obj:
                    sprite.add_slice(slice_obj)
        
        return document
    
    def _parse_document_info(self, data: bytes) -> Optional[Document]:
        """Parse document info chunk."""
        try:
            # Decompress if needed
            method = struct.unpack('<I', data[:4])[0]
            compressed = data[4:]
            decompressed = decompress_data(compressed, method)
            
            if decompressed is None:
                decompressed = compressed
            
            data = decompressed
            offset = 0
            
            # Read dimensions
            width, height, layer_count, frame_count = struct.unpack_from('<IIII', data, offset)
            offset += 16
            
            # Read color mode
            color_mode_id = struct.unpack_from('<I', data, offset)[0]
            offset += 4
            
            # Grid bounds
            grid_x, grid_y, grid_w, grid_h = struct.unpack_from('<iiii', data, offset)
            offset += 16
            
            # Name
            name_len = struct.unpack_from('<I', data, offset)[0]
            offset += 4
            name = data[offset:offset + name_len].decode('utf-8')
            offset += name_len
            
            # Custom data
            custom_len = struct.unpack_from('<I', data, offset)[0]
            offset += 4
            custom_json = data[offset:offset + custom_len].decode('utf-8')
            
            import json
            custom_data = json.loads(custom_json) if custom_json else {}
            
            # Create document
            document = Document(width, height, name)
            document.custom_data = custom_data
            document.sprite.grid_bounds = (grid_x, grid_y, grid_w, grid_h)
            
            return document
            
        except Exception as e:
            print(f"Error parsing document info: {e}")
            return None
    
    def _parse_palette(self, data: bytes) -> Optional[Palette]:
        """Parse palette chunk."""
        try:
            count = struct.unpack_from('<I', data, 0)[0]
            offset = 4
            
            from engine.tools.pixel_art_editor.core.palette import PaletteEntry
            palette = Palette("Palette", 0)
            
            for i in range(count):
                r, g, b, a = struct.unpack_from('<BBBB', data, offset)
                offset += 4
                
                name_len = struct.unpack_from('<H', data, offset)[0]
                offset += 2
                name = data[offset:offset + name_len].decode('utf-8')
                offset += name_len
                
                entry = PaletteEntry(r, g, b, a, name)
                palette._entries.append(entry)
            
            return palette
            
        except Exception as e:
            print(f"Error parsing palette: {e}")
            return None
    
    def _parse_layer(self, data: bytes, sprite) -> Optional[Layer]:
        """Parse layer chunk."""
        try:
            layer_id = struct.unpack_from('<I', data, 0)[0]
            offset = 4
            
            name_len = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            name = data[offset:offset + name_len].decode('utf-8')
            offset += name_len
            
            visible, editable, is_bg, _ = struct.unpack_from('<BBBB', data, offset)
            offset += 4
            
            opacity = struct.unpack_from('<B', data, offset)[0]
            offset += 1
            
            blend_mode_val = struct.unpack_from('<I', data, offset)[0]
            
            # Create layer
            layer = sprite.add_layer(name, bool(is_bg))
            layer.id = layer_id
            layer.visible = bool(visible)
            layer.editable = bool(editable)
            layer.opacity = opacity
            layer.blend_mode = BlendMode(blend_mode_val)
            
            return layer
            
        except Exception as e:
            print(f"Error parsing layer: {e}")
            return None
    
    def _parse_layer_group(self, data: bytes, sprite) -> Optional[LayerGroup]:
        """Parse layer group chunk."""
        # TODO: Implement layer groups
        return self._parse_layer(data, sprite)
    
    def _parse_frame(self, data: bytes) -> Optional[Frame]:
        """Parse frame chunk."""
        try:
            index, duration = struct.unpack_from('<II', data, 0)
            return Frame(index, duration)
        except Exception:
            return None
    
    def _parse_cel(self, data: bytes) -> Optional[Cel]:
        """Parse cel chunk."""
        try:
            layer_id, frame, opacity, x, y = struct.unpack_from('<IIIff', data, 0)
            offset = 20
            
            width, height = struct.unpack_from('<II', data, offset)
            offset += 8
            
            cel = Cel(layer_id, frame, width, height, int(x), int(y), opacity / 255.0)
            
            if width > 0 and height > 0:
                # Read compressed image data
                method = struct.unpack_from('<I', data, offset)[0]
                offset += 4
                
                compressed_len = struct.unpack_from('<I', data, offset)[0]
                offset += 4
                
                compressed = data[offset:offset + compressed_len]
                img_data = decompress_data(compressed, method)
                
                if img_data:
                    # Create image from raw data
                    from PIL import Image
                    img = Image.frombytes('RGBA', (width, height), img_data)
                    buffer = ImageBuffer(width, height, ColorMode.RGBA)
                    buffer.from_pil(img)
                    cel.image = buffer
            
            return cel
            
        except Exception as e:
            print(f"Error parsing cel: {e}")
            return None
    
    def _parse_linked_cel(self, data: bytes) -> Optional[LinkedCel]:
        """Parse linked cel chunk."""
        # TODO: Implement linked cels
        return self._parse_cel(data)
    
    def _parse_tag(self, data: bytes) -> Optional[Tag]:
        """Parse tag chunk."""
        try:
            name_len = struct.unpack_from('<H', data, 0)[0]
            offset = 2
            
            name = data[offset:offset + name_len].decode('utf-8')
            offset += name_len
            
            from_frame, to_frame, repeat = struct.unpack_from('<III', data, offset)
            offset += 12
            
            r, g, b = struct.unpack_from('<BBB', data, offset)
            
            from engine.tools.pixel_art_editor.core.tag import TagRepeat
            return Tag(name, from_frame, to_frame, (r, g, b), TagRepeat(repeat))
            
        except Exception:
            return None
    
    def _parse_slice(self, data: bytes) -> Optional[Slice]:
        """Parse slice chunk."""
        # TODO: Implement slices
        return None


class BinaryFormat:
    """High-level interface for GES binary format."""
    
    EXTENSION = '.ges'
    
    @staticmethod
    def save(document: Document, filepath: str, compression: str = "auto") -> bool:
        """Save document to GES file."""
        writer = GESWriter(compression)
        return writer.write(document, filepath)
    
    @staticmethod
    def load(filepath: str) -> Optional[Document]:
        """Load document from GES file."""
        reader = GESReader()
        return reader.read(filepath)
    
    @staticmethod
    def get_info(filepath: str) -> Optional[Dict[str, Any]]:
        """Get quick info about a GES file without loading it."""
        try:
            with open(filepath, 'rb') as f:
                magic = f.read(4)
                if magic != GES_MAGIC:
                    return None
                
                version = f.read(4)
                major, minor, patch, _ = struct.unpack('<BBBB', version)
                
                # Read document chunk
                header_data = f.read(ChunkHeader.SIZE)
                if len(header_data) < ChunkHeader.SIZE:
                    return None
                
                header = ChunkHeader.from_bytes(header_data)
                if header.type_code != int(ChunkType.DOCS):
                    return None
                
                data = f.read(header.size)
                
                # Parse basic info
                method = struct.unpack('<I', data[:4])[0]
                compressed = data[4:]
                decompressed = decompress_data(compressed, method)
                
                if decompressed is None:
                    return None
                
                width, height, layer_count, frame_count = struct.unpack_from('<IIII', decompressed, 0)
                
                return {
                    'version': f"{major}.{minor}.{patch}",
                    'width': width,
                    'height': height,
                    'layers': layer_count,
                    'frames': frame_count,
                    'size': Path(filepath).stat().st_size,
                }
                
        except Exception:
            return None
