"""
Alpha Composite Module: Image compositing operations.
"""

from __future__ import annotations

import typing
from typing import Any

try:
    import numpy as np  # type: ignore[unused-ignore]
    from PIL import Image

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

# Constants
RGB_CHANNELS = 3
RGBA_CHANNELS = 4


def alpha_composite(bg: np.ndarray, fg: np.ndarray) -> np.ndarray:
    """
    Alpha composite foreground over background.

    Args:
        bg: Background RGBA numpy array.
        fg: Foreground RGBA numpy array.

    Returns:
        Composited RGB numpy array (no alpha).
    """
    # Ensure both are RGBA
    if bg.shape[2] == RGB_CHANNELS:
        bg = np.concatenate([bg, np.full((*bg.shape[:2], 1), 255, dtype=np.uint8)], axis=2)
    if fg.shape[2] == RGB_CHANNELS:
        fg = np.concatenate([fg, np.full((*fg.shape[:2], 1), 255, dtype=np.uint8)], axis=2)

    # Resize fg to match bg if needed
    if fg.shape[:2] != bg.shape[:2]:
        fg_img = Image.fromarray(fg)
        fg_img = fg_img.resize((bg.shape[1], bg.shape[0]), Image.Resampling.LANCZOS)
        fg = np.array(fg_img)

    # Alpha composite
    fg_alpha = fg[:, :, 3:4].astype(float) / 255.0
    bg_alpha = bg[:, :, 3:4].astype(float) / 255.0

    out_alpha = fg_alpha + bg_alpha * (1 - fg_alpha)
    out_rgb = fg[:, :, :3].astype(float) * fg_alpha + bg[:, :, :3].astype(float) * bg_alpha * (
        1 - fg_alpha
    )

    # Avoid division by zero
    out_rgb = np.where(out_alpha > 0, out_rgb / out_alpha, 0)

    result = np.concatenate(
        [np.clip(out_rgb, 0, 255).astype(np.uint8), (out_alpha * 255).astype(np.uint8)], axis=2
    )

    # Convert to RGB for video

    return typing.cast(np.ndarray, result[:, :, :3])  # type: ignore[redundant-cast]


def convert_to_numpy_rgba(image: Any) -> np.ndarray:
    """Convert PIL Image or numpy array to RGBA numpy array."""
    if hasattr(image, "convert"):
        return np.array(image.convert("RGBA"))
    return np.array(image)


def convert_to_numpy_rgb(image: Any) -> np.ndarray:
    """Convert PIL Image or numpy array to RGB numpy array."""
    if hasattr(image, "convert"):
        return np.array(image.convert("RGB"))
    elif isinstance(image, np.ndarray):
        if image.shape[2] == RGBA_CHANNELS:
            return image[:, :, :3]
        return image
    else:
        raise ValueError(f"Unsupported image type: {type(image)}")
