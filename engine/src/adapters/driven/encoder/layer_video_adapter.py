"""
Layer Video Adapter
===================

Implements FrameOutputPort for video recording of layers.
Automatically manages Mp4EncoderAdapter lifecycle per layer.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

try:
    from .mp4_encoder_adapter import Mp4EncoderAdapter
except ImportError:
    Mp4EncoderAdapter = None  # type: ignore[assignment,misc]

if TYPE_CHECKING:
    from domain.modules.animator.layer_state_generator_module import (  # type: ignore[import-not-found]
        FrameData,
    )
# type: ignore[unused-ignore]


class LayerVideoAdapter:
    """
    Adapter that manages recording video for multiple layers sequentially.
    Implements FrameOutputPort interface implicitly or explicitly.
    """

    def __init__(self, output_dir: str, width: int, height: int, fps: int):
        self.output_dir = output_dir
        self.width = width
        self.height = height
        self.fps = fps

        self.current_encoder: Mp4EncoderAdapter | None = None
        self.current_layer_id: str | None = None

    def write_frame(self, frame_data: FrameData, output_path: str) -> None:
        """
        Write frame to the current video stream.
        Automatically starts a new stream if layer_id changes.
        """
        if Mp4EncoderAdapter is None:
            return

        # Check if we need to start a new encoder  # type: ignore[unreachable]
        if self.current_layer_id != frame_data.layer_id:
            # Close previous if exists (though finalize should have done it)
            self.finalize()

            # Start new
            self.current_layer_id = frame_data.layer_id
            safe_name = frame_data.layer_id.replace(" ", "_").replace("/", "_").lower()
            video_path = os.path.join(self.output_dir, f"{safe_name}.mp4")

            self.current_encoder = Mp4EncoderAdapter(self.width, self.height, self.fps, video_path)

        # Encode
        if self.current_encoder and frame_data.image:
            self.current_encoder.encode_frame(frame_data.image)

    def finalize(self) -> str:
        """Close the current encoder."""
        if self.current_encoder:
            self.current_encoder.release()
            self.current_encoder = None
        self.current_layer_id = None
        return ""


def create_layer_video_adapter(
    output_dir: str, width: int, height: int, fps: int
) -> LayerVideoAdapter:
    return LayerVideoAdapter(output_dir, width, height, fps)
