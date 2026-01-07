"""
ViewportEntity: Output frame resolution configuration.
Dependencies: None (Pure Data)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OutputPreset(Enum):
    """Common output resolution presets."""

    HD_720 = (1280, 720)
    FHD_1080 = (1920, 1080)
    QHD_1440 = (2560, 1440)
    UHD_4K = (3840, 2160)
    SQUARE_1080 = (1080, 1080)
    PORTRAIT_1080 = (1080, 1920)


@dataclass
class ViewportEntity:
    """Domain entity representing the output frame configuration."""

    output_width: int = 1920
    output_height: int = 1080
    fps: int = 30
    background_color: tuple[int, int, int, int] = (255, 255, 255, 255)

    @property
    def resolution(self) -> tuple[int, int]:
        """Get resolution as tuple."""
        return (self.output_width, self.output_height)

    @property
    def aspect_ratio(self) -> float:
        """Get width/height ratio."""
        if self.output_height == 0:
            return 0.0
        return self.output_width / self.output_height

    @property
    def is_landscape(self) -> bool:
        """Check if viewport is landscape orientation."""
        return self.output_width > self.output_height

    @property
    def is_portrait(self) -> bool:
        """Check if viewport is portrait orientation."""
        return self.output_height > self.output_width

    @property
    def is_square(self) -> bool:
        """Check if viewport is square."""
        return self.output_width == self.output_height

    @property
    def total_pixels(self) -> int:
        """Total pixel count."""
        return self.output_width * self.output_height

    @staticmethod
    def from_preset(preset: OutputPreset, fps: int = 30) -> ViewportEntity:
        """Create viewport from a preset."""
        width, height = preset.value
        return ViewportEntity(output_width=width, output_height=height, fps=fps)

    def scale_to_fit(self, source_width: int, source_height: int) -> tuple[float, float]:
        """
        Calculate scale factors to fit source into viewport.
        Returns (scale_x, scale_y) where both should be the same for aspect-correct scaling.
        """
        scale_x = self.output_width / source_width
        scale_y = self.output_height / source_height
        return (scale_x, scale_y)

    def __repr__(self) -> str:
        orientation = "L" if self.is_landscape else ("P" if self.is_portrait else "S")
        return f"Viewport({self.output_width}x{self.output_height} @{self.fps}fps [{orientation}])"
