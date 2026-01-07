"""
Visual Value Objects
====================

Properti visual, warna, dan output configuration.

Contents:
- Color: RGBA color
- Opacity: Transparency value
- BlendMode: Layer blending
- Border: Border styling
- Orientation: Layout orientation
- Resolution: Output resolution
- VideoConstants: Fixed video layout
"""

from .blend_mode_value import BlendMode, BlendModeType
from .border_value import Border, BorderAlignment, BorderStyle
from .color_value import BLACK, BLUE, GREEN, RED, TRANSPARENT, WHITE, Color
from .opacity_value import Opacity
from .orientation_value import Orientation
from .resolution_value import RESOLUTION_PRESETS, Resolution
from .video_constants_value import (
    BG_COLOR,
    CANVAS_MARGIN,
    CANVAS_RENDER_AREA,
    LAYER_PANEL_HEIGHT,
    UI_CANVAS,
    UI_LAYERS_PANEL,
    UI_MENUBAR,
    UI_TOOLBAR,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
    calculate_psd_offset,
)

__all__ = [
    # Color
    "Color",
    "WHITE",
    "BLACK",
    "RED",
    "GREEN",
    "BLUE",
    "TRANSPARENT",
    # Opacity
    "Opacity",
    # BlendMode
    "BlendMode",
    "BlendModeType",
    # Border
    "Border",
    "BorderAlignment",
    "BorderStyle",
    # Orientation
    "Orientation",
    # Resolution
    "Resolution",
    "RESOLUTION_PRESETS",
    # VideoConstants
    "VIDEO_WIDTH",
    "VIDEO_HEIGHT",
    "BG_COLOR",
    "LAYER_PANEL_HEIGHT",
    "UI_MENUBAR",
    "UI_LAYERS_PANEL",
    "UI_TOOLBAR",
    "UI_CANVAS",
    "CANVAS_MARGIN",
    "CANVAS_RENDER_AREA",
    "calculate_psd_offset",
]
