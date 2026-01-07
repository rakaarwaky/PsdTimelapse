"""
OverlayPort: Interface for UI overlay rendering.
Dependencies: Vector2 (value object)
"""

from abc import ABC, abstractmethod
from typing import Any

from ...value_objects.geometry import Rect, Vector2


class CursorType:
    """Cursor type constants."""

    HAND = "hand"
    BRUSH = "brush"
    POINTER = "pointer"
    CROSSHAIR = "crosshair"


class OverlayPort(ABC):
    """
    Port interface for UI overlay rendering.

    Handles drawing of cursors, guides, and other UI elements
    on top of rendered frames.

    Adapters implementing this port:
    - pillow_overlay_adapter.py (PIL-based drawing)
    - cairo_overlay_adapter.py (vector graphics)
    """

    @abstractmethod
    def draw_cursor(
        self,
        image: Any,
        position: Vector2,
        cursor_type: str,
        visible: bool = True,
        scale: float = 1.0,
    ) -> Any:
        """
        Draw cursor overlay on image.

        Args:
            image: Base image to draw on.
            position: Cursor position (viewport coordinates).
            cursor_type: Type of cursor (hand, brush, etc).
            visible: Whether cursor should be visible.
            scale: Cursor scale factor.

        Returns:
            Image with cursor overlay.
        """
        pass

    @abstractmethod
    def draw_selection_guides(
        self, image: Any, rect: Rect, color: tuple[Any, ...] = (
            0,
            120,
            255,
            180), line_width: int = 2
    ) -> Any:
        """
        Draw selection rectangle guides.

        Args:
            image: Base image.
            rect: Selection rectangle.
            color: Guide color (RGBA).
            line_width: Line thickness.

        Returns:
            Image with selection guides.
        """
        pass

    @abstractmethod
    def draw_progress_bar(
        self, image: Any, progress: float, position: Vector2, width: int = 200, height: int = 10
    ) -> Any:
        """
        Draw progress bar overlay.

        Args:
            image: Base image.
            progress: Progress value (0.0 to 1.0).
            position: Top-left position of bar.
            width: Bar width in pixels.
            height: Bar height in pixels.

        Returns:
            Image with progress bar.
        """
        pass

    @abstractmethod
    def draw_text(
        self,
        image: Any,
        text: str,
        position: Vector2,
        font_size: int = 14,
        color: tuple[Any, ...] = (255, 255, 255, 255),
    ) -> Any:
        """
        Draw text overlay.

        Args:
            image: Base image.
            text: Text to draw.
            position: Text position.
            font_size: Font size in pixels.
            color: Text color (RGBA).

        Returns:
            Image with text overlay.
        """
        pass


class NullOverlay(OverlayPort):
    """No-op overlay for testing or headless operation."""

    def draw_cursor(
        self,
        image: Any,
        position: Vector2,
        cursor_type: str,
        visible: bool = True,
        scale: float = 1.0,
    ) -> Any:
        return image

    def draw_selection_guides(
        self, image: Any, rect: Rect, color: tuple[Any, ...] = (
            0,
            120,
            255,
            180), line_width: int = 2
    ) -> Any:
        return image

    def draw_progress_bar(
        self, image: Any, progress: float, position: Vector2, width: int = 200, height: int = 10
    ) -> Any:
        return image

    def draw_text(
        self,
        image: Any,
        text: str,
        position: Vector2,
        font_size: int = 14,
        color: tuple[Any, ...] = (255, 255, 255, 255),
    ) -> Any:
        return image
