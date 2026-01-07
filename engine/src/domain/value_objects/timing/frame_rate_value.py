"""
FrameRate Value Object: Immutable frame rate (FPS).
Part of timing category - video timing.
"""

from __future__ import annotations

from dataclasses import dataclass

COMMON_FRAME_RATES: set[int] = {24, 25, 30, 48, 50, 60, 120}


@dataclass(frozen=True)
class FrameRate:
    """Immutable frame rate (frames per second)."""

    fps: int

    def __post_init__(self) -> None:
        if self.fps <= 0:
            raise ValueError(f"FPS must be positive: {self.fps}")
        if self.fps > 240:
            raise ValueError(f"FPS too high (max 240): {self.fps}")

    @property
    def frame_duration(self) -> float:
        """Duration of one frame in seconds."""
        return 1.0 / self.fps

    @property
    def frame_duration_ms(self) -> float:
        """Duration of one frame in milliseconds."""
        return 1000.0 / self.fps

    def frames_for_duration(self, seconds: float) -> int:
        """Calculate number of frames for given duration."""
        return int(seconds * self.fps)

    def duration_for_frames(self, frames: int) -> float:
        """Calculate duration in seconds for given frame count."""
        return frames / self.fps

    def is_common(self) -> bool:
        """Check if this is a common/standard frame rate."""
        return self.fps in COMMON_FRAME_RATES

    def format(self) -> str:
        """Format as string, e.g., '30 fps'."""
        return f"{self.fps} fps"

    def __int__(self) -> int:
        """Allow int(frame_rate) to get fps value."""
        return self.fps


# Common presets
FrameRate.FILM = FrameRate(24)
FrameRate.PAL = FrameRate(25)
FrameRate.NTSC = FrameRate(30)
FrameRate.SMOOTH = FrameRate(60)
