from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from ....entities.layer_entity import LayerEntity
from ....value_objects.animation.layer_anim_state import LayerAnimState
from ....value_objects.animation.render_state_value import RenderFrame
from ....value_objects.configs import LayerRenderConfig
from ..core.animator_controller_module import AnimationController

"""
Layer State Generator Module
============================

Pure state calculation for layer animation - NO I/O.
This module yields animation states that PipelineManager consumes for rendering.
"""


# ============================================================
# Value Objects (Pure Data)
# ============================================================


# ============================================================
# State Generator (Pure Logic)
# ============================================================


class LayerStateGenerator:
    """
    Generates animation states for a layer - NO I/O.

    Usage:
        generator = LayerStateGenerator(config)
        for frame_data in generator.iterate_layer_states(layer, timeline):
            # PipelineManager handles I/O and Rendering here
            output_port.write_frame(frame_data)
    """

    def __init__(self, config: LayerRenderConfig):
        self.config = config
        # Masks moved to rendering service

    def iterate_layer_states(
        self,
        layer: LayerEntity,
        timeline_info: dict[str, Any],
    ) -> Iterator[RenderFrame]:
        """
        Yields FrameData for each frame - pure generator, NO I/O.

        Args:
            layer: Layer entity to animate
            timeline_info: dict with start_frame, end_frame, total_frames, action

        Yields:
            FrameData for each frame in the timeline with state but NO image.
        """
        start_frame = timeline_info.get("start_frame", 0)
        end_frame = timeline_info.get("end_frame", 100)
        total_frames = timeline_info.get("total_frames", 100)
        action = timeline_info.get("action")
        duration_frames = end_frame - start_frame

        # Init Animation Controller
        controller = AnimationController(self.config.canvas_width, self.config.canvas_height)
        controller.initialize_layers([layer])

        # Track last active frame for hold detection
        last_active_state: LayerAnimState | None = None

        for frame in range(total_frames):
            if frame < start_frame:
                # Blank frame (before animation starts)
                yield RenderFrame(
                    frame_number=frame,
                    layer_id=layer.id,
                    state=None,
                    image=None,
                    frame_type="blank",
                )
                continue

            # Calculate animation progress
            progress = 0.0
            if action and duration_frames > 0:
                raw_progress = (frame - start_frame) / duration_frames
                progress = max(0.0, min(1.0, raw_progress))
                controller.update(action, progress)

            state = controller.get_layer_state(layer.id)

            if frame > end_frame:
                # Hold frame (after animation ends) - reuse last active state
                yield RenderFrame(
                    frame_number=frame,
                    layer_id=layer.id,
                    state=last_active_state or state,
                    image=None,  # Rendering handled by Pipeline
                    frame_type="hold",
                )
            else:
                # Active frame
                last_active_state = state

                yield RenderFrame(
                    frame_number=frame,
                    layer_id=layer.id,
                    state=state,
                    image=None,  # Rendering handled by Pipeline
                    frame_type="active",
                )


# ============================================================
# Factory
# ============================================================


def create_layer_state_generator(config: LayerRenderConfig) -> LayerStateGenerator:
    """Factory function for LayerStateGenerator."""
    return LayerStateGenerator(config)
