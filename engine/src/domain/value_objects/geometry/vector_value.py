"""
Vector2 Value Object: Immutable 2D vector for position and direction calculations.
Part of geometry category - coordinates and spatial math.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Vector2:
    """Immutable 2D vector with common math operations."""

    x: float = 0.0
    y: float = 0.0

    def add(self, other: Vector2) -> Vector2:
        """Add two vectors."""
        return Vector2(self.x + other.x, self.y + other.y)

    def sub(self, other: Vector2) -> Vector2:
        """Subtract another vector from this one."""
        return Vector2(self.x - other.x, self.y - other.y)

    def scale(self, factor: float) -> Vector2:
        """Scale vector by a factor."""
        return Vector2(self.x * factor, self.y * factor)

    def magnitude(self) -> float:
        """Calculate the length of this vector."""
        return sqrt(self.x * self.x + self.y * self.y)

    def normalize(self) -> Vector2:
        """Return a unit vector in the same direction."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0.0, 0.0)
        return Vector2(self.x / mag, self.y / mag)

    def lerp(self, target: Vector2, t: float) -> Vector2:
        """Linear interpolation towards target. t=0 returns self, t=1 returns target."""
        t = max(0.0, min(1.0, t))
        return Vector2(self.x + (target.x - self.x) * t, self.y + (target.y - self.y) * t)

    def dot(self, other: Vector2) -> float:
        """Dot product with another vector."""
        return self.x * other.x + self.y * other.y

    def distance_to(self, other: Vector2) -> float:
        """Calculate distance to another vector."""
        return self.sub(other).magnitude()

    def __repr__(self) -> str:
        return f"Vector2({self.x:.2f}, {self.y:.2f})"


# Factory functions
def vec2(x: float = 0.0, y: float = 0.0) -> Vector2:
    """Convenience factory for Vector2."""
    return Vector2(x, y)


ZERO = Vector2(0.0, 0.0)
ONE = Vector2(1.0, 1.0)
UP = Vector2(0.0, -1.0)
DOWN = Vector2(0.0, 1.0)
LEFT = Vector2(-1.0, 0.0)
RIGHT = Vector2(1.0, 0.0)
