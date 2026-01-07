"""
Dimensions Value Object: Immutable width and height pair.
Part of geometry category - size and dimension handling.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Dimensions:
    """Immutable width and height pair."""

    width: int
    height: int

    def __post_init__(self):
        if self.width <= 0:
            raise ValueError(f"Width must be positive: {self.width}")
        if self.height <= 0:
            raise ValueError(f"Height must be positive: {self.height}")

    @property
    def aspect_ratio(self) -> float:
        """Width / Height ratio."""
        return self.width / self.height

    @property
    def total_pixels(self) -> int:
        """Total pixel count."""
        return self.width * self.height

    def as_tuple(self) -> tuple[int, int]:
        """Return as (width, height) tuple."""
        return (self.width, self.height)

    def scale(self, factor: float) -> Dimensions:
        """Scale dimensions by factor."""
        return Dimensions(
            width=max(1, int(self.width * factor)), height=max(1, int(self.height * factor))
        )

    def fit_within(self, max_dims: Dimensions) -> Dimensions:
        """Scale down to fit within max dimensions, preserving aspect ratio."""
        scale_w = max_dims.width / self.width
        scale_h = max_dims.height / self.height
        scale = min(scale_w, scale_h, 1.0)
        return self.scale(scale)

    def is_landscape(self) -> bool:
        """Check if width > height."""
        return self.width > self.height

    def is_portrait(self) -> bool:
        """Check if height > width."""
        return self.height > self.width

    def is_square(self) -> bool:
        """Check if width == height."""
        return self.width == self.height

    def __mul__(self, factor: float) -> Dimensions:
        """Scale dimensions by factor."""
        return self.scale(factor)


# Common presets
Dimensions.HD = Dimensions(1280, 720)
Dimensions.FULL_HD = Dimensions(1920, 1080)
Dimensions.QHD = Dimensions(2560, 1440)
Dimensions.UHD_4K = Dimensions(3840, 2160)
