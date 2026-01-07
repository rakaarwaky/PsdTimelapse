"""
Orientation Value Object: Layer orientation based on dimensions.
Part of visual category - layout orientation.
"""

from enum import Enum


class Orientation(Enum):
    """Layer orientation derived from bounding box dimensions."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    SQUARE = "square"

    @classmethod
    def from_dimensions(cls, width: float, height: float) -> "Orientation":
        """Determine orientation from width and height."""
        if width > height:
            return cls.HORIZONTAL
        elif height > width:
            return cls.VERTICAL
        else:
            return cls.SQUARE

    @property
    def is_horizontal_dominant(self) -> bool:
        """True if orientation should be treated as horizontal (includes SQUARE)."""
        return self in (Orientation.HORIZONTAL, Orientation.SQUARE)

    @property
    def is_vertical_dominant(self) -> bool:
        """True if orientation is strictly vertical."""
        return self == Orientation.VERTICAL
