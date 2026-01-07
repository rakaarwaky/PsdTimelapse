"""
Rect Value Object: Immutable bounding box for spatial calculations.
Part of geometry category - coordinates and spatial math.
"""

from __future__ import annotations

from dataclasses import dataclass

from .vector_value import Vector2


@dataclass(frozen=True)
class Rect:
    """Immutable axis-aligned bounding box."""

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def center(self) -> Vector2:
        """Get the center point of this rectangle."""
        return Vector2(self.x + self.width / 2, self.y + self.height / 2)

    def contains_point(self, point: Vector2) -> bool:
        """Check if a point is inside this rectangle."""
        return self.left <= point.x <= self.right and self.top <= point.y <= self.bottom

    def contains_rect(self, other: Rect) -> bool:
        """Check if another rectangle is fully contained within this one."""
        return (
            self.left <= other.left
            and self.right >= other.right
            and self.top <= other.top
            and self.bottom >= other.bottom
        )

    def intersects(self, other: Rect) -> bool:
        """Check if this rectangle overlaps with another."""
        return not (
            self.right < other.left
            or self.left > other.right
            or self.bottom < other.top
            or self.top > other.bottom
        )

    def intersection(self, other: Rect) -> Rect | None:
        """Get the intersection rectangle, or None if no overlap."""
        if not self.intersects(other):
            return None

        new_x = max(self.left, other.left)
        new_y = max(self.top, other.top)
        new_right = min(self.right, other.right)
        new_bottom = min(self.bottom, other.bottom)

        return Rect(new_x, new_y, new_right - new_x, new_bottom - new_y)

    def union(self, other: Rect) -> Rect:
        """Get the smallest rectangle containing both rectangles."""
        new_x = min(self.left, other.left)
        new_y = min(self.top, other.top)
        new_right = max(self.right, other.right)
        new_bottom = max(self.bottom, other.bottom)

        return Rect(new_x, new_y, new_right - new_x, new_bottom - new_y)

    def area(self) -> float:
        """Calculate the area of this rectangle."""
        return self.width * self.height

    @staticmethod
    def from_bounds(left: float, top: float, right: float, bottom: float) -> Rect:
        """Create a Rect from boundary coordinates."""
        return Rect(left, top, right - left, bottom - top)

    @staticmethod
    def from_center(center: Vector2, width: float, height: float) -> Rect:
        """Create a Rect centered at a point."""
        return Rect(center.x - width / 2, center.y - height / 2, width, height)

    def __repr__(self) -> str:
        return f"Rect({self.x:.1f}, {self.y:.1f}, {self.width:.1f}x{self.height:.1f})"


# Factory function
def rect(x: float = 0, y: float = 0, w: float = 0, h: float = 0) -> Rect:
    """Convenience factory for Rect."""
    return Rect(x, y, w, h)
