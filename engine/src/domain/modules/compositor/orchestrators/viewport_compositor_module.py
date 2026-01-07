"""
ViewportCompositor: Composes frames specifically for Viewport/Camera display.
Separates Viewport/Camera logic from the main PSD composition pipeline.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ....entities.camera_entity import CameraEntity
from ....entities.layer_entity import LayerEntity
from ....entities.viewport_entity import ViewportEntity
from ....entities.world_entity import WorldEntity
from ...animator import AnimationController, LayerAnimState
from ..ops.viewport_centered_module import compose_centered_frame
from ..ops.viewport_frame_module import compose_viewport_frame
from ..services.layer_service import LayerRetrievalService

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class ViewportCompositor:
    """
    Handles composition for Viewport/Camera rendering.
    Acts as a Facade orchestrating specialized composition modules.
    """

    def __init__(self, world: WorldEntity, viewport: ViewportEntity):
        if not HAS_PILLOW:
            raise ImportError("Pillow required")

        self.world = world
        self.viewport = viewport
        self.layer_service = LayerRetrievalService()

    def compose_frame(self, camera: CameraEntity, controller: AnimationController) -> Image.Image:
        """Compose a complete animation frame using Camera coordinates."""

        return compose_viewport_frame(
            world=self.world,
            viewport=self.viewport,
            camera=camera,
            controller=controller,
            layer_service=self.layer_service,
        )

    def compose_centered_frame(
        self, layer_states: dict[str, LayerAnimState], find_layer_func: Callable[..., Any]
    ) -> Image.Image:
        """
        Compose frame with PSD centered in viewport.
        Centers PSD document within viewport by calculating proper Y offset.
        """

        return compose_centered_frame(
            world=self.world,
            viewport=self.viewport,
            layer_states=layer_states,
            find_layer_func=find_layer_func,
            layer_service=self.layer_service,
        )

    def _get_layer_image(self, layer: LayerEntity) -> Image.Image | None:
        """Get cached layer image or extract from layer data."""
        return self.layer_service.get_layer_image(layer)

    def clear_cache(self) -> None:
        self.layer_service.clear_cache()
