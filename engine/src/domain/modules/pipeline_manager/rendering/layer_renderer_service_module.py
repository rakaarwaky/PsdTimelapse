import os
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Optional

try:
    from PIL import Image
except ImportError:
    Image = None

from ....entities.layer_entity import LayerEntity
from ....value_objects.configs import LayerRenderConfig
from ...animator.io.layer_manifest_module import LayerManifest, RenderManifest
from .layer_animation_service_module import create_layer_animation_service

if TYPE_CHECKING:
    from ...orchestrator.render_orchestrator_module import FrameOutputPort


class LayerRenderer:
    """
    Renders individual layers to separate EXR sequences.

    Refactored to Separation of Concerns:
    - State Calculation & Rendering: Delegated to LayerAnimationService
    - I/O: Delegated to injected FrameOutputPort
    """

    def __init__(
        self,
        config: LayerRenderConfig,
        exr_port: Optional["FrameOutputPort"] = None,
        video_port: Optional["FrameOutputPort"] = None,
    ):
        self.config = config
        self.manifests: list[LayerManifest] = []
        self.exr_port = exr_port
        self.video_port = video_port

        # Internal service
        self.service = create_layer_animation_service(config)

    def _sanitize_folder_name(self, layer_id: str) -> str:
        """Convert layer ID to safe folder name."""
        return layer_id.replace(" ", "_").replace("/", "_").lower()

    def render_layer(
        self,
        layer: LayerEntity,
        get_layer_image: Callable[[LayerEntity], Image.Image],
        timeline_info: dict[str, Any],  # {start_frame, end_frame, total_frames}
    ) -> LayerManifest:
        """
        Render a single layer using pure state generator and injected ports.
        """
        # Prepare output path
        folder_name = self._sanitize_folder_name(layer.id)
        folder_path = os.path.join(self.config.output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        start_frame = timeline_info.get("start_frame", 0)
        end_frame = timeline_info.get("end_frame", 100)
        total_frames = timeline_info.get("total_frames", 100)

        blank_count = 0
        hold_ranges = []

        # Iterate pure states
        for frame_data in self.service.generate_frames(layer, get_layer_image, timeline_info):
            frame_path = os.path.join(folder_path, f"frame_{frame_data.frame_number:04d}.exr")

            # Delegate I/O to ports
            if frame_data.frame_type == "blank":
                blank_count += 1
                if self.video_port and frame_data.image:
                    self.video_port.write_frame(frame_data, frame_path)

            else:
                # Active or Hold
                if self.exr_port:
                    self.exr_port.write_frame(frame_data, frame_path)

                if self.video_port and frame_data.image:
                    self.video_port.write_frame(frame_data, frame_path)

        # Finalize
        if self.video_port:
            self.video_port.finalize()

        manifest = LayerManifest(
            layer_id=layer.id,
            folder_path=folder_path,
            total_frames=total_frames,
            visible_range=(start_frame, end_frame),
            hold_ranges=hold_ranges,
            blank_frames=blank_count,
        )
        self.manifests.append(manifest)
        return manifest

    def get_render_manifest(self) -> RenderManifest:
        """Get complete render manifest."""
        total_frames = max((m.total_frames for m in self.manifests), default=0)
        return RenderManifest(
            total_frames=total_frames,
            fps=self.config.fps,
            canvas_size=(self.config.canvas_width, self.config.canvas_height),
            layers=self.manifests,
        )


def create_layer_renderer(
    config: LayerRenderConfig,
    exr_port: Optional["FrameOutputPort"] = None,
    video_port: Optional["FrameOutputPort"] = None,
) -> LayerRenderer:
    """
    Factory function for LayerRenderer.
    Ports MUST be injected manually.
    """
    return LayerRenderer(config, exr_port=exr_port, video_port=video_port)
