"""
Renderer for Left and Right Toolbars.
"""

import os

from PIL import Image, ImageDraw

from .pillow_base_adapter import BaseRenderer
from .pillow_constants_adapter import (
    HEADER_HEIGHT,
    ICONS_DIR,
    LAYERS_PANEL_HEIGHT,
    LEFT_TOOLBAR_WIDTH,
    RIGHT_TOOLBAR_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
    PSColors,
)


class ToolbarRenderer(BaseRenderer):
    """Renders side toolbars."""

    def draw_left(self, draw: ImageDraw.ImageDraw, frame: Image.Image) -> None:
        """Draw main tools (Move, Brush, etc)."""
        top = HEADER_HEIGHT
        bottom = VIDEO_HEIGHT - LAYERS_PANEL_HEIGHT

        draw.rectangle([0, top, LEFT_TOOLBAR_WIDTH, bottom], fill=PSColors.PANEL)  # type: ignore[arg-type]
        draw.line([(LEFT_TOOLBAR_WIDTH, top), (LEFT_TOOLBAR_WIDTH, bottom)], fill=PSColors.BORDER)

        toolbar_icons_path = os.path.join(ICONS_DIR, "toolbar")

        icon_layout = [
            "icon_move",
            "icon_marquee",
            "icon_lasso",
            "icon_wand",
            None,
            "icon_crop",
            "icon_brush",
            "icon_eraser",
            "icon_gradient",
            None,
            "icon_text",
            "icon_eyedropper",
            "icon_hand",
            "icon_zoom",
        ]

        # Load available icons
        icons = {}
        for name in icon_layout:
            if name:
                path = os.path.join(toolbar_icons_path, f"{name}.png")
                if os.path.exists(path):
                    try:
                        icons[name] = (
                            Image.open(path)
                            .convert("RGBA")
                            .resize((36, 36), Image.Resampling.LANCZOS)
                        )
                    except Exception:
                        pass

        # Layout calculation
        num_tools = len([x for x in icon_layout if x is not None])
        num_seps = len([x for x in icon_layout if x is None])
        btn_h = 48
        sep_h = 24
        total_content_h = (num_tools * btn_h) + (num_seps * sep_h)
        available_height = (bottom - top) - 80
        extra_space = max(0, available_height - total_content_h)
        gap = extra_space // (len(icon_layout) + 1)

        y = top + gap + 16

        for item in icon_layout:
            if item is None:
                draw.line([(10, y + 10), (34, y + 10)], fill=PSColors.BORDER)
                y += sep_h
                continue

            is_selected = item == "icon_move"
            btn_x = (LEFT_TOOLBAR_WIDTH - 44) // 2

            if is_selected:
                draw.rectangle([btn_x, y, btn_x + 44, y + 44], fill=PSColors.HOVER)  # type: ignore[arg-type]

            if item in icons:
                icon = icons[item]
                # Center 36px icon in 44px btn
                icon_x = btn_x + 4
                icon_y = y + 4
                frame.paste(icon, (icon_x, icon_y), icon)

            y += btn_h + gap

        # Swatches
        swatch_y = bottom - 55
        draw.rectangle([10, swatch_y, 30, swatch_y + 20], fill=(0, 0, 0), outline=PSColors.MUTED)  # type: ignore[arg-type]
        draw.rectangle(
            [18, swatch_y + 10, 38, swatch_y + 30],  # type: ignore[arg-type]
            fill=(255, 255, 255),
            outline=PSColors.MUTED,  # type: ignore[unused-ignore]
        )

    def draw_right(self, draw: ImageDraw.ImageDraw, frame: Image.Image) -> None:
        """Draw right actions toolbar."""
        top = HEADER_HEIGHT
        bottom = VIDEO_HEIGHT - LAYERS_PANEL_HEIGHT
        left = VIDEO_WIDTH - RIGHT_TOOLBAR_WIDTH

        draw.rectangle([left, top, VIDEO_WIDTH, bottom], fill=PSColors.PANEL)  # type: ignore[arg-type]
        draw.line([(left, top), (left, bottom)], fill=PSColors.BORDER)

        sidebar_mapping = {
            "layers": "icon_layer.png",
            "properties": "icon_setting.png",
            "color": "icon_color_palette.png",
            "history": "icon_history .png",
            "settings": None,
        }

        icons = {}
        for key, fname in sidebar_mapping.items():
            if fname:
                path = os.path.join(ICONS_DIR, "sidebar", fname)
                if os.path.exists(path):
                    try:
                        icons[key] = (
                            Image.open(path)
                            .convert("RGBA")
                            .resize((36, 36), Image.Resampling.LANCZOS)
                        )
                    except Exception:
                        pass

        sidebar_tools = ["layers", "properties", "color", "history"]
        y = top + 20

        for name in sidebar_tools:
            if name in icons:
                icon = icons[name]
                # Center 36px icon in 50px toolbar -> offset 7
                frame.paste(icon, (VIDEO_WIDTH - 50 + 7, y), icon)
            else:
                # Fallback MDI
                mdi_map = {
                    "layers": "layers",
                    "properties": "tune-vertical",
                    "color": "palette",
                    "history": "history",
                }
                self.draw_mdi_fallback(
                    frame,
                    mdi_map.get(name, "help"),
                    VIDEO_WIDTH - 48,
                    y + 2,
                    size=32,
                    color=PSColors.ICON_GRAY,
                )

            y += 85  # Increased spacing per user feedback
