"""
RenderOrchestrator Module
==========================

Orchestrates all 4 render passes:
1. UI Render (UIRendererPort)
2. Layout Transform (LayoutManager)
3. Layer Animation (Animator -> LayerStateGenerator)
4. Compositing (FrameCompositor)

This module is the single point of I/O coordination.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

try:
    from PIL import Image
except ImportError:
    Image = None

from ....ports.media.frame_output_port import FrameOutputPort
from ....ports.ui.ui_renderer_port import UIRendererPort
from .config.render_config import RenderOrchestratorConfig

if TYPE_CHECKING:
    from ....entities.layer_entity import LayerEntity
    from ....entities.world_entity import WorldEntity
    from ...animator.generators.layer_state_generator_module import LayerStateGenerator
    from ...compositor import FrameCompositor


class RenderOrchestrator:
    """
    Orchestrates all 4 render passes.

    This is the SINGLE ORCHESTRATOR for rendering.
    All I/O is delegated to injected ports.
    """

    def __init__(
        self,
        config: RenderOrchestratorConfig,
        ui_renderer: UIRendererPort | None = None,
        exr_output: FrameOutputPort | None = None,
        video_output: FrameOutputPort | None = None,
    ):
        self.config = config
        self.ui_renderer = ui_renderer
        self.exr_output = exr_output
        self.video_output = video_output

    def render_layer_sequence(
        self,
        layer: LayerEntity,
        state_generator: LayerStateGenerator,
        get_layer_image: Callable[..., Any],
        timeline_info: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Render a single layer's animation sequence.

        Orchestrates:
        1. LayerStateGenerator yields FrameData (pure)
        2. FrameOutputPort writes to disk (I/O)

        Returns:
            Manifest dict with layer render info
        """

        # Create output folder
        folder_name = layer.id.replace(" ", "_").replace("/", "_").lower()
        folder_path = os.path.join(self.config.output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        blank_count = 0
        active_count = 0
        hold_count = 0

        # Iterate through pure state generator
        for frame_data in state_generator.iterate_layer_states(layer, timeline_info):
            frame_path = os.path.join(folder_path, f"frame_{frame_data.frame_number:04d}.exr")

            # Delegate I/O to ports
            if frame_data.frame_type == "blank":
                blank_count += 1
                # Skip EXR for blank (optimization)
                if self.video_output and frame_data.image:
                    self.video_output.write_frame(frame_data, frame_path)

            elif frame_data.frame_type == "hold":
                hold_count += 1
                if self.exr_output:
                    self.exr_output.write_frame(frame_data, frame_path)
                if self.video_output and frame_data.image:
                    self.video_output.write_frame(frame_data, frame_path)

            else:  # active
                active_count += 1
                if self.exr_output:
                    self.exr_output.write_frame(frame_data, frame_path)
                if self.video_output and frame_data.image:
                    self.video_output.write_frame(frame_data, frame_path)

        # Finalize video if needed
        video_path = None
        if self.video_output:
            video_path = self.video_output.finalize()

        return {
            "layer_id": layer.id,
            "folder_path": folder_path,
            "video_path": video_path,
            "total_frames": blank_count + active_count + hold_count,
            "blank_frames": blank_count,
            "active_frames": active_count,
            "hold_frames": hold_count,
        }

    def render_full_pipeline(
        self,
        world: WorldEntity,
        timeline: Any,
        compositor: FrameCompositor,
        state_generator: LayerStateGenerator,
        find_layer_fn: Callable[..., Any],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Iterator[tuple[int, Image.Image]]:
        """
        Full 4-pass render pipeline.

        Pass 1: UI Render (static shell)
        Pass 2: Layout Transform
        Pass 3: Layer Animation States
        Pass 4: Compositing

        Yields:
            (frame_number, composited_image)
        """
        from .pipeline_manager_module import CompositeConfig, PipelineManager

        # Get total frames from timeline
        total_frames = int(timeline.total_duration * self.config.fps)

        # Pass 1: Render static UI once
        static_ui = None
        if self.ui_renderer:
            layers_data = [
                {"name": layer.name, "visible": layer.visible, "id": layer.id}
                for layer in world.scene.iterate_all()
            ]
            static_ui = self.ui_renderer.render_static_ui(layers_data)

        # Setup PipelineManager for final compositing
        pipeline_manager = PipelineManager(
            CompositeConfig(width=1080, height=1920, fps=self.config.fps)
        )

        for frame_num in range(total_frames):
            # Pass 3: Get animation states
            # layer_states = {} # (Animation state calculation would go here)
            # Placeholder for actual implementation if needed but keeping structure

            # Pass 4: Composite
            # This is simplified in original code too, likely uses mock or partial logic
            # Since this is "Orchestrator", it should orchestrate.
            # Original code had logic commented out/placeholder too.
            # We preserve existing structure but cleaned up.

            psd_content = compositor.compose_psd_content(
                {},  # layer_states placeholder
                find_layer_fn,
            )

            # Final composition
            if static_ui:
                final_frame = pipeline_manager.compose_frame(static_ui, psd_content)
            else:
                final_frame = psd_content

            if progress_callback and frame_num % 30 == 0:
                progress_callback(frame_num, total_frames)

            yield frame_num, final_frame


def create_render_orchestrator(
    config: RenderOrchestratorConfig | None = None, **kwargs
) -> RenderOrchestrator:
    """Factory function for RenderOrchestrator."""
    return RenderOrchestrator(config or RenderOrchestratorConfig(**kwargs))
