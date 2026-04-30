# /**************************************************************************/
# /*  io/__init__.py                                                        */
# /**************************************************************************/

"""I/O module for native binary format (.ges) and export formats.

Provides fast, compact binary serialization for pixel art documents.
"""

from .binary_format import BinaryFormat, GESReader, GESWriter
from .chunk_types import ChunkType, ChunkHeader
from .compression import compress_data, decompress_data

__all__ = [
    "BinaryFormat",
    "GESReader",
    "GESWriter", 
    "ChunkType",
    "ChunkHeader",
    "compress_data",
    "decompress_data",
]
