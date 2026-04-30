# /**************************************************************************/
# /*  resources.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from collections import OrderedDict
from typing import Any, Dict, Optional


# Maximum cached resources to prevent memory leaks
MAX_CACHED_RESOURCES = 500


class ResourceManager:
    """Resource registry with LRU cache to prevent memory leaks."""

    def __init__(self, max_resources: int = MAX_CACHED_RESOURCES) -> None:
        self._max_resources = max_resources
        # Use OrderedDict for LRU cache behavior
        self._resources: OrderedDict[str, Any] = OrderedDict()
        self._source_paths: Dict[str, str] = {}

    def _enforce_cache_limit(self) -> None:
        """Remove oldest resources if cache exceeds max limit."""
        while len(self._resources) > self._max_resources:
            # Remove oldest item (first in OrderedDict)
            oldest_key, _ = self._resources.popitem(last=False)
            # Also clean up source path if exists
            self._source_paths.pop(oldest_key, None)

    def register(self, key: str, resource: Any) -> None:
        """Register a resource with LRU cache management."""
        # Move to end if already cached (marks as recently used)
        if key in self._resources:
            self._resources.move_to_end(key)
        else:
            # Enforce limit before adding new
            if len(self._resources) >= self._max_resources:
                self._enforce_cache_limit()
            self._resources[key] = resource

    def register_with_source(self, key: str, resource: Any, source_path: str) -> None:
        """Register a resource with its source path and LRU cache management."""
        self.register(key, resource)
        self._source_paths[key] = source_path

    def get(self, key: str) -> Optional[Any]:
        """Get a resource and mark it as recently used."""
        if key in self._resources:
            # Move to end to mark as recently used
            self._resources.move_to_end(key)
            return self._resources[key]
        return None

    def get_source(self, key: str) -> Optional[str]:
        return self._source_paths.get(key)

    def to_dict(self) -> Dict[str, str]:
        return {k: type(v).__name__ for k, v in self._resources.items()}

    def clear(self) -> None:
        """Clear all cached resources."""
        self._resources.clear()
        self._source_paths.clear()

    @property
    def cache_size(self) -> int:
        """Current number of cached resources."""
        return len(self._resources)
