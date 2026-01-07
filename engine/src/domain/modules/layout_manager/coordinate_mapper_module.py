"""
CoordinateMapper: Transform coordinates between World, Camera, and Viewport spaces.

This module is "Blind" - it does not import concrete entity types.
It uses Protocol-based duck typing per 07_ORCHESTRATION_PATTERN.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from ...value_objects.geometry import Rect, Vector2


class CameraLike(Protocol):
    """Protocol for camera-like objects (duck typing)."""

    position: Any  # Vector2-like
    zoom: float

    def get_visible_rect(self, width: float, height: float) -> Any: ...


class ViewportLike(Protocol):
    """Protocol for viewport-like objects (duck typing)."""

    output_width: float
    output_height: float


@dataclass
class CoordinateMapper:
    """
    Handles coordinate transformations between three spaces:

    - World Space: Absolute position in the design (PSD coordinates)
    - Camera Space: Position relative to camera center
    - Viewport Space: Pixel position on the output frame

    This class is "Blind" - accepts any object matching CameraLike/ViewportLike.
    """

    camera: CameraLike
    viewport: ViewportLike

    def world_to_camera(self, world_pos: Vector2) -> Vector2:
        """
        Convert world coordinates to camera-relative coordinates.

        Args:
            world_pos: Position in world space.

        Returns:
            Position relative to camera center.
        """
        return world_pos.sub(self.camera.position)

    def camera_to_world(self, camera_pos: Vector2) -> Vector2:
        """
        Convert camera-relative coordinates back to world space.
        """
        return camera_pos.add(self.camera.position)

    def camera_to_viewport(self, camera_pos: Vector2) -> Vector2:
        """
        Convert camera-relative position to viewport pixel coordinates.

        Applies zoom and centers on viewport.
        """
        # Scale by zoom (higher zoom = larger on screen)
        scaled_x = camera_pos.x * self.camera.zoom
        scaled_y = camera_pos.y * self.camera.zoom

        # Offset to viewport center
        viewport_x = scaled_x + self.viewport.output_width / 2
        viewport_y = scaled_y + self.viewport.output_height / 2

        return Vector2(viewport_x, viewport_y)

    def viewport_to_camera(self, viewport_pos: Vector2) -> Vector2:
        """
        Convert viewport pixel position back to camera space.
        """
        # Remove viewport center offset
        centered_x = viewport_pos.x - self.viewport.output_width / 2
        centered_y = viewport_pos.y - self.viewport.output_height / 2

        # Remove zoom scaling
        camera_x = centered_x / self.camera.zoom
        camera_y = centered_y / self.camera.zoom

        return Vector2(camera_x, camera_y)

    def world_to_viewport(self, world_pos: Vector2) -> Vector2:
        """
        Direct conversion from world space to viewport pixels.
        """
        camera_pos = self.world_to_camera(world_pos)
        return self.camera_to_viewport(camera_pos)

    def viewport_to_world(self, viewport_pos: Vector2) -> Vector2:
        """
        Direct conversion from viewport pixels to world space.
        """
        camera_pos = self.viewport_to_camera(viewport_pos)
        return self.camera_to_world(camera_pos)

    def world_rect_to_viewport(self, world_rect: Rect) -> Rect:
        """
        Transform a world-space rectangle to viewport space.
        """
        top_left = self.world_to_viewport(Vector2(world_rect.x, world_rect.y))
        scaled_width = world_rect.width * self.camera.zoom
        scaled_height = world_rect.height * self.camera.zoom

        return Rect(top_left.x, top_left.y, scaled_width, scaled_height)

    def is_visible(self, world_rect: Rect) -> bool:
        """
        Check if a world-space rectangle is visible in the viewport.
        """
        visible_world_rect = self.camera.get_visible_rect(
            self.viewport.output_width, self.viewport.output_height
        )
        return world_rect.intersects(visible_world_rect)

    def get_visible_world_rect(self) -> Rect:
        """
        Get the world-space rectangle currently visible.
        """
        return self.camera.get_visible_rect(self.viewport.output_width, self.viewport.output_height)
