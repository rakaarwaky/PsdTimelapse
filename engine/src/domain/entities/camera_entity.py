"""
CameraEntity: Virtual director controlling the view.
Dependencies: Vector2, Rect
"""

from __future__ import annotations

from dataclasses import dataclass

from ..value_objects.geometry import Rect, Vector2


@dataclass
class CameraEntity:
    """Domain entity representing the virtual camera/director."""

    position: Vector2 = None
    zoom: float = 1.0
    min_zoom: float = 0.1
    max_zoom: float = 10.0

    def __post_init__(self) -> None:
        if self.position is None:
            self.position = Vector2(0.0, 0.0)

    def pan_to(self, target: Vector2) -> None:
        """Move camera to a target position."""
        self.position = target

    def pan_by(self, delta: Vector2) -> None:
        """Move camera by a delta amount."""
        self.position = self.position.add(delta)

    def zoom_to(self, level: float) -> None:
        """Set zoom level (clamped to min/max)."""
        self.zoom = max(self.min_zoom, min(self.max_zoom, level))

    def zoom_in(self, factor: float = 1.2) -> None:
        """Zoom in by a factor."""
        self.zoom_to(self.zoom * factor)

    def zoom_out(self, factor: float = 1.2) -> None:
        """Zoom out by a factor."""
        self.zoom_to(self.zoom / factor)

    def get_visible_rect(self, viewport_width: float, viewport_height: float) -> Rect:
        """
        Calculate the world-space rectangle visible through this camera.

        Higher zoom = smaller visible area (more zoomed in).
        """
        visible_width = viewport_width / self.zoom
        visible_height = viewport_height / self.zoom

        return Rect.from_center(self.position, visible_width, visible_height)

    def look_at(self, target: Vector2, viewport_width: float, viewport_height: float) -> None:
        """Center camera on a target point."""
        self.position = target

    def lerp_to(self, target_pos: Vector2, target_zoom: float, t: float) -> None:
        """Smoothly interpolate towards target state."""
        self.position = self.position.lerp(target_pos, t)
        self.zoom = self.zoom + (target_zoom - self.zoom) * t

    def __repr__(self) -> str:
        return f"Camera(pos={self.position}, zoom={self.zoom:.2f}x)"
