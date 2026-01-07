"""
Animator Configuration Value Object.
Immutable configuration for animator behavior.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnimatorConfig:
    """Configuration for animator behavior."""

    viewport_width: int = 1080
    viewport_height: int = 1920
    default_easing: str = "ease_out"
    motion_blur_enabled: bool = False
    subpixel_precision: bool = True
