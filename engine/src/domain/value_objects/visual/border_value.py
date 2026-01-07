"""
Border Value Object: Immutable border styling.
Part of visual category - border and outline properties.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from .color_value import BLACK, Color


class BorderAlignment(Enum):
    CENTER = auto()
    INSIDE = auto()
    OUTSIDE = auto()


class BorderStyle(Enum):
    SOLID = auto()
    DASHED = auto()
    DOTTED = auto()


@dataclass(frozen=True)
class Border:
    """Immutable representation of a border."""

    color: Color = field(default_factory=lambda: BLACK)
    width: float = 1.0
    alignment: BorderAlignment = BorderAlignment.INSIDE
    style: BorderStyle = BorderStyle.SOLID

    def __post_init__(self):
        if self.width < 0:
            object.__setattr__(self, "width", 0.0)

    @staticmethod
    def none() -> Border:
        """Create a transparent/zero-width border."""
        from .color_value import TRANSPARENT

        return Border(color=TRANSPARENT, width=0.0)

    @staticmethod
    def simple(color: Color, width: float = 1.0) -> Border:
        """Create a simple solid inside border."""
        return Border(color=color, width=width, alignment=BorderAlignment.INSIDE)
