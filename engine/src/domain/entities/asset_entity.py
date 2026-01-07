"""
AssetEntity: Abstraction of a media resource.
Decouples the logic of 'what file to load' from 'how it is displayed'.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..value_objects.geometry import Dimensions
from ..value_objects.resource import FilePath
from ..value_objects.timing import Duration


class AssetType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LOTTIE = "lottie"
    UNKNOWN = "unknown"


@dataclass
class AssetMetadata:
    """Metadata describing the asset properties."""

    dimensions: Dimensions = field(default_factory=lambda: Dimensions(0, 0))
    format: str = ""
    size_bytes: int = 0
    duration: Duration = field(default_factory=lambda: Duration.ZERO)  # For video/audio

    @property
    def width(self) -> int:
        return self.dimensions.width

    @property
    def height(self) -> int:
        return self.dimensions.height


@dataclass
class AssetEntity:
    """
    Domain Entity representing a raw media asset context.
    Does NOT hold the actual heavy data by default, but manages its lifecycle.
    """

    id: str
    type: AssetType
    source_path: FilePath  # URI, FilePath, or Hash
    metadata: AssetMetadata

    # Internal cache for loaded data (e.g. PIL Image object)
    # Excluded from repr to avoid clutter
    _cached_data: Any | None = field(default=None, repr=False)

    def is_loaded(self) -> bool:
        """Check if asset data is currently in memory."""
        return self._cached_data is not None

    def set_data(self, data: Any) -> None:
        """Inject loaded data into this entity."""
        self._cached_data = data

    def get_data(self) -> Any | None:
        """Retrieve cached data."""
        return self._cached_data

    def release(self) -> None:
        """Release memory held by this asset."""
        self._cached_data = None
