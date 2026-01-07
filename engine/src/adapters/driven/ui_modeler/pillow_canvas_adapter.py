"""
Renderer for the main Canvas area.
"""

from PIL import Image, ImageDraw

from .pillow_base_adapter import BaseRenderer
from .pillow_constants_adapter import (
    HEADER_HEIGHT,
    LAYERS_PANEL_HEIGHT,
    LEFT_TOOLBAR_WIDTH,
    RIGHT_TOOLBAR_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
    PSColors,
)


class CanvasRenderer(BaseRenderer):
    """Renders the central canvas viewport."""

    def draw_background(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw the gray canvas background."""
        left = LEFT_TOOLBAR_WIDTH
        top = HEADER_HEIGHT
        right = VIDEO_WIDTH - RIGHT_TOOLBAR_WIDTH
        bottom = VIDEO_HEIGHT - LAYERS_PANEL_HEIGHT

        draw.rectangle([left, top, right, bottom], fill=PSColors.CANVAS)

    def place_content(self, frame: Image.Image, content: Image.Image) -> None:
        """Center and scale the PSD content within the canvas area."""
        left = LEFT_TOOLBAR_WIDTH
        top = HEADER_HEIGHT
        right = VIDEO_WIDTH - RIGHT_TOOLBAR_WIDTH
        bottom = VIDEO_HEIGHT - LAYERS_PANEL_HEIGHT

        view_w = right - left
        view_h = bottom - top

        cw, ch = content.size
        scale = min(view_w / cw, view_h / ch) * 0.9
        nw, nh = int(cw * scale), int(ch * scale)

        resized = content.resize((nw, nh), Image.Resampling.LANCZOS)

        ix = left + (view_w - nw) // 2
        iy = top + (view_h - nh) // 2

        # Use alpha mask if content is RGBA to preserve gray world background
        if resized.mode == "RGBA":
            frame.paste(resized, (int(ix), int(iy)), resized)
        else:
            frame.paste(resized, (int(ix), int(iy)))
