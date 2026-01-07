"""
Progress Value Object: Immutable progress value (0.0-1.0).
Part of timing category - task progress tracking.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Progress:
    """Immutable progress value between 0.0 (start) and 1.0 (complete)."""

    value: float

    def __post_init__(self):
        clamped = max(0.0, min(1.0, self.value))
        object.__setattr__(self, "value", clamped)

    @classmethod
    def from_ratio(cls, current: int, total: int) -> Progress:
        """Create from current/total ratio."""
        if total <= 0:
            return cls(0.0)
        return cls(current / total)

    @classmethod
    def from_percent(cls, percent: float) -> Progress:
        """Create from percentage (0-100)."""
        return cls(percent / 100.0)

    def to_percent(self) -> float:
        """Convert to percentage (0-100)."""
        return self.value * 100.0

    def format_percent(self, decimals: int = 1) -> str:
        """Format as percentage string."""
        return f"{self.to_percent():.{decimals}f}%"

    def is_complete(self) -> bool:
        """Check if progress is complete (100%)."""
        return self.value >= 1.0

    def is_started(self) -> bool:
        """Check if progress has started (> 0%)."""
        return self.value > 0.0

    def remaining(self) -> Progress:
        """Get remaining progress (1.0 - current)."""
        return Progress(1.0 - self.value)

    def __add__(self, other: Progress) -> Progress:
        return Progress(self.value + other.value)

    def __sub__(self, other: Progress) -> Progress:
        return Progress(self.value - other.value)


# Class-level constants
Progress.ZERO = Progress(0.0)
Progress.COMPLETE = Progress(1.0)
Progress.HALF = Progress(0.5)
