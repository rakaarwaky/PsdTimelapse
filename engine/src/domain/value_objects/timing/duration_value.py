"""
Duration Value Object: Immutable time duration in seconds.
Part of timing category - time handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Duration:
    """Immutable time duration in seconds."""

    ZERO: ClassVar[Duration]
    ONE_SECOND: ClassVar[Duration]
    ONE_FRAME_30FPS: ClassVar[Duration]

    seconds: float

    def __post_init__(self) -> None:
        if self.seconds < 0:
            raise ValueError(f"Duration cannot be negative: {self.seconds}")

    @classmethod
    def from_milliseconds(cls, ms: float) -> Duration:
        """Create Duration from milliseconds."""
        return cls(seconds=ms / 1000.0)

    @classmethod
    def from_frames(cls, frames: int, fps: int = 30) -> Duration:
        """Create Duration from frame count at given FPS."""
        return cls(seconds=frames / fps)

    def to_frames(self, fps: int = 30) -> int:
        """Convert to frame count at given FPS."""
        return int(self.seconds * fps)

    def to_milliseconds(self) -> float:
        """Convert to milliseconds."""
        return self.seconds * 1000.0

    def __add__(self, other: Duration) -> Duration:
        return Duration(self.seconds + other.seconds)

    def __sub__(self, other: Duration) -> Duration:
        return Duration(self.seconds - other.seconds)

    def __mul__(self, factor: float) -> Duration:
        return Duration(self.seconds * factor)

    def __lt__(self, other: Duration) -> bool:
        return self.seconds < other.seconds

    def __le__(self, other: Duration) -> bool:
        return self.seconds <= other.seconds

    def __gt__(self, other: Duration) -> bool:
        return self.seconds > other.seconds

    def __ge__(self, other: Duration) -> bool:
        return self.seconds >= other.seconds

    def format(self) -> str:
        """Format as MM:SS.ms"""
        mins = int(self.seconds // 60)
        secs = self.seconds % 60
        return f"{mins:02d}:{secs:05.2f}"


# Class-level constants
Duration.ZERO = Duration(0.0)
Duration.ONE_SECOND = Duration(1.0)
Duration.ONE_FRAME_30FPS = Duration(1.0 / 30.0)
