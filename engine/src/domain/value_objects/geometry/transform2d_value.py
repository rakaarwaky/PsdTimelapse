"""
Transform2D Value Object: Immutable 2D transformation matrix.
Part of geometry category - spatial transformations.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .vector_value import Vector2


@dataclass(frozen=True)
class Transform2D:
    """
    Immutable 2D transformation combining position, scale, and rotation.

    Applies transformations in order: Scale -> Rotate -> Translate
    """

    position: Vector2 = None  # type: ignore[assignment]
    scale: float = 1.0
    rotation: float = 0.0
    anchor: Vector2 = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.position is None:
            object.__setattr__(self, "position", Vector2(0, 0))  # type: ignore[unreachable]
        if self.anchor is None:
            object.__setattr__(self, "anchor", Vector2(0, 0))  # type: ignore[unreachable]

        if self.scale <= 0:
            raise ValueError(f"Scale must be positive: {self.scale}")

    @property
    def rotation_radians(self) -> float:
        """Get rotation in radians."""
        return math.radians(self.rotation)

    def apply(self, point: Vector2) -> Vector2:
        """Apply transformation to a point."""
        p = point.sub(self.anchor)
        p = Vector2(p.x * self.scale, p.y * self.scale)

        if self.rotation != 0:
            cos_r = math.cos(self.rotation_radians)
            sin_r = math.sin(self.rotation_radians)
            new_x = p.x * cos_r - p.y * sin_r
            new_y = p.x * sin_r + p.y * cos_r
            p = Vector2(new_x, new_y)

        p = p.add(self.anchor).add(self.position)
        return p

    def apply_inverse(self, point: Vector2) -> Vector2:
        """Apply inverse transformation (untransform a point)."""
        p = point.sub(self.position).sub(self.anchor)

        if self.rotation != 0:
            cos_r = math.cos(-self.rotation_radians)
            sin_r = math.sin(-self.rotation_radians)
            new_x = p.x * cos_r - p.y * sin_r
            new_y = p.x * sin_r + p.y * cos_r
            p = Vector2(new_x, new_y)

        p = Vector2(p.x / self.scale, p.y / self.scale)
        p = p.add(self.anchor)
        return p

    def combine(self, other: Transform2D) -> Transform2D:
        """Combine with another transform (this applied first, then other)."""
        return Transform2D(
            position=self.position.add(other.position),
            scale=self.scale * other.scale,
            rotation=self.rotation + other.rotation,
            anchor=self.anchor,
        )

    def with_position(self, position: Vector2) -> Transform2D:
        """Create new transform with different position."""
        return Transform2D(position, self.scale, self.rotation, self.anchor)

    def with_scale(self, scale: float) -> Transform2D:
        """Create new transform with different scale."""
        return Transform2D(self.position, scale, self.rotation, self.anchor)

    def with_rotation(self, rotation: float) -> Transform2D:
        """Create new transform with different rotation (degrees)."""
        return Transform2D(self.position, self.scale, rotation, self.anchor)

    def translate(self, offset: Vector2) -> Transform2D:
        """Create new transform translated by offset."""
        return Transform2D(self.position.add(offset), self.scale, self.rotation, self.anchor)

    def rotate(self, degrees: float) -> Transform2D:
        """Create new transform rotated by additional degrees."""
        return Transform2D(self.position, self.scale, self.rotation + degrees, self.anchor)

    def is_identity(self) -> bool:
        """Check if this is an identity transform (no change)."""
        return (
            self.position.x == 0
            and self.position.y == 0
            and self.scale == 1.0
            and self.rotation == 0
        )


# Identity transform
Transform2D.IDENTITY = Transform2D()  # type: ignore[attr-defined]
