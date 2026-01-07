"""
BezierSolver: Cubic Bézier curve calculations.
Dependencies: Vector2
"""

from __future__ import annotations

from collections.abc import Generator

from ....value_objects.geometry import Vector2


def cubic_bezier(p0: Vector2, p1: Vector2, p2: Vector2, p3: Vector2, t: float) -> Vector2:
    """
    Calculate point on a cubic Bézier curve at parameter t.

    Args:
        p0: Start point
        p1: First control point
        p2: Second control point
        p3: End point
        t: Parameter [0, 1]

    Returns:
        Point on the curve at t.
    """
    t = max(0.0, min(1.0, t))
    u = 1.0 - t
    u2 = u * u
    u3 = u2 * u
    t2 = t * t
    t3 = t2 * t

    x = u3 * p0.x + 3 * u2 * t * p1.x + 3 * u * t2 * p2.x + t3 * p3.x
    y = u3 * p0.y + 3 * u2 * t * p1.y + 3 * u * t2 * p2.y + t3 * p3.y

    return Vector2(x, y)


def quadratic_bezier(p0: Vector2, p1: Vector2, p2: Vector2, t: float) -> Vector2:
    """Calculate point on a quadratic Bézier curve at parameter t."""
    t = max(0.0, min(1.0, t))
    u = 1.0 - t

    x = u * u * p0.x + 2 * u * t * p1.x + t * t * p2.x
    y = u * u * p0.y + 2 * u * t * p1.y + t * t * p2.y

    return Vector2(x, y)


def generate_curve_points(
    p0: Vector2, p1: Vector2, p2: Vector2, p3: Vector2, segments: int = 20
) -> list[Vector2]:
    """
    Generate a list of points along a cubic Bézier curve.

    Args:
        p0-p3: Control points
        segments: Number of segments (output will have segments+1 points)

    Returns:
        List of points along the curve.
    """
    points = []
    for i in range(segments + 1):
        t = i / segments
        points.append(cubic_bezier(p0, p1, p2, p3, t))
    return points


def iterate_curve(
    p0: Vector2, p1: Vector2, p2: Vector2, p3: Vector2, segments: int = 20
) -> Generator[tuple[float, Vector2], None, None]:
    """
    Iterate curve points with t parameter.

    Yields:
        Tuple of (t, point) for each segment.
    """
    for i in range(segments + 1):
        t = i / segments
        yield (t, cubic_bezier(p0, p1, p2, p3, t))


# Easing functions for animation
def ease_in_out(t: float) -> float:
    """Smooth ease-in-out (cubic)."""
    if t < 0.5:
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
    import math

    if t == 0 or t == 1:
        return t
    c4 = (2 * math.pi) / 3
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values."""
    t = max(0.0, min(1.0, t))
    return start + (end - start) * t
