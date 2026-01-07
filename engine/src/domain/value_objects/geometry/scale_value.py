"""
Scale Value Object: Immutable scale/zoom factor.
Part of geometry category - transformation and sizing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scale:
    """Immutable scale/zoom factor."""

    value: float

    MIN_SCALE: float = 0.01
    MAX_SCALE: float = 100.0

    def __post_init__(self):
        if not Scale.MIN_SCALE <= self.value <= Scale.MAX_SCALE:
            raise ValueError(
                f"Scale must be {Scale.MIN_SCALE}-{Scale.MAX_SCALE}, got: {self.value}"
            )

    @classmethod
    def from_percent(cls, percent: float) -> Scale:
        """Create from percentage (e.g., 150 for 150%)."""
        return cls(percent / 100.0)

    def to_percent(self) -> float:
        """Convert to percentage."""
        return self.value * 100.0

    def apply(self, value: float) -> float:
        """Apply scale to a value."""
        return value * self.value

    def inverse(self) -> Scale:
        """Get inverse scale (1/scale)."""
        return Scale(1.0 / self.value)

    def combine(self, other: Scale) -> Scale:
        """Multiply two scales together."""
        return Scale(max(Scale.MIN_SCALE, min(Scale.MAX_SCALE, self.value * other.value)))

    def is_zoomed_in(self) -> bool:
        """Check if scale > 1.0 (zoomed in)."""
        return self.value > 1.0

    def is_zoomed_out(self) -> bool:
        """Check if scale < 1.0 (zoomed out)."""
        return self.value < 1.0

    def format(self) -> str:
        """Format as percentage string."""
        return f"{self.to_percent():.0f}%"

    def __mul__(self, other: Scale) -> Scale:
        """Multiply two scales."""
        return self.combine(other)

    def __float__(self) -> float:
        """Allow float(scale) to get value."""
        return self.value


# Class-level constants
Scale.IDENTITY = Scale(1.0)
Scale.HALF = Scale(0.5)
Scale.DOUBLE = Scale(2.0)
