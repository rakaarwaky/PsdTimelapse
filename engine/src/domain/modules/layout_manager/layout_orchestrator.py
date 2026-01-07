from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...entities.camera_entity import CameraEntity
    from ...entities.viewport_entity import ViewportEntity
    from .coordinate_mapper_module import CoordinateMapper


def create_coordinate_mapper(
    camera: CameraEntity,
    viewport: ViewportEntity,
) -> CoordinateMapper:
    """
    Factory: Create CoordinateMapper with camera and viewport.

    Args:
        camera: Camera entity for position/zoom
        viewport: Viewport entity for output dimensions

    Returns:
        Configured CoordinateMapper instance

    Example:
        mapper = create_coordinate_mapper(camera, viewport)
        screen_pos = mapper.world_to_viewport(Vector2(100, 200))
    """
    from .coordinate_mapper_module import CoordinateMapper

    return CoordinateMapper(camera=camera, viewport=viewport)
