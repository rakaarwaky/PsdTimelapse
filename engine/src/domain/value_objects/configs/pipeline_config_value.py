"""
Pipeline Configuration Value Objects.
Immutable configurations for pipeline/render management.
"""

from dataclasses import dataclass
from enum import Enum

from ..animation import SequencingStrategy


class EngineState(Enum):
    """Current state of the engine."""

    IDLE = "idle"
    LOADING = "loading"
    PLANNING = "planning"
    RENDERING = "rendering"
    SAVING = "saving"
    COMPLETE = "complete"
    ERROR = "error"


class RenderMode(Enum):
    """Render strategy selection."""

    CPU = "cpu"
    OPTIMIZED = "optimized"
    GPU = "gpu"


@dataclass(frozen=True)
class RenderConfig:
    """Configuration for rendering."""

    output_path: str = "./output.mp4"
    fps: int = 30
    width: int = 1920
    height: int = 1080
    strategy: SequencingStrategy = SequencingStrategy.STAGGERED
    use_gpu: bool = False


@dataclass(frozen=True)
class PipelineConfig:
    """Configuration for pipeline behavior."""

    mode: RenderMode = RenderMode.OPTIMIZED
    fps: int = 30
    width: int = 1080
    height: int = 1920
    enable_cursor: bool = True
    enable_progress: bool = True


@dataclass(frozen=True)
class EngineProgress:
    """Progress callback data."""

    state: EngineState
    current_frame: int
    total_frames: int
    message: str

    @property
    def progress_percent(self) -> float:
        if self.total_frames == 0:
            return 0.0
        return (self.current_frame / self.total_frames) * 100
