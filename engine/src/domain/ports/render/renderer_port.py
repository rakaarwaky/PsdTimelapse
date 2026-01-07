"""
RendererPort: Interface for image rendering operations.
Dependencies: WorldEntity, CameraEntity, ViewportEntity
"""

from abc import ABC, abstractmethod
from typing import Any

from ...entities.camera_entity import CameraEntity
from ...entities.layer_entity import LayerEntity
from ...entities.viewport_entity import ViewportEntity
from ...entities.world_entity import WorldEntity


class RendererPort(ABC):
    """
    Port interface for rendering frames.

    Adapters implementing this port:
    - pillow_renderer.py (uses Pillow/PIL library)
    """

    @abstractmethod
    def render_frame(
        self, world: WorldEntity, camera: CameraEntity, viewport: ViewportEntity
    ) -> Any:
        """
        Render a single frame of the scene.

        Args:
            world: The world containing layers to render.
            camera: Camera defining visible area.
            viewport: Output resolution configuration.

        Returns:
            PIL.Image or similar image object.
        """
        pass

    @abstractmethod
    def composite_layer(
        self,
        base_image: Any,
        layer: LayerEntity,
        camera: CameraEntity,
        viewport: ViewportEntity,
        opacity_override: float | None = None,
    ) -> Any:
        """
        Composite a single layer onto a base image.

        Args:
            base_image: Image to draw onto.
            layer: Layer to composite.
            camera: Current camera for coordinate transformation.
            viewport: Output viewport.
            opacity_override: Override layer opacity if specified.

        Returns:
            Modified image with layer composited.
        """
        pass

    @abstractmethod
    def create_blank_frame(self, viewport: ViewportEntity) -> Any:
        """
        Create a blank frame with viewport dimensions.

        Returns:
            Empty image filled with background color.
        """
        pass

    @abstractmethod
    def save_frame(self, image: Any, file_path: str, format: str = "PNG") -> None:
        """
        Save an image to disk.

        Args:
            image: Image to save.
            file_path: Destination path.
            format: Image format (PNG, JPEG, etc).
        """
        pass
