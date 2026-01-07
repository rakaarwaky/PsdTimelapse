"""
Pipeline Config: Configuration for the render pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PipelineConfig:
    """Configuration for render pipeline."""

    output_path: str = "./output.mp4"
    fps: int = 30
    width: int = 1920
    height: int = 1080
    codec: str = "libx264"
    batch_size: int = 30  # Frames to process before memory cleanup
    enable_caching: bool = True
    max_memory_mb: int = 2048
