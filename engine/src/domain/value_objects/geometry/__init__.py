"""
Geometry Value Objects
======================

Koordinat, bentuk, dan transformasi spasial.

Contents:
- Vector2: 2D vector for position/direction
- Rect: Bounding box
- Dimensions: Width/height pair
- Scale: Zoom factor
- Transform2D: Combined transformation
"""

from .dimensions_value import Dimensions
from .rect_value import Rect, rect
from .scale_value import Scale
from .transform2d_value import Transform2D
from .vector_value import DOWN, LEFT, ONE, RIGHT, UP, ZERO, Vector2, vec2

__all__ = [
    # Vector
    "Vector2",
    "vec2",
    "ZERO",
    "ONE",
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    # Rect
    "Rect",
    "rect",
    # Dimensions
    "Dimensions",
    # Scale
    "Scale",
    # Transform
    "Transform2D",
]
