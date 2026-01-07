"""
InMemoryCacheAdapter: In-memory implementation of CachePort.
Dependencies: Domain.Ports.CachePort
"""

from typing import Any

from domain.ports.store.cache_port import CachePort


class InMemoryCacheAdapter(CachePort):
    """
    Simple in-memory cache using Python dict.
    No TTL support in this basic version, unbounded size.
    """

    def __init__(self):
        self._cache: dict[str, Any] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        if key in self._cache:
            self._hits += 1
            return self._cache[key]
        self._misses += 1
        return None

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        # TTL not implemented in simple version
        self._cache[key] = value

    def has(self, key: str) -> bool:
        return key in self._cache

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
        }
