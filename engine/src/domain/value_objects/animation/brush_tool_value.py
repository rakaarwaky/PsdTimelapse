"""
BrushTool Value Object: Configuration for brush-based mask generation.
Part of animation category - brush reveal animations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BrushTool:
    """Configuration for a brush tool used in reveal animations."""

    size_px: float
    hardness: float = 1.0
    flow: float = 1.0
    spacing: float = 0.1
    feather: float = 5.0

    @property
    def blur_radius(self) -> float:
        """Calculate blur radius based on hardness."""
        return (1.0 - self.hardness) * (self.size_px / 4.0)

    @property
    def feather_radius(self) -> float:
        """Get feather radius for mask edge smoothing."""
        if self.feather > 0:
            return self.feather
        return self.blur_radius
