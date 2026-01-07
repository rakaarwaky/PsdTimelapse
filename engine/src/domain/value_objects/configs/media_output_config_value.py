"""
MediaOutputConfig Value Object: Configuration for media output settings.
Defines resolution, fps, and cache behavior settings.
"""

from dataclasses import dataclass

# Locked resolution constants
FINAL_WIDTH: int = 1080
FINAL_HEIGHT: int = 1920
ANIMATION_RATIO: float = 1.0  # 1:1 square


@dataclass(frozen=True)
class MediaOutputConfig:
    """
    Immutable configuration for media output.
    Resolution is locked to 1080x1920 vertical Full HD.
    """

    base_path: str = "./engine/media"
    fps: int = 30

    # Resolution is locked (read-only properties)
    @property
    def final_width(self) -> int:
        """Final video width (locked at 1080)."""
        return FINAL_WIDTH

    @property
    def final_height(self) -> int:
        """Final video height (locked at 1920)."""
        return FINAL_HEIGHT

    @property
    def animation_ratio(self) -> float:
        """Animation layer ratio (locked at 1:1)."""
        return ANIMATION_RATIO

    @property
    def resolution_tuple(self) -> tuple[int, int]:
        """Resolution as (width, height) tuple."""
        return (FINAL_WIDTH, FINAL_HEIGHT)

    def get_animation_size(self, layout_size: int) -> tuple[int, int]:
        """
        Calculate animation layer size based on layout manager size.
        Returns square dimensions (1:1 ratio).

        Args:
            layout_size: Size from layout manager

        Returns:
            (width, height) tuple with 1:1 ratio
        """
        return (layout_size, layout_size)

    def with_base_path(self, new_path: str) -> "MediaOutputConfig":
        """Create new config with different base path."""
        return MediaOutputConfig(base_path=new_path, fps=self.fps)

    def with_fps(self, new_fps: int) -> "MediaOutputConfig":
        """Create new config with different fps."""
        if new_fps <= 0:
            raise ValueError("FPS must be positive")
        return MediaOutputConfig(base_path=self.base_path, fps=new_fps)
