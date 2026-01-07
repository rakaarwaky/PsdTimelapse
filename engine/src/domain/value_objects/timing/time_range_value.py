"""
TimeRange Value Object: Immutable time range with start and end.
Part of timing category - timeline intervals.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeRange:
    """Immutable time range with start and end."""

    start: float
    end: float

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError(f"Start cannot be negative: {self.start}")
        if self.end < self.start:
            raise ValueError(f"End ({self.end}) cannot be before start ({self.start})")

    @classmethod
    def from_duration(cls, start: float, duration: float) -> TimeRange:
        """Create from start time and duration."""
        return cls(start=start, end=start + duration)

    @property
    def duration(self) -> float:
        """Get duration of the range."""
        return self.end - self.start

    @property
    def midpoint(self) -> float:
        """Get midpoint of the range."""
        return (self.start + self.end) / 2

    def contains(self, time: float) -> bool:
        """Check if time is within range."""
        return self.start <= time < self.end

    def overlaps(self, other: TimeRange) -> bool:
        """Check if two ranges overlap."""
        return self.start < other.end and other.start < self.end

    def intersection(self, other: TimeRange) -> TimeRange | None:
        """Get overlapping portion of two ranges."""
        if not self.overlaps(other):
            return None
        return TimeRange(start=max(self.start, other.start), end=min(self.end, other.end))

    def union(self, other: TimeRange) -> TimeRange:
        """Get combined range covering both."""
        return TimeRange(start=min(self.start, other.start), end=max(self.end, other.end))

    def extend(self, amount: float) -> TimeRange:
        """Extend range by amount on both ends."""
        return TimeRange(start=max(0, self.start - amount), end=self.end + amount)

    def shift(self, offset: float) -> TimeRange:
        """Shift range by offset."""
        return TimeRange(start=self.start + offset, end=self.end + offset)

    def progress_at(self, time: float) -> float:
        """Get progress (0.0-1.0) at given time."""
        if time <= self.start:
            return 0.0
        if time >= self.end:
            return 1.0
        return (time - self.start) / self.duration


TimeRange.ZERO = TimeRange(0.0, 0.0)  # type: ignore[attr-defined]
