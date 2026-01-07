from collections.abc import Callable, Iterator
from typing import Any

try:
    from PIL import Image
except ImportError:
    Image = None

from ....entities.layer_entity import LayerEntity
from ....value_objects.configs import LayerRenderConfig
from ...animator.generators.layer_state_generator_module import LayerStateGenerator
from ...value_objects.animation.render_state_value import RenderFrame
from .layer_composition_module import render_layer_to_image


class LayerAnimationService:
    """
    Service that generates rendered animation frames for a layer.

    Responsibilities:
    1. Delegates state calculation to LayerStateGenerator.
    2. Manages pure state -> Rendered Image transition.
    3. Handles mask state persistence (Cumulative Masks).
    """

    def __init__(self, config: LayerRenderConfig):
        self.config = config
        self.generator = LayerStateGenerator(config)
        self.cumulative_masks: dict[str, Image.Image] = {}

    def generate_frames(
        self,
        layer: LayerEntity,
        get_layer_image: Callable[[LayerEntity], Image.Image],
        timeline_info: dict[str, Any],
    ) -> Iterator[RenderFrame]:
        """
        Generate animation frames for a single layer.
        """
        # Initialize cumulative mask for this layer
        if Image:
            self.cumulative_masks[layer.id] = Image.new(
                "L", (self.config.canvas_width, self.config.canvas_height), 0
            )

        layer_img = get_layer_image(layer)
        last_active_image: Image.Image | None = None

        for frame_data in self.generator.iterate_layer_states(layer, timeline_info):
            # If generator yields a hold frame or active frame, we must ensure it has an image
            if frame_data.frame_type in ("active", "hold"):
                if frame_data.frame_type == "hold" and last_active_image:
                    # Reuse last rendered image for holds
                    yield RenderFrame(
                        frame_number=frame_data.frame_number,
                        layer_id=frame_data.layer_id,
                        state=frame_data.state,
                        image=last_active_image,
                        frame_type=frame_data.frame_type,
                    )
                else:
                    # Render image for active frame
                    rendered_img = render_layer_to_image(
                        layer_img,
                        layer,
                        frame_data.state,
                        self.config.canvas_width,
                        self.config.canvas_height,
                        self.cumulative_masks,
                    )

                    last_active_image = rendered_img

                    yield RenderFrame(
                        frame_number=frame_data.frame_number,
                        layer_id=frame_data.layer_id,
                        state=frame_data.state,
                        image=rendered_img,
                        frame_type=frame_data.frame_type,
                    )
            else:
                # Blank frames or others passed through
                yield frame_data


def create_layer_animation_service(config: LayerRenderConfig) -> LayerAnimationService:
    """Factory function for LayerAnimationService."""
    return LayerAnimationService(config)
