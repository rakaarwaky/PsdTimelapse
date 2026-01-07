"""
VideoConstants Value Object: Fixed resolution and UI layout constants.
Part of visual category - video output configuration.
"""

from __future__ import annotations

from ..geometry.rect_value import Rect

# === VIDEO RESOLUTION (LOCKED) ===
VIDEO_WIDTH: int = 1080
VIDEO_HEIGHT: int = 1920
BG_COLOR: tuple[int, int, int] = (255, 255, 255)

# === UI LAYOUT REGIONS ===
LAYER_PANEL_HEIGHT = 300

UI_MENUBAR = Rect(0, 0, 1080, 40)
UI_LAYERS_PANEL = Rect(0, 1920 - LAYER_PANEL_HEIGHT, 1080, LAYER_PANEL_HEIGHT)
UI_TOOLBAR = Rect(0, 40, 50, 1920 - 40 - LAYER_PANEL_HEIGHT)
UI_CANVAS = Rect(50, 40, 1030, 1920 - 40 - LAYER_PANEL_HEIGHT)

# === CANVAS RENDER AREA (with margins) ===
CANVAS_MARGIN: int = 20
CANVAS_RENDER_AREA = Rect(
    UI_CANVAS.x + CANVAS_MARGIN,
    UI_CANVAS.y + CANVAS_MARGIN,
    UI_CANVAS.width - CANVAS_MARGIN * 2,
    UI_CANVAS.height - CANVAS_MARGIN * 2,
)


def calculate_psd_offset(psd_width: float, psd_height: float) -> tuple[float, float]:
    """Calculate offset to center PSD at world origin."""
    psd_center_x = psd_width / 2
    psd_center_y = psd_height / 2
    return (-psd_center_x, -psd_center_y)
