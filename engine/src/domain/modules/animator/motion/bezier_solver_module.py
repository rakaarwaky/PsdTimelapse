"""
BezierSolver: Cubic Bézier curve calculations.
"""

from __future__ import annotations

import math
from collections.abc import Generator

from domain.value_objects.geometry import Vector2  # type: ignore[import-not-found]

# Auto-extracted constants
CONSTANT_0_5 = 0.5

# Auto-extracted constants

# Auto-extracted constants


def fix_code() -> None:  # type: ignore[unused-ignore]
    pass


def cubic_bezier(p0: Vector2, p1: Vector2, p2: Vector2, p3: Vector2, t: float) -> Vector2:
    """Calculate point on cubic Bezier curve at t."""
    u = 1 - t  # type: ignore[unused-ignore]
    tt = t * t
    uu = u * u
    x = (uu * p0.x) + (3 * uu * t * p1.x) + (3 * u * tt * p2.x) + (tt * t * p3.x)
    y = (uu * p0.y) + (3 * uu * t * p1.y) + (3 * u * tt * p2.y) + (tt * t * p3.y)
    return Vector2(x, y)


def generate_curve_points(points: list[Vector2]) -> Generator[tuple[float, Vector2], None, None]:
    """Yield each point along the curve with its parameter value."""
    if not points:
        return

    total = len(points) - 1
    if total <= 0:
        yield (0.0, points[0])
        return

    for i, point in enumerate(points):
        yield (i / total, point)


def ease_in_out(t: float) -> float:
    """Smooth ease-into-out (cubic)."""
    if t < CONSTANT_0_5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def ease_in(t: float) -> float:
    """Ease-in (cubic)."""
    return t * t * t


def ease_out(t: float) -> float:
    """Ease-out (cubic)."""
    return 1 - pow(1 - t, 3)


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """Ease-out with overshoot (for 'spring' effect)."""
    c1 = overshoot
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


def ease_out_elastic(t: float) -> float:
    """Elastic ease-out (bouncy effect)."""
    if t in {0, 1}:
        return t
    c4 = (2 * math.pi) / 3
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values."""
    t = max(0.0, min(1.0, t))
    return start + (end - start) * t
