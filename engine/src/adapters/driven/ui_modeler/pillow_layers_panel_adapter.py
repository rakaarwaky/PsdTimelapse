"""
Renderer for the Layers Panel (Bottom Drawer).
"""

import os
from typing import Any

from PIL import Image, ImageDraw

from .pillow_base_adapter import BaseRenderer
from .pillow_constants_adapter import (
    ICONS_DIR,
    LAYERS_PANEL_HEIGHT,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
    PSColors,
)


class LayersPanelRenderer(BaseRenderer):
    """Renders the layers panel at the bottom of the screen."""

    def draw(
        self, draw: ImageDraw.ImageDraw, frame: Image.Image, layers: list[Any], active_idx: int
    ) -> None:
        """Draw the complete layers panel."""
        panel_x = 0
        panel_y = VIDEO_HEIGHT - LAYERS_PANEL_HEIGHT
        panel_w = VIDEO_WIDTH
        panel_h = LAYERS_PANEL_HEIGHT

        # Background
        draw.rectangle(
            [panel_x, panel_y, panel_x + panel_w, panel_y + panel_h],  # type: ignore[arg-type]
            fill=PSColors.PANEL,  # type: ignore[unused-ignore]
        )
        draw.line([(panel_x, panel_y), (panel_x + panel_w, panel_y)], fill=PSColors.BORDER)

        # Header Tabs
        self._draw_tabs(draw, panel_x, panel_y, panel_w)

        # Load Icons
        icons = self._load_layer_icons()  # type: ignore[no-untyped-call]

        # Lock Status Row (below tabs)
        self._draw_lock_status(draw, frame, panel_x, panel_y, icons)

        # Layers List
        self._draw_layer_list(draw, frame, layers, active_idx, panel_x, panel_y, icons)

        # Footer Actions
        self._draw_footer(frame, panel_x, icons)

    def _draw_tabs(self, draw: ImageDraw.ImageDraw, x: int, y: int, w: int) -> None:
        header_y = y
        tab_h = 36
        draw.rectangle([x, header_y, x + w, header_y + tab_h], fill=PSColors.LAYER_TAB)  # type: ignore[arg-type]

        draw.text((x + 20, header_y + 10), "Layers", font=self.fonts["bold"], fill=PSColors.TEXT)
        draw.text((x + 90, header_y + 10), "Channels", font=self.fonts["std"], fill=PSColors.MUTED)
        draw.text((x + 180, header_y + 10), "Paths", font=self.fonts["std"], fill=PSColors.MUTED)

        # Active Indicator
        draw.line([(x + 15, header_y + 34), (x + 70, header_y + 34)], fill=PSColors.ACCENT, width=2)

    def _load_layer_icons(self):  # type: ignore[no-untyped-def]
        """Load specific icons for layers panel."""
        icons = {}
        # Map logical names to filenames
        icon_map = {
            "eye_on": "icon_eye.png",
            "eye_off": "icon_eye_disable.png",
            "lock": "icon_lock.png",
            "unlock": "icon_unlock.png",
            "link": "icon_link.png",
            "fx": "icon_fx.png",
            "mask": "icon_mask.png",
            "adjustment": "icon_add+.png",
            "group": "icon_group.png",
            "delete": "icon_delete.png",
            "new": "icon_+.png",
            "folder": "icon_folder.png",
        }

        for key, fname in icon_map.items():
            path = os.path.join(ICONS_DIR, "layers", fname)
            if os.path.exists(path):
                try:
                    # Specific sizing
                    size = (24, 24)
                    if key in ["eye_on", "eye_off", "lock", "unlock"]:
                        size = (16, 16)
                    icons[key] = (
                        Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                    )
                except Exception:
                    pass
        return icons

    def _draw_lock_status(
        self, draw: ImageDraw.ImageDraw, frame: Image.Image, x: int, y: int, icons: dict[str, Any]
    ) -> None:
        lock_y = y + 50
        draw.text((x + 12, lock_y + 2), "Lock:", fill=PSColors.MUTED, font=self.fonts["sm"])
        if "unlock" in icons:
            self.draw_icon(frame, icons["unlock"], x + 50, lock_y + 2)

    def _draw_layer_list(  # noqa: PLR0913, PLR0912
        self,
        draw: ImageDraw.ImageDraw,
        frame: Image.Image,
        layers: list[Any],
        active_idx: int,
        panel_x: int,
        panel_y: int,
        icons: dict[str, Any],
    ) -> None:
        list_y = panel_y + 90
        layer_h = 50
        display_layers = layers[::-1]  # Top visual layer first

        for i, layer in enumerate(display_layers):
            layer_y = list_y + (i * layer_h)

            # Active Highlight
            is_active = (len(layers) - 1 - i) == active_idx
            if is_active:
                draw.rectangle(
                    [panel_x, layer_y, panel_x + VIDEO_WIDTH, layer_y + layer_h],  # type: ignore[arg-type]
                    fill=PSColors.SELECTED,
                )

            # Visibility
            eye_x, eye_y = panel_x + 10, layer_y + 17
            visible = layer.get("visible", True)
            eye_key = "eye_on" if visible else "eye_off"

            if eye_key in icons:
                self.draw_icon(frame, icons[eye_key], eye_x, eye_y)
            else:
                draw.ellipse([eye_x, eye_y, eye_x + 16, eye_y + 16], outline=PSColors.TEXT)

            # Thumbnail
            thumb_x = panel_x + 35
            thumb_y = layer_y + 7
            draw.rectangle([thumb_x, thumb_y, thumb_x + 36, thumb_y + 36], fill=(255, 255, 255))  # type: ignore[arg-type]
            if layer.get("type") == "group" and "folder" in icons:
                f_icon = icons["folder"].resize((24, 24), Image.Resampling.LANCZOS)
                self.draw_icon(frame, f_icon, thumb_x + 6, thumb_y + 6)

            # Name
            draw.text(
                (thumb_x + 46, layer_y + 15),
                layer.get("name", "Layer"),
                font=self.fonts["std"],
                fill=PSColors.TEXT,
            )

            # Lock Icon on right
            if layer.get("locked") and "lock" in icons:
                self.draw_icon(frame, icons["lock"], VIDEO_WIDTH - 35, layer_y + 17)

            # Divider
            draw.line(
                [(panel_x, layer_y + layer_h), (panel_x + VIDEO_WIDTH, layer_y + layer_h)],
                fill=PSColors.DIVIDER,
            )

    def _draw_footer(self, frame: Image.Image, panel_x: int, icons: dict[str, Any]) -> None:
        # Action Bar at bottom
        action_y = VIDEO_HEIGHT - 36

        # Left Actions
        left_actions = ["link", "fx", "mask", "adjustment"]
        lx = panel_x + 15
        for name in left_actions:
            if name in icons:
                self.draw_icon(frame, icons[name], lx, action_y + 6)
            lx += 35

        # Right Actions
        right_actions = ["group", "new", "delete"]
        rx = VIDEO_WIDTH - (len(right_actions) * 35) - 10
        for name in right_actions:
            if name in icons:
                self.draw_icon(frame, icons[name], rx, action_y + 6)
            rx += 35
