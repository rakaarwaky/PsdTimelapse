"""
DEPRECATED: This module violates Hexagonal Architecture.
Use adapters/driven/encoder/exr_output_adapter.py instead.

This file will be removed in a future version.
"""

import warnings

import Imath
import numpy as np
import OpenEXR

try:
    from PIL import Image
except ImportError:
    Image = None

from ....entities.layer_entity import LayerEntity
from ....value_objects.animation.layer_anim_state import LayerAnimState

warnings.warn(
    "layer_io_module is deprecated. Use exr_output_adapter from adapters layer.",
    DeprecationWarning,
    stacklevel=2,
)


class LayerIO:
    """Service for handling layer IO operations (EXR export)."""

    @staticmethod
    def save_blank_frame(path: str, width: int, height: int) -> None:
        """Save a transparent/blank EXR frame using OpenEXR."""
        if OpenEXR is None:
            raise ImportError("OpenEXR is required for EXR export")

        # Prepare header
        header = OpenEXR.Header(width, height)
        float_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
        header["channels"] = dict([(c, float_chan) for c in "RGBA"])

        # Write file with zero data
        out = OpenEXR.OutputFile(path, header)

        # Create zero buffer (float32)
        zero_data = np.zeros((height, width), dtype=np.float32).tobytes()

        out.writePixels({"R": zero_data, "G": zero_data, "B": zero_data, "A": zero_data})
        out.close()

    @staticmethod
    def save_layer_frame(
        layer_img: Image.Image,
        path: str,
        layer: LayerEntity,
        canvas_width: int,
        canvas_height: int,
        state: LayerAnimState | None = None,
    ) -> None:
        """
        Save layer positioned on canvas as EXR using OpenEXR.
        Uses state for position and opacity.
        """
        if OpenEXR is None:
            raise ImportError("OpenEXR is required for EXR export")

        # Use state if available, else fallback to layer defaults
        pos_x = state.position.x if state else layer.position.x
        pos_y = state.position.y if state else layer.position.y
        opacity = (
            state.opacity if state else layer.opacity.value
        )  # assuming layer.opacity is ValueObject or has value

        # Create blank canvas
        canvas = np.zeros((canvas_height, canvas_width, 4), dtype=np.float32)

        # Convert layer image to numpy
        if layer_img:
            layer_np = np.array(layer_img.convert("RGBA")).astype(np.float32) / 255.0

            # Apply Opacity (Task 2)
            if opacity != 1.0:
                layer_np[:, :, 3] *= opacity

            # Calculate position (center-based)
            # Center of layer is at pos_x, pos_y
            x = int(pos_x - layer.bounds.width / 2)
            y = int(pos_y - layer.bounds.height / 2)

            # Clamp to canvas bounds
            h, w = layer_np.shape[:2]
            x1, y1 = max(0, x), max(0, y)
            x2 = min(canvas_width, x + w)
            y2 = min(canvas_height, y + h)

            # Source crop
            sx1, sy1 = max(0, -x), max(0, -y)
            sx2 = sx1 + (x2 - x1)
            sy2 = sy1 + (y2 - y1)

            if x2 > x1 and y2 > y1:
                canvas[y1:y2, x1:x2] = layer_np[sy1:sy2, sx1:sx2]

        # Write using OpenEXR
        header = OpenEXR.Header(canvas_width, canvas_height)
        float_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
        header["channels"] = dict([(c, float_chan) for c in "RGBA"])

        out = OpenEXR.OutputFile(path, header)

        # Extract channels and write (numpy array is H,W,4 RGBA)
        out.writePixels(
            {
                "R": canvas[:, :, 0].tobytes(),
                "G": canvas[:, :, 1].tobytes(),
                "B": canvas[:, :, 2].tobytes(),
                "A": canvas[:, :, 3].tobytes(),
            }
        )
        out.close()
