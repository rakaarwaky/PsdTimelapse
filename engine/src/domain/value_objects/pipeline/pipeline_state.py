"""
Pipeline State: Status and progress tracking for the render pipeline.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class PipelineState(Enum):
    IDLE = "idle"
    PREPARING = "preparing"
    RENDERING = "rendering"
    ENCODING = "encoding"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class PipelineProgress:
    """Progress information for the render pipeline."""

    state: PipelineState
    current_frame: int
    total_frames: int
    current_phase: str
    message: str
    elapsed_seconds: float = 0.0
    estimated_remaining: float = 0.0

    @property
    def percent(self) -> float:
        if self.total_frames == 0:
            return 0.0
        return (self.current_frame / self.total_frames) * 100


ProgressCallback = Callable[[PipelineProgress], None]
