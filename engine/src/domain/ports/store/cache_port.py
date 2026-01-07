"""
CachePort: Interface for key-value caching operations.
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod
from typing import Any


class CachePort(ABC):
    """
    Port interface for key-value caching.

    Abstracts caching to allow swapping between in-memory,
    disk-based, or distributed cache backends.

    Adapters implementing this port:
    - memory_cache_adapter.py (in-process dict)
    - lru_cache_adapter.py (bounded memory)
    - redis_cache_adapter.py (distributed)
    """

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """
        Retrieve value by key.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """
        Store value with key.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl_seconds: Optional time-to-live in seconds.
        """
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key to check.

        Returns:
            True if key exists.
        """
        pass

    @abstractmethod
    def invalidate(self, key: str) -> None:
        """
        Remove a specific key from cache.

        Args:
            key: Cache key to remove.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Remove all entries from cache."""
        pass

    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with: entries, size_bytes, hit_rate, etc.
        """
        pass
