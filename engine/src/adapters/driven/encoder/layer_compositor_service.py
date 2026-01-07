from typing import Any

import numpy as np
from PIL import Image


def composite_frame_naive(
    static_layer: Image.Image, psd_frame: Image.Image, canvas_layout: dict[str, Any]
) -> np.ndarray:
    """
    Composite a single PSD frame onto a static base layer.
    canvas_layout: dict with keys left, top, view_w, view_h
    """
    # Start with copy of static layer
    frame = static_layer.copy()

    # Scale and center PSD content within canvas area
    cw, ch = psd_frame.size
    view_w, view_h = canvas_layout["view_w"], canvas_layout["view_h"]

    scale = min(view_w / cw, view_h / ch) * 0.9
    nw, nh = int(cw * scale), int(ch * scale)

    resized = psd_frame.resize((nw, nh), Image.Resampling.LANCZOS)

    ix = canvas_layout["left"] + (view_w - nw) // 2
    iy = canvas_layout["top"] + (view_h - nh) // 2

    # Paste with alpha mask if RGBA
    if resized.mode == "RGBA":
        frame.paste(resized, (ix, iy), resized)
    else:
        frame.paste(resized, (ix, iy))

    return np.array(frame.convert("RGB"))


def prepare_layer_compositing(static_layer: Image.Image) -> dict[str, Any]:
    """Calculate canvas layout from static layer dimensions."""
    # Canvas area constants (derived from pillow_constants_adapter implicitly or passed in)
    # Using the constants found in original file
    header_height = 50
    left_toolbar_width = 50
    right_toolbar_width = 50
    layers_panel_height = 672

    video_width = static_layer.width
    video_height = static_layer.height

    canvas_left = left_toolbar_width
    canvas_top = header_height
    canvas_right = video_width - right_toolbar_width
    canvas_bottom = video_height - layers_panel_height

    return {
        "left": canvas_left,
        "top": canvas_top,
        "view_w": canvas_right - canvas_left,
        "view_h": canvas_bottom - canvas_top,
    }
