from __future__ import annotations

from typing import Any
import hashlib
    from PIL import Image
from ....value_objects.compositor import CachedLayer


"""
LayerCache: Caches static render layers for reuse across frames.
Dependencies: PIL Image
"""



try:

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False



class LayerCache:
    """
    Caches static render layers to avoid redundant rendering.

    Used for UI chrome, backgrounds, and other elements that don't change per frame.
    """

    def __init__(self, max_size_mb: int = 100):
        if not HAS_PILLOW:
            raise ImportError("Pillow required")

        self._cache: dict[str, CachedLayer] = {}
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._current_size_bytes = 0

    def get(self, key: str) -> Image.Image | None:
        """Get cached layer by key."""
        if key in self._cache:
            return self._cache[key].image.copy()
        return None

    def set(self, key: str, image: Image.Image) -> None:
        """Cache a layer image."""
        # Calculate image size
        image_size = image.width * image.height * len(image.getbands())

        # Check if cache is full
        if self._current_size_bytes + image_size > self._max_size_bytes:
            self._evict_oldest()

        # Generate hash for change detection
        img_hash = self._hash_image(image)

        cached = CachedLayer(
            name=key, image=image.copy(), width=image.width, height=image.height, hash=img_hash
        )

        self._cache[key] = cached
        self._current_size_bytes += image_size

    def has(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache

    def invalidate(self, key: str) -> None:
        """Remove a specific key from cache."""
        if key in self._cache:
            cached = self._cache.pop(key)
            image_size = cached.width * cached.height * 4  # Assume RGBA
            self._current_size_bytes -= image_size

    def clear(self) -> None:
        """Clear all cached layers."""
        self._cache.clear()
        self._current_size_bytes = 0

    def _evict_oldest(self) -> None:
        """Evict oldest cached layer to free memory."""
        if self._cache:
            oldest_key = next(iter(self._cache))
            self.invalidate(oldest_key)

    def _hash_image(self, image: Image.Image) -> str:
        """Generate hash for image content."""
        return hashlib.md5(image.tobytes()[:1024]).hexdigest()

    @property
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "entries": len(self._cache),
            "size_mb": round(self._current_size_bytes / (1024 * 1024), 2),
            "max_size_mb": self._max_size_bytes // (1024 * 1024),
        }