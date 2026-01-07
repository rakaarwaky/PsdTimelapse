"""
UI Modeler: Creates Photoshop iPad-style UI chrome assets using Pillow library.

Exports:
    - PillowModelerAdapter: Main UI modeler (ex UIRendererCore)
    - PillowHeaderAdapter, PillowToolbarsAdapter, etc: Component adapters
"""

from .pillow_canvas_adapter import CanvasRenderer
from .pillow_constants_adapter import VIDEO_HEIGHT, VIDEO_WIDTH, PSColors
from .pillow_header_adapter import HeaderRenderer
from .pillow_layers_panel_adapter import LayersPanelRenderer
from .pillow_modeler_adapter import UIRendererCore
from .pillow_toolbars_adapter import ToolbarRenderer

# Alias following brand convention
PillowModelerAdapter = UIRendererCore
PillowHeaderAdapter = HeaderRenderer
PillowToolbarsAdapter = ToolbarRenderer
PillowCanvasAdapter = CanvasRenderer
PillowLayersPanelAdapter = LayersPanelRenderer

__all__ = [
    "PillowModelerAdapter",
    "UIRendererCore",
    "PillowHeaderAdapter",
    "HeaderRenderer",
    "PillowToolbarsAdapter",
    "ToolbarRenderer",
    "PillowCanvasAdapter",
    "CanvasRenderer",
    "PillowLayersPanelAdapter",
    "LayersPanelRenderer",
    "PSColors",
    "VIDEO_WIDTH",
    "VIDEO_HEIGHT",
]
