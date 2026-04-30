# /**************************************************************************/
# /*  cache_node_path.py                                                    */
# /**************************************************************************/

"""CacheNodePath - Utility for caching node path lookups."""

from typing import Optional, Dict, Any


class CacheNodePath:
    """Caches node path lookups for animation performance."""
    
    def __init__(self, max_size: int = 100):
        self._cache: Dict[str, Any] = {}
        self._max_size = max(10, max_size)
    
    def get_cached(self, path: str) -> Optional[Any]:
        return self._cache.get(path)
    
    def set_cached(self, path: str, node: Any) -> None:
        if len(self._cache) >= self._max_size:
            if self._cache:
                oldest = next(iter(self._cache))
                del self._cache[oldest]
        self._cache[path] = node
    
    def has_cached(self, path: str) -> bool:
        return path in self._cache
    
    def clear(self) -> None:
        self._cache.clear()
    
    def invalidate(self, path: str) -> None:
        if path in self._cache:
            del self._cache[path]
    
    def get_cache_size(self) -> int:
        return len(self._cache)
    
    def get_max_size(self) -> int:
        return self._max_size
    
    def set_max_size(self, size: int) -> None:
        self._max_size = max(10, size)
        while len(self._cache) > self._max_size:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
    
    def __repr__(self) -> str:
        return f"CacheNodePath(size={len(self._cache)}/{self._max_size})"
