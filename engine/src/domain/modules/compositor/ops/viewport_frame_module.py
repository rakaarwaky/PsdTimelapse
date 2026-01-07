from typing import TYPE_CHECKING

from PIL import Image

from ....entities.camera_entity import CameraEntity
from ....entities.viewport_entity import ViewportEntity
from ....entities.world_entity import WorldEntity
from ..layout_manager.coordinate_mapper_module import CoordinateMapper
from ..services.layer_service import LayerRetrievalService
from .viewport_layer_module import composite_viewport_layer

if TYPE_CHECKING:
    from ...animator import AnimationController


def compose_viewport_frame(
    world: WorldEntity,
    viewport: ViewportEntity,
    camera: CameraEntity,
    controller: "AnimationController",
    layer_service: LayerRetrievalService,
) -> Image.Image:
    """Compose a complete animation frame using Camera coordinates."""
    # Create blank frame
    frame = Image.new(
        "RGBA", (viewport.output_width, viewport.output_height), viewport.background_color
    )

    mapper = CoordinateMapper(camera, viewport)

    # Compose visible layers in order with animation states
    for layer in world.scene.iterate_visible():
        state = controller.get_layer_state(layer.id)
        if state and state.visible and state.opacity > 0:
            frame = composite_viewport_layer(frame, layer, state, mapper, layer_service)

    return frame
