"""
Renderer for the top header/menubar.
"""

import os

from PIL import Image, ImageDraw

from .pillow_base_adapter import HAS_MDI, BaseRenderer
from .pillow_constants_adapter import HEADER_HEIGHT, ICONS_DIR, VIDEO_WIDTH, PSColors


class HeaderRenderer(BaseRenderer):
    """Renders the top application bar."""

    MENU_ITEMS = [
        "File",
        "Edit",
        "Image",
        "Layer",
        "Type",
        "Select",
        "Filter",
        "3D",
        "View",
        "Plugins",
        "Window",
        "Help",
    ]

    def draw(self, draw: ImageDraw.ImageDraw, frame: Image.Image) -> None:
        """Draw header background, logo, and menu."""
        # Background
        draw.rectangle([0, 0, VIDEO_WIDTH, HEADER_HEIGHT], fill=PSColors.DARK)
        draw.line([(0, HEADER_HEIGHT), (VIDEO_WIDTH, HEADER_HEIGHT)], fill=PSColors.BORDER)

        # Ps Logo
        self._draw_logo(draw, frame)

        # Menu items
        x_pos = 56
        for item in self.MENU_ITEMS:
            draw.text((x_pos, 17), item, fill=PSColors.TEXT, font=self.fonts["std"])
            x_pos += len(item) * 9 + 20

        # Undo/Redo (Right side)
        self._draw_undo_redo(frame)

    def _draw_logo(self, draw: ImageDraw.ImageDraw, frame: Image.Image):
        """Draw Ps logo with transparency fix."""
        logo_path = os.path.join(ICONS_DIR, "header", "Ps_logo.png")
        logo_x, logo_y = 8, 6
        logo_size = 36

        if os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path).convert("RGBA")
                # Simple transparency hack for gray bg
                pixel_data = logo.getdata()
                new_data = []
                for item in pixel_data:
                    if item[0] < 60 and item[1] < 60 and item[2] < 60:
                        new_data.append((item[0], item[1], item[2], 0))
                    else:
                        new_data.append(item)
                logo.putdata(new_data)
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                frame.paste(logo, (logo_x, logo_y), logo)
                return
            except Exception:
                pass

        # Fallback
        draw.rectangle(
            [logo_x, logo_y, logo_x + logo_size, logo_y + logo_size],
            fill=(0, 30, 54),
            outline=PSColors.ACCENT,
        )
        draw.text((logo_x + 8, logo_y + 10), "Ps", fill=PSColors.ACCENT, font=self.fonts["bold"])

    def _draw_undo_redo(self, frame: Image.Image):
        """Draw undo/redo buttons."""
        if not HAS_MDI:
            return

        undo_x = VIDEO_WIDTH - 100
        # draw.rectangle not needed if just icons, but let's keep it clean
        try:
            # We need draw object for rectangle, passed frame only here?
            # Ideally pas draw everywhere. But for icons we paste on frame.
            # Let's use mdi directly
            self.draw_mdi_fallback(frame, "undo", undo_x + 5, 12, size=24, color=PSColors.MUTED)
            self.draw_mdi_fallback(frame, "redo", undo_x + 40, 12, size=24, color=PSColors.MUTED)
        except Exception:
            pass
