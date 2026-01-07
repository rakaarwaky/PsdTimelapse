"""
Layer Render Configuration Value Object.
Immutable configuration for layer rendering.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LayerRenderConfig:
    """Configuration for layer rendering."""

    output_dir: str
    fps: int = 24
    canvas_width: int = 1920
    canvas_height: int = 1080
    use_symlinks_for_hold: bool = True  # Symlink instead of copy for static frames
    enable_video: bool = False  # Enable MP4 output per layer
