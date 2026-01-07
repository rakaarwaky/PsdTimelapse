"""
BrushPathType Value Object: Brush movement path for reveal animations.
Part of animation category - brush path definitions.
"""

from enum import Enum


class BrushPathType(Enum):
    """Available brush path types for reveal animations."""

    STRAIGHT = "straight"
    CURVE_DOWN = "curve_down"
    CURVE_UP = "curve_up"
    ZIGZAG = "zigzag"
    DIAGONAL_DOWN = "diagonal_down"
    DIAGONAL_UP = "diagonal_up"
