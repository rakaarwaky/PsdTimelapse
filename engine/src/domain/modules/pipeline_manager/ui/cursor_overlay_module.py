"""
CursorOverlay: Render cursor icons on top of composited frames.
Separated from compositor for proper separation of concerns.
Dependencies: PIL Image
Migrated from render_manager to pipeline_manager.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from PIL import Image

from ....value_objects.geometry.vector_value import Vector2

# Cursor icon paths (relative to project root)
CURSOR_ICONS_DIR = Path(__file__).parent.parent.parent.parent / "assets" / "ui_icons" / "toolbar"
HAND_ICON_PATH = CURSOR_ICONS_DIR / "icon_hand.png"
BRUSH_ICON_PATH = CURSOR_ICONS_DIR / "icon_brush.png"


class CursorOverlay:
    """
    Handles cursor icon rendering on top of composited frames.

    Loads cursor icons once and caches them for reuse.
    """

    def __init__(self, icon_size: int = 32):
        """
        Initialize cursor overlay.

        Args:
            icon_size: Size to scale cursor icons to
        """
        self.icon_size = icon_size
        self._hand_icon: Image.Image | None = None
        self._brush_icon: Image.Image | None = None
        self._load_icons()

    def _load_icons(self) -> None:
        """Load and cache cursor icons."""
        try:
            if HAND_ICON_PATH.exists():
                self._hand_icon = Image.open(HAND_ICON_PATH).convert("RGBA")
                self._hand_icon = self._hand_icon.resize(
                    (self.icon_size, self.icon_size), Image.Resampling.LANCZOS
                )

            if BRUSH_ICON_PATH.exists():
                self._brush_icon = Image.open(BRUSH_ICON_PATH).convert("RGBA")
                self._brush_icon = self._brush_icon.resize(
                    (self.icon_size, self.icon_size), Image.Resampling.LANCZOS
                )
        except Exception as e:
            print(f"Warning: Could not load cursor icons: {e}")

    def overlay_cursor(
        self,
        frame: Image.Image,
        position: Vector2,
        cursor_type: Literal["hand", "brush"] = "hand",
        visible: bool = True,
    ) -> Image.Image:
        """
        Overlay cursor icon on frame.

        Args:
            frame: Base frame image (will be modified in-place)
            position: Cursor position in viewport coordinates
            cursor_type: Type of cursor to show
            visible: Whether cursor should be visible

        Returns:
            Frame with cursor overlay
        """
        if not visible:
            return frame

        # Select icon
        icon = self._hand_icon if cursor_type == "hand" else self._brush_icon
        if icon is None:
            return frame

        # Calculate paste position (center icon on cursor position)
        paste_x = int(position.x - self.icon_size // 2)
        paste_y = int(position.y - self.icon_size // 2)

        # Ensure we don't paste outside frame bounds
        if paste_x < 0 or paste_y < 0:
            return frame
        if paste_x + self.icon_size > frame.width or paste_y + self.icon_size > frame.height:
            return frame

        # Paste cursor with alpha
        frame.paste(icon, (paste_x, paste_y), icon)

        return frame


def create_cursor_overlay(icon_size: int = 32) -> CursorOverlay:
    """Factory function to create CursorOverlay instance."""
    return CursorOverlay(icon_size=icon_size)
