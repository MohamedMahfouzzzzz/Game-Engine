# /**************************************************************************/
# /*  chunk_types.py                                                        */
# /**************************************************************************/

"""Chunk types for GES binary format.

The GES format uses a chunk-based structure similar to PNG and Aseprite.
Each chunk has a type, size, and CRC32 for integrity.
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Tuple
import struct
import zlib


class ChunkType(IntEnum):
    """Chunk type identifiers (4-byte codes)."""
    # Header chunks
    HEAD = 0x48454144  # 'HEAD' - File header
    VERS = 0x56455253  # 'VERS' - Version info
    
    # Document chunks
    DOCS = 0x444F4353  # 'DOCS' - Document info
    META = 0x4D455441  # 'META' - Metadata
    PALT = 0x50414C54  # 'PALT' - Palette
    
    # Layer chunks
    LAYR = 0x4C415952  # 'LAYR' - Layer definition
    LGRP = 0x4C475250  # 'LGRP' - Layer group
    
    # Frame/Cel chunks
    FRAME = 0x46524D45  # 'FRME' - Frame data
    CEL = 0x43454C20   # 'CEL ' - Cel image data
    LNKD = 0x4C4E4B44  # 'LNKD' - Linked cel
    
    # Animation chunks
    TAGS = 0x54414753  # 'TAGS' - Frame tags
    SLCE = 0x534C4345  # 'SLCE' - Slices
    
    # Image chunks
    PXLS = 0x50584C53  # 'PXLS' - Raw pixel data
    TILE = 0x54494C45  # 'TILE' - Tilemap data
    
    # End chunk
    END = 0x454E4420   # 'END ' - File end


@dataclass
class ChunkHeader:
    """Header for each chunk in the file."""
    type_code: int      # 4 bytes - Chunk type
    size: int           # 4 bytes - Data size (excluding header)
    crc32: int          # 4 bytes - CRC32 of data
    
    STRUCT_FORMAT = '<III'  # Little-endian, 3 unsigned ints
    SIZE = 12  # bytes
    
    @classmethod
    def from_type(cls, chunk_type: ChunkType, data: bytes) -> 'ChunkHeader':
        """Create header from type and data."""
        return cls(
            type_code=int(chunk_type),
            size=len(data),
            crc32=zlib.crc32(data) & 0xFFFFFFFF
        )
    
    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        return struct.pack(self.STRUCT_FORMAT, self.type_code, self.size, self.crc32)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'ChunkHeader':
        """Deserialize from bytes."""
        type_code, size, crc32 = struct.unpack(cls.STRUCT_FORMAT, data)
        return cls(type_code, size, crc32)
    
    def verify_crc(self, data: bytes) -> bool:
        """Verify data integrity."""
        return (zlib.crc32(data) & 0xFFFFFFFF) == self.crc32
    
    @property
    def type_name(self) -> str:
        """Get 4-character type name."""
        return struct.pack('<I', self.type_code).decode('ascii', errors='replace')


# Magic number and version
GES_MAGIC = b'GES\x00'  # 4 bytes
GES_VERSION_MAJOR = 1
GES_VERSION_MINOR = 0
GES_VERSION_PATCH = 0

# Compression types
class CompressionType(IntEnum):
    """Compression algorithm identifiers."""
    NONE = 0
    ZLIB = 1
    ZSTD = 2  # If available


# Color mode identifiers
class ColorModeID(IntEnum):
    """Color mode identifiers for binary format."""
    RGBA = 0
    GRAYSCALE = 1
    INDEXED = 2
