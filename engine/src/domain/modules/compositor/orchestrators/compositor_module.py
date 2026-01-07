"""
FrameCompositor: Orchestrator.
Delegates to ops/ and services/.
Strictly < 100 lines.
"""

from collections.abc import Callable
from typing import Any

from PIL import Image

from domain.ports.media.image_processing_port import (  # type: ignore[import-not-found]
    ImageProcessingPort,  # type: ignore[unused-ignore]
)

from ....entities.layer_entity import LayerEntity
from ....entities.viewport_entity import ViewportEntity
from ....entities.world_entity import WorldEntity
from ....value_objects.animation import RenderState
from ....value_objects.compositor.compositor_dependencies import CompositorDependencies
from ..ops.psd_composition_module import compose_psd_content
from ..ops.render_states_composition_module import compose_from_render_states
from ..ops.velocity_map_module import compose_velocity_map
from ..services.layer_service import LayerRetrievalService


class FrameCompositor:
    def __init__(  # type: ignore[no-untyped-def]
        self,
        world: WorldEntity,
        viewport: ViewportEntity,
        image_processor: ImageProcessingPort | None = None,
        dependencies: CompositorDependencies | None = None,
        cursor_style=None,
    ) -> None:
        self.world = world
        self.viewport = viewport
        self.image_processor = image_processor
        self.layer_service = LayerRetrievalService()
        self.cursor_style = cursor_style  # Kept for compatibility
        self.dependencies = dependencies or CompositorDependencies()

    def compose_psd_content(self, layer_states: dict[str, Any], find_layer_func) -> Image.Image:  # type: ignore[no-untyped-def]
        return compose_psd_content(
            layer_states=layer_states,
            find_layer_func=find_layer_func,
            layer_service=self.layer_service,
            width=self.world.width,
            height=self.world.height,
            document=self.world.document,
            # Injected Dependencies
            image_processor=self.image_processor,
            mask_generator_fn=self.dependencies.mask_generator_fn,
            path_generator_fn=self.dependencies.path_generator_fn,
            brush_tool_factory_fn=self.dependencies.brush_tool_factory_fn,
        )

    def compose_velocity_map(
        self, layer_states: dict[str, Any], find_layer_func: Callable[[str], LayerEntity | None]
    ) -> Any:
        return compose_velocity_map(
            layer_states=layer_states,
            find_layer_func=find_layer_func,
            layer_service=self.layer_service,
            width=self.world.width,
            height=self.world.height,
            # Injected Dependencies
            # Use mask generator as general reveal fn
            apply_reveal_mask_fn=self.dependencies.mask_generator_fn,
        )

    def compose_from_render_states(
        self, states: list[RenderState], find_layer_func: Callable[[str], LayerEntity | None]
    ) -> Image.Image:
        return compose_from_render_states(
            states=states,
            find_layer_func=find_layer_func,
            layer_service=self.layer_service,
            width=self.world.width,
            height=self.world.height,
            document=self.world.document,
            # Injected Dependencies
            apply_reveal_mask_fn=self.dependencies.mask_generator_fn,
            get_brush_cursor_pos_fn=self.dependencies.get_brush_cursor_pos_fn,
            draw_brush_cursor_ui_fn=self.dependencies.draw_brush_cursor_ui_fn,
        )
