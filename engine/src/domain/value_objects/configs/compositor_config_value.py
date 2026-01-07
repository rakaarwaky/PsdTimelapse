"""
Compositor Configuration Value Object.
Immutable configuration for compositor behavior.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CompositorConfig:
    """Configuration for compositor behavior."""

    enable_motion_blur: bool = True
    enable_subpixel: bool = True
    cache_static_layers: bool = True
    cursor_visible: bool = True
    cursor_size: int = 24
