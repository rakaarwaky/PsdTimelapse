"""
Resolution Value Object: Video resolution with preset recognition.
Part of visual category - output resolution configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import ClassVar

RESOLUTION_PRESETS: dict[tuple[int, int], str] = {
    (1280, 720): "720p HD",
    (1920, 1080): "1080p Full HD",
    (2560, 1440): "1440p QHD",
    (3840, 2160): "4K UHD",
    (7680, 4320): "8K UHD",
}


@dataclass(frozen=True)
class Resolution:
    """Video resolution with common preset recognition."""

    width: int
    height: int
    name: str | None = None

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Resolution dimensions must be positive")

        if self.name is None:
            detected = self._detect_name()
            object.__setattr__(self, "name", detected)

    def _detect_name(self) -> str:
        """Detect resolution name from common presets."""
        return RESOLUTION_PRESETS.get((self.width, self.height), f"{self.height}p")

    @property
    def aspect_ratio(self) -> str:
        """Human-readable aspect ratio."""
        g = gcd(self.width, self.height)
        return f"{self.width // g}:{self.height // g}"

    @property
    def aspect_ratio_float(self) -> float:
        """Numeric aspect ratio (width/height)."""
        return self.width / self.height

    @property
    def megapixels(self) -> float:
        """Total megapixels."""
        return (self.width * self.height) / 1_000_000

    @property
    def total_pixels(self) -> int:
        """Total pixel count."""
        return self.width * self.height

    def as_tuple(self) -> tuple[int, int]:
        """Return as (width, height) tuple."""
        return (self.width, self.height)

    def is_hd(self) -> bool:
        """Check if HD or higher (720p+)."""
        return self.height >= 720

    def is_full_hd(self) -> bool:
        """Check if Full HD or higher (1080p+)."""
        return self.height >= 1080

    def is_4k(self) -> bool:
        """Check if 4K or higher."""
        return self.width >= 3840

    def format(self) -> str:
        """Format as string, e.g., '1920x1080 (1080p Full HD)'."""
        return f"{self.width}x{self.height} ({self.name})"

    def format_short(self) -> str:
        """Format as short string, e.g., '1080p'."""
        return self.name or f"{self.height}p"

    # Class-level presets (assigned after class definition)
    HD: ClassVar[Resolution]
    FULL_HD: ClassVar[Resolution]
    QHD: ClassVar[Resolution]
    UHD_4K: ClassVar[Resolution]


# Standard presets
Resolution.HD = Resolution(1280, 720)
Resolution.FULL_HD = Resolution(1920, 1080)
Resolution.QHD = Resolution(2560, 1440)
Resolution.UHD_4K = Resolution(3840, 2160)
