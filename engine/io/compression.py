# /**************************************************************************/
# /*  compression.py                                                        */
# /**************************************************************************/

"""Compression utilities for binary format.

Supports multiple compression algorithms with fallback.
"""

import zlib
from typing import Optional

# Try to import zstandard for better compression
try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False
    zstd = None

from .chunk_types import CompressionType


def compress_data(data: bytes, method: CompressionType = CompressionType.ZLIB) -> tuple:
    """Compress data using specified method.
    
    Returns:
        Tuple of (compressed_data, actual_method)
    """
    if method == CompressionType.NONE or len(data) < 100:
        # Don't compress small data
        return data, CompressionType.NONE
    
    if method == CompressionType.ZSTD and HAS_ZSTD:
        try:
            cctx = zstd.ZstdCompressor()
            compressed = cctx.compress(data)
            return compressed, CompressionType.ZSTD
        except Exception:
            # Fall back to zlib
            pass
    
    # Default to zlib
    compressed = zlib.compress(data, level=6)
    return compressed, CompressionType.ZLIB


def decompress_data(data: bytes, method: CompressionType) -> Optional[bytes]:
    """Decompress data using specified method.
    
    Returns:
        Decompressed data or None if failed
    """
    if method == CompressionType.NONE:
        return data
    
    if method == CompressionType.ZSTD and HAS_ZSTD:
        try:
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(data)
        except Exception:
            return None
    
    if method == CompressionType.ZLIB:
        try:
            return zlib.decompress(data)
        except Exception:
            return None
    
    return None


def get_compression_ratio(original: bytes, compressed: bytes) -> float:
    """Calculate compression ratio.
    
    Returns:
        Ratio (1.0 = no compression, 0.5 = 50% size)
    """
    if len(original) == 0:
        return 1.0
    return len(compressed) / len(original)


def auto_compress(data: bytes, threshold: float = 0.9) -> tuple:
    """Automatically choose best compression method.
    
    Args:
        data: Data to compress
        threshold: Minimum ratio to bother compressing
    
    Returns:
        Tuple of (compressed_data, method_used)
    """
    if len(data) < 100:
        return data, CompressionType.NONE
    
    # Try zlib first (fast)
    zlib_data, _ = compress_data(data, CompressionType.ZLIB)
    zlib_ratio = get_compression_ratio(data, zlib_data)
    
    if zlib_ratio <= threshold:
        return zlib_data, CompressionType.ZLIB
    
    # Try zstd if available
    if HAS_ZSTD:
        zstd_data, _ = compress_data(data, CompressionType.ZSTD)
        zstd_ratio = get_compression_ratio(data, zstd_data)
        
        if zstd_ratio < zlib_ratio:
            return zstd_data, CompressionType.ZSTD
    
    # Use zlib if it's good enough
    if zlib_ratio < 1.0:
        return zlib_data, CompressionType.ZLIB
    
    # No compression
    return data, CompressionType.NONE
