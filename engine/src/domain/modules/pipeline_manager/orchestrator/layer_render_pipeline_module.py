"""
Layer Render Pipeline Module
============================

Orchestrates the rendering of a single layer to disk (EXR/MP4).
Consumes pure RenderFrame objects from LayerAnimationService and delegates I/O to FrameOutputPort.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage: Any = None

from ....entities.layer_entity import LayerEntity
from ....value_objects.animation.render_state_value import RenderFrame
from ....value_objects.configs import LayerRenderConfig
from ....value_objects.manifest.layer_manifest_value import LayerManifest
from ....value_objects.resource.media_output_path_value import MediaOutputPath
from ...animator.core.animator_controller_module import AnimationController
from .render_orchestrator_module import FrameOutputPort


class LayerRenderPipeline:
    """
    Pipeline responsible for driving the animation generation and writing results to disk.

    Responsibilities:
    1. Setup output directories.
    2. Drive the LayerAnimationService (pure state).
    3. Route frames to appropriate Output Ports (EXR, Video).
    4. Generate LayerManifest.
    """

    def __init__(
        self,
        config: LayerRenderConfig,
        animation_service: AnimationController,
        exr_port: FrameOutputPort | None = None,
        video_port: FrameOutputPort | None = None,
        media_output: MediaOutputPath | None = None,  # New injection
    ):
        self.config = config
        self.service = animation_service
        self.exr_port = exr_port
        self.video_port = video_port
        self.media_output = media_output

    def _sanitize_folder_name(self, layer_id: str) -> str:
        """Convert layer ID to safe folder name."""
        return layer_id.replace(" ", "_").replace("/", "_").lower()

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
        # total_frames = timeline_info.get("total_frames", 100)
        action = timeline_info.get("action")

        # 1. Determine Output Paths
        if self.media_output:
            folder_path = str(self.media_output.animation_frames_dir(layer.id))
            os.makedirs(folder_path, exist_ok=True)

            if self.video_port:
                # Video port setup might be needed here if not global
                pass
        else:
            # Legacy Fallback
            folder_name = self._sanitize_folder_name(layer.id)
            folder_path = os.path.join(self.config.output_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)

        blank_count = 0
        hold_ranges: list[tuple[int, int]] = []

        # Initialize Controller for this layer
        self.service.initialize_layers([layer])

        # 2. Drive Animation Loop
        # Iterate through ALL frames to check for visibility/activity
        # Optimization: Only render active range?
        # For now, render active range defined by start_frame to end_frame

        fps = self.config.fps

        for f in range(start_frame, end_frame):
            time = f / fps

            # Reset transient state
            self.service.reset_frame_state()

            # Update Controller
            if action:
                # Calculate progress
                # Note: Action duration might be different than frame range if we add handles
                pass
                # Simple progress for single action
                if time >= action.start_time and time <= (action.start_time + action.duration):
                    p = (time - action.start_time) / action.duration
                    self.service.update(action, p)
                elif time > (action.start_time + action.duration):
                    self.service.update(action, 1.0)

            # Get State (Used in real pipeline, mocked here)
            # state = self.service.get_layer_state(layer.id)

            # Render Frame (Conceptually)
            # In this pipeline, we are responsible for creating the "RenderFrame" object
            # which usually contains the pixel data.
            # But wait, AnimationController produces STATE.
            # Who produces PIXELS? The Compositor? Or the Renderer?
            # Creating a RenderFrame usually implies we have the image.

            # If this is "Layer Render", we typically take the raw layer image
            # and apply the transformations (Affine, Opacity, Mask).

            base_image = get_layer_image(layer)
            if not base_image:
                # Blank frame
                blank_count += 1
                frame_obj = RenderFrame(f, layer.id, None, "blank")
            else:
                # Apply transformations (Mocking this)
                pass
                # In real pipeline: transformed_image = image_transformer.apply(base_image, state)
                transformed_image = base_image  # Pass-through for now
                frame_obj = RenderFrame(f, layer.id, transformed_image, "active")

            # 3. Output logic
            if self.media_output:
                frame_path = str(self.media_output.animation_frame_path(layer.id, f))
            else:
                frame_path = os.path.join(folder_path, f"frame_{f:04d}.exr")

            if frame_obj.frame_type == "active":
                if self.exr_port:
                    self.exr_port.write_frame(frame_obj, frame_path)
                if self.video_port:
                    self.video_port.write_frame(frame_obj, frame_path)
            else:
                blank_count += 1

        # 4. Finalize Video
        if self.video_port:
            self.video_port.finalize()

        # 5. Build Manifest
        # 5. Build Manifest
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
