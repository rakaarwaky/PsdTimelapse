"""
Shared constants for UI Renderers.
"""

import os

try:
    from PIL import ImageFont
except ImportError:
    ImageFont = None  # type: ignore[assignment]


# =====================================================
# EXACT COLORS FROM HTML (Photoshop iPad)
# =====================================================
class PSColors:
    """Photoshop iPad color palette."""

    DARK = (30, 30, 30)  # #1e1e1e - App frame
    PANEL = (38, 38, 38)  # #262626 - Panels
    TOOLBAR = (43, 43, 43)  # #2b2b2b - Toolbar bg
    CANVAS = (83, 83, 83)  # #535353 - Canvas bg
    ACCENT = (38, 128, 235)  # #2680eb - Photoshop Blue
    TEXT = (224, 224, 224)  # #e0e0e0 - Main text
    MUTED = (149, 149, 149)  # #959595 - Muted text
    BORDER = (62, 62, 62)  # #3e3e3e - Borders
    HOVER = (58, 58, 58)  # #3a3a3a - Hover state
    SELECTED = (53, 53, 53)  # #353535 - Selected bg
    LAYER_TAB = (50, 50, 50)  # #323232 - Layer tabs bg
    LAYER_SELECTED = (61, 61, 61)  # #3d3d3d - Selected layer
    DIVIDER = (62, 62, 62)  # #3e3e3e - Dividers
    ICON_GRAY = (200, 200, 200)  # Default icon color for fallbacks


# =====================================================
# LAYOUT CONSTANTS (1080x1920)
# =====================================================
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Header (Menubar)
HEADER_HEIGHT = 50

# Toolbars
LEFT_TOOLBAR_WIDTH = 50
RIGHT_TOOLBAR_WIDTH = 50

# Layers Panel (footer)
LAYERS_PANEL_HEIGHT = 672  # ~35vh of 1920
LAYERS_PANEL_WIDTH = (
    280  # Width of the layers panel (if used as sidebar, but redundant for bottom layout)
)

# =====================================================
# ASSET PATHS
# =====================================================
# This file is in src/Domain/modules/ui_renderer/constants_module.py
# Assets are in src/assets/ (3 levels up)
# src/Domain/modules/ui_renderer/ -> ../../../assets
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.abspath(os.path.join(CURR_DIR, "../../../assets"))

FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
ICONS_DIR = os.path.join(ASSETS_DIR, "ui_icons")

INTER_FONT = os.path.join(FONTS_DIR, "InterVariable.ttf")


def load_font(size: int):  # type: ignore[no-untyped-def]
    """Load Inter font at given size, fallback to default."""
    try:
        if os.path.exists(INTER_FONT) and ImageFont:
            return ImageFont.truetype(INTER_FONT, size)
    except Exception:
        pass
    if ImageFont:
        return ImageFont.load_default()
    return None
