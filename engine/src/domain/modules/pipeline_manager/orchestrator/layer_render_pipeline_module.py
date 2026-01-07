"""
Layer Render Pipeline Module
============================

Orchestrates the rendering of a single layer to disk (EXR/MP4).
Consumes pure RenderFrame objects from LayerAnimationService and delegates I/O to FrameOutputPort.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage: Any = None  # type: ignore

from ....entities.layer_entity import LayerEntity
from ....value_objects.animation.render_state_value import RenderFrame
from ....value_objects.configs import LayerRenderConfig
from ....value_objects.manifest.layer_manifest_value import LayerManifest
from ....value_objects.resource.media_output_path_value import MediaOutputPath
from ...animator.core.animator_controller_module import AnimationController
from .render_orchestrator_module import FrameOutputPort  # type: ignore[attr-defined]


@dataclass
class RenderLoopContext:
    """Context object for the execution loop to reduce argument count."""

    start: int
    end: int
    fps: float
    layer: LayerEntity
    action: Any
    get_layer_image: Callable[..., Any]
    folder_path: str


class LayerRenderPipeline:
    """
    Pipeline responsible for driving the animation generation and writing results to disk.
    """

    def __init__(
        self,
        config: LayerRenderConfig,
        animation_service: AnimationController,
        exr_port: FrameOutputPort | None = None,
        video_port: FrameOutputPort | None = None,
        media_output: MediaOutputPath | None = None,
    ):
        self.config = config
        self.service = animation_service
        self.exr_port = exr_port
        self.video_port = video_port
        self.media_output = media_output

    def _sanitize_folder_name(self, layer_id: str) -> str:
        """Convert layer ID to safe folder name."""
        return layer_id.replace(" ", "_").replace("/", "_").lower()

    def _setup_output_folder(self, layer: LayerEntity) -> str:
        """Determine and create the output directory."""
        if self.media_output:
            folder_path = str(self.media_output.animation_frames_dir(layer.id))
        else:
            folder_name = self._sanitize_folder_name(layer.id)
            folder_path = os.path.join(self.config.output_dir, folder_name)

        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def _process_frame_action(self, time: float, action: Any) -> None:
        """Update service state based on action progress."""
        if not action:
            return

        if time >= action.start_time and time <= (action.start_time + action.duration):
            p = (time - action.start_time) / action.duration
            self.service.update(action, p)
        elif time > (action.start_time + action.duration):
            self.service.update(action, 1.0)

    def _render_frame(
        self, f: int, layer: LayerEntity, get_layer_image: Callable[[LayerEntity], Any]
    ) -> RenderFrame:
        """Generate the RenderFrame object for a given frame index."""
        base_image = get_layer_image(layer)
        if not base_image:
            return RenderFrame(f, layer.id, None, "blank")

        # Future: apply per-frame transformations from self.service.get_layer_state()
        return RenderFrame(f, layer.id, base_image, "active")

    def _execution_loop(self, ctx: RenderLoopContext) -> list[tuple[int, int]]:
        """Run the main render loop."""
        hold_ranges: list[tuple[int, int]] = []

        for f in range(ctx.start, ctx.end):
            time = f / ctx.fps
            self.service.reset_frame_state()
            self._process_frame_action(time, ctx.action)

            frame_obj = self._render_frame(f, ctx.layer, ctx.get_layer_image)

            # Output
            if self.media_output:
                frame_path = str(self.media_output.animation_frame_path(ctx.layer.id, f))
            else:
                frame_path = os.path.join(ctx.folder_path, f"frame_{f:04d}.exr")

            if frame_obj.frame_type == "active":
                if self.exr_port:
                    self.exr_port.write_frame(frame_obj, frame_path)
                if self.video_port:
                    self.video_port.write_frame(frame_obj, frame_path)

        return hold_ranges

    def execute(
        self,
        layer: LayerEntity,
        get_layer_image: Callable[[LayerEntity], Any],
        timeline_info: dict[str, Any],
    ) -> LayerManifest:
        """
        Execute the render pipeline for a single layer.
        """
        start_frame = timeline_info.get("start_frame", 0)
        end_frame = timeline_info.get("end_frame", 100)
        action = timeline_info.get("action")

        # 1. Setup
        folder_path = self._setup_output_folder(layer)
        self.service.initialize_layers([layer])

        # 2. Context
        ctx = RenderLoopContext(
            start=start_frame,
            end=end_frame,
            fps=self.config.fps,
            layer=layer,
            action=action,
            get_layer_image=get_layer_image,
            folder_path=folder_path,
        )

        # 3. Loop
        hold_ranges = self._execution_loop(ctx)

        # 4. Finalize
        if self.video_port:
            self.video_port.finalize()

        anim_type = (
            action.action_type.value if action and hasattr(action, "action_type") else "static"
        )

        return LayerManifest(
            id=layer.id,
            name=layer.name,
            sequence_folder=folder_path,
            animation_type=anim_type,
            visible_range=(start_frame, end_frame),
            hold_frames=hold_ranges,
        )
