from typing import Any

from PIL import Image, ImageDraw

from domain.ports.ui.ui_renderer_port import UIRendererPort

from .pillow_base_adapter import HAS_PILLOW
from .pillow_canvas_adapter import CanvasRenderer
from .pillow_constants_adapter import VIDEO_HEIGHT, VIDEO_WIDTH, PSColors
from .pillow_header_adapter import HeaderRenderer
from .pillow_layers_panel_adapter import LayersPanelRenderer
from .pillow_toolbars_adapter import ToolbarRenderer

"""
Core Orchestrator for UI Rendering.
Combines modular renderers to produce the final frame.
"""





class UIRendererCore(UIRendererPort):
    """
    Main Orchestrator.
    Facade that uses sub-renderers to build the UI.
    """

    def __init__(self) -> None:
        if not HAS_PILLOW:
            raise ImportError("Pillow not installed")

        self.header = HeaderRenderer()
        self.toolbar = ToolbarRenderer()
        self.canvas = CanvasRenderer()
        self.layers = LayersPanelRenderer()

    def render_frame(self, canvas_content: Image.Image, layers: list[Any] = None) -> Image.Image:
        """Render the complete UI frame with the given canvas content.

        Args:
            canvas_content: PSD content image to place in canvas area
            layers: Optional list of layer dicts for panel display
        """

        # 1. Create Base Frame
        frame = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), PSColors.DARK)
        draw = ImageDraw.Draw(frame)

        # 2. Draw Canvas Background & Content
        self.canvas.draw_background(draw)
        self.canvas.place_content(frame, canvas_content)

        # 3. Draw UI Components
        self.header.draw(draw, frame)
        self.toolbar.draw_left(draw, frame)
        self.toolbar.draw_right(draw, frame)

        # 4. Layer Panel - use provided layers or default sample
        if layers is None:
            layers = [
                {"name": "Layer 1", "visible": True},
                {"name": "Background", "visible": True, "locked": True},
            ]

        self.layers.draw(draw, frame, layers, active_idx=0)

        return frame

    def render_static_ui(self, layers: list[Any] = None) -> Image.Image:
        """
        Render only the static UI chrome (no canvas content).

        Used for multi-layer compositing optimization.
        Returns RGBA image with transparent canvas area.

        Args:
            layers: Optional list of layer dicts for panel display
        """
        # Create frame with dark background
        frame = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), PSColors.DARK + (255,))
        draw = ImageDraw.Draw(frame)

        # Draw gray canvas area (world background)
        self.canvas.draw_background(draw)

        # Draw UI chrome on top
        self.header.draw(draw, frame)
        self.toolbar.draw_left(draw, frame)
        self.toolbar.draw_right(draw, frame)

        # Layer Panel
        if layers is None:
            layers = [
                {"name": "Layer 1", "visible": True},
                {"name": "Background", "visible": True, "locked": True},
            ]
        self.layers.draw(draw, frame, layers, active_idx=0)

        return frame
