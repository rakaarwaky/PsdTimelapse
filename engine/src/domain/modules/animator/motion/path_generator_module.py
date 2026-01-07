"""
PathGenerator: Generate animation paths for layers.
Dependencies: Vector2, Rect, BezierSolver
"""

from __future__ import annotations

import random
from typing import Any

from ....value_objects.animation.animation_path import AnimationPath
from ....value_objects.geometry import Rect, Vector2
from .bezier_solver_module import ease_out_back, generate_curve_points


def generate_drag_path(
    target_position: Vector2,
    viewport_width: int,
    viewport_height: int,
    direction: str = "auto",
    duration: float = 0.8,
    **kwargs: Any,
) -> AnimationPath:
    """
    Generate a drag-and-drop animation path.

    Element flies in from off-screen to target position.

    Args:
        target_position: Final position in world space.
        viewport_width/height: Viewport dimensions.
        direction: Entry direction (left, right, top, bottom, auto).
        duration: Animation duration in seconds.

    Returns:
        AnimationPath with control points.
    """
    # Determine entry point (off-screen)
    if direction == "auto":
        directions = ["left", "right", "top", "bottom"]
        direction = random.choice(directions)

    margin = 400  # Extra distance off-screen (Increased for dramatic effect)

    if direction == "left":
        start = Vector2(-margin, target_position.y)
    elif direction == "right":
        start = Vector2(viewport_width + margin, target_position.y)
    elif direction == "top":
        start = Vector2(target_position.x, -margin)
    else:  # bottom
        start = Vector2(target_position.x, viewport_height + margin)

    # Generate bezier control points for smooth entry
    mid_x = (start.x + target_position.x) / 2
    mid_y = (start.y + target_position.y) / 2

    # Control points create an arc
    ctrl1 = Vector2(start.x + (mid_x - start.x) * 0.5, start.y)
    ctrl2 = Vector2(target_position.x, mid_y)

    points = generate_curve_points(start, ctrl1, ctrl2, target_position, segments=100)

    return AnimationPath(
        points=points, duration=duration, start_position=start, end_position=target_position
    )


def generate_brush_path(
    layer_bounds: Rect, complexity: int = 3, duration: float = 1.5, brush_size: float = 100.0
) -> AnimationPath:
    """
    Generate a brush reveal path over a layer's bounds.

    Creates a deterministic ZigZag path that ensures coverage.
    Start/End points are offset based on brush_size to prevent pre-reveal.

    Args:
        layer_bounds: Rectangle to cover.
        complexity: (Unused in new logic)
        duration: Animation duration.
        brush_size: Diameter of brush (used for offset).

    Returns:
        AnimationPath covering the layer.
    """
    radius = brush_size / 2.0

    # Calculate offsets to ensure:
    # 1. Start is mostly outside (only ~10% overlap)
    # 2. End is fully outside (full coverage)

    # Start: Top-Left-ish, shifted Left
    # Overlap target: ~1/64 of layer width (1.5%)
    # Center X = LayerX - Radius + (Width * 0.015)
    start_x = layer_bounds.x - radius + (layer_bounds.width * 0.015)
    start_y = layer_bounds.y + (layer_bounds.height * 0.3)
    start = Vector2(start_x, start_y)

    # Waypoints for coverage
    # Mid 1: Center/Top
    p1 = Vector2(layer_bounds.center().x, layer_bounds.y + layer_bounds.height * 0.2)
    # Mid 2: Center/Bottom
    p2 = Vector2(layer_bounds.center().x, layer_bounds.bottom - layer_bounds.height * 0.2)

    # End: Bottom-Right, shifted Right/Down
    end_x = layer_bounds.right + radius * 0.5
    end_y = layer_bounds.bottom + radius * 0.5
    end = Vector2(end_x, end_y)

    # Generate smooth path through these 4 points
    # Start -> P1 -> P2 -> End
    points = []

    # Segment 1: Start -> P1
    pts1 = generate_curve_points(
        start, Vector2(start.x + radius, start.y), Vector2(p1.x - radius / 2, p1.y), p1, segments=20
    )
    points.extend(pts1)

    # Segment 2: P1 -> P2
    pts2 = generate_curve_points(
        p1, Vector2(p1.x + radius / 2, p1.y), Vector2(p2.x - radius / 2, p2.y), p2, segments=20
    )
    points.extend(pts2)

    # Segment 3: P2 -> End
    pts3 = generate_curve_points(
        p2, Vector2(p2.x + radius / 2, p2.y), Vector2(end.x - radius, end.y), end, segments=20
    )
    points.extend(pts3)

    return AnimationPath(points=points, duration=duration, start_position=start, end_position=end)


def generate_camera_path(
    start_position: Vector2,
    end_position: Vector2,
    start_zoom: float,
    end_zoom: float,
    duration: float = 2.0,
) -> list[tuple[Vector2, float, float]]:
    """
    Generate a smooth camera movement path.

    Returns:
        List of (position, zoom, t) tuples for each frame.
    """
    frames: list[tuple[Vector2, float, float]] = []
    segments = int(duration * 30)  # 30 fps

    for i in range(segments + 1):
        t = i / segments
        eased_t = ease_out_back(t, overshoot=0.3)  # Subtle overshoot

        # Interpolate position
        pos_x = start_position.x + (end_position.x - start_position.x) * eased_t
        pos_y = start_position.y + (end_position.y - start_position.y) * eased_t
        position = Vector2(pos_x, pos_y)

        # Interpolate zoom
        zoom = start_zoom + (end_zoom - start_zoom) * eased_t

        frames.append((position, zoom, t))

    return frames
