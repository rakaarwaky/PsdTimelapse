"""
Opacity Value Object: Immutable opacity value (0.0-1.0).
Part of visual category - transparency handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Opacity:
    """Immutable opacity value between 0.0 (transparent) and 1.0 (opaque)."""

    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Opacity must be 0.0-1.0, got: {self.value}")

    @classmethod
    def from_percent(cls, percent: float) -> Opacity:
        """Create from percentage (0-100)."""
        return cls(value=percent / 100.0)

    @classmethod
    def from_byte(cls, byte_value: int) -> Opacity:
        """Create from 8-bit value (0-255)."""
        return cls(value=byte_value / 255.0)

    def to_percent(self) -> float:
        """Convert to percentage (0-100)."""
        return self.value * 100.0

    def to_byte(self) -> int:
        """Convert to 8-bit value (0-255)."""
        return int(self.value * 255)

    def blend(self, other: Opacity) -> Opacity:
        """Multiply blend two opacities."""
        return Opacity(self.value * other.value)

    def is_visible(self) -> bool:
        """Check if opacity allows visibility."""
        return self.value > 0.0

    def is_fully_opaque(self) -> bool:
        """Check if fully opaque (no transparency)."""
        return self.value >= 1.0

    def __mul__(self, factor: float) -> Opacity:
        """Scale opacity by factor, clamped to valid range."""
        return Opacity(max(0.0, min(1.0, self.value * factor)))

    # Class-level presets (assigned after class definition)
    TRANSPARENT: ClassVar[Opacity]
    OPAQUE: ClassVar[Opacity]
    HALF: ClassVar[Opacity]


# Class-level constants
Opacity.TRANSPARENT = Opacity(0.0)
Opacity.OPAQUE = Opacity(1.0)
Opacity.HALF = Opacity(0.5)
