"""
EXR Output Adapter
==================

Implements FrameOutputPort for EXR sequence output.
Moved from domain (layer_io_module) to adapter layer.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

try:
    import numpy as np
except ImportError:
    np = None

try:
    import Imath  # type: ignore[import-not-found]
    import OpenEXR  # type: ignore[import-not-found]
except ImportError:
    OpenEXR = None
    Imath = None

try:
    from PIL import Image
except ImportError:
    Image = None

if TYPE_CHECKING:
    from domain.modules.animator.layer_state_generator_module import (
        FrameData,  # type: ignore[import-not-found]
    )

    from domain.modules.pipeline_manager import FrameOutputPort  # type: ignore[import-not-found]


from domain.ports.media.frame_output_port import FrameOutputPort  # type: ignore[import-not-found]


class ExrOutputAdapter(FrameOutputPort):
    """
    Adapter for writing EXR frame sequences.

    Implements FrameOutputPort.
    """

    def __init__(self, output_dir: str, width: int, height: int):
        self.output_dir = output_dir
        self.width = width
        self.height = height
        self.frames_written = 0

        os.makedirs(output_dir, exist_ok=True)

    def write_frame(self, frame_data: FrameData, output_path: str) -> None:
        """
        Write a single frame to EXR.

        Handles blank, active, and hold frames appropriately.
        """
        if OpenEXR is None:
            raise ImportError("OpenEXR is required for EXR export")

        if frame_data.frame_type == "blank":
            self._write_blank_frame(output_path)
        elif frame_data.image is not None:
            self._write_image_frame(frame_data.image, output_path)

        self.frames_written += 1

    def _write_blank_frame(self, path: str) -> None:
        """Write transparent/blank EXR frame."""
        header = OpenEXR.Header(self.width, self.height)
        float_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
        header["channels"] = dict([(c, float_chan) for c in "RGBA"])

        out = OpenEXR.OutputFile(path, header)
        zero_data = np.zeros((self.height, self.width), dtype=np.float32).tobytes()

        out.writePixels({"R": zero_data, "G": zero_data, "B": zero_data, "A": zero_data})
        out.close()

    def _write_image_frame(self, image: Image.Image, path: str) -> None:
        """Write PIL image as EXR frame."""
        # Convert PIL to numpy float32
        img_np = np.array(image.convert("RGBA")).astype(np.float32) / 255.0

        header = OpenEXR.Header(self.width, self.height)
        float_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
        header["channels"] = dict([(c, float_chan) for c in "RGBA"])

        out = OpenEXR.OutputFile(path, header)

        # Create canvas and paste image
        canvas = np.zeros((self.height, self.width, 4), dtype=np.float32)

        h, w = img_np.shape[:2]
        if h <= self.height and w <= self.width:
            canvas[:h, :w] = img_np

        out.writePixels(
            {
                "R": canvas[:, :, 0].tobytes(),
                "G": canvas[:, :, 1].tobytes(),
                "B": canvas[:, :, 2].tobytes(),
                "A": canvas[:, :, 3].tobytes(),
            }
        )
        out.close()

    def finalize(self) -> str:
        """Finalize and return output directory."""
        return self.output_dir


def create_exr_output_adapter(
    output_dir: str,
    width: int = 1080,
    height: int = 1920,
) -> ExrOutputAdapter:
    """Factory for ExrOutputAdapter."""
    return ExrOutputAdapter(output_dir, width, height)
