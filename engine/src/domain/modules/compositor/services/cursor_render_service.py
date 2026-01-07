"""
CursorRenderService: Renders cursor PNG overlay on composed frames.

Responsibility: Load cursor icon via AssetProviderPort, render at CursorState position.
"""

from PIL import Image

from ....ports import AssetProviderPort
from ....value_objects.compositor import CursorState


class CursorRenderService:
    """
    Service for rendering cursor PNG overlay on frames.

    Uses AssetProviderPort to load cursor icons, caches them for performance.
    """

    def __init__(self, asset_provider: AssetProviderPort):
        self.asset_provider = asset_provider
        self._cursor_cache: dict[str, Image.Image | None] = {}

    def render_cursor(
        self, frame: Image.Image, cursor_state: CursorState, hotspot: tuple[int, int] = (0, 0)
    ) -> Image.Image:
        """
        Render cursor PNG onto frame at cursor position.

        Args:
            frame: Target frame to render cursor onto
            cursor_state: Cursor position and visibility state
            hotspot: Cursor hotspot offset (tip of arrow)

        Returns:
            Frame with cursor rendered
        """
        if not cursor_state.visible:
            return frame

        cursor_img = self._get_cursor_image(cursor_state.tool_type)
        if cursor_img is None:
            return frame

        # Apply scale if needed
        if cursor_state.scale != 1.0:
            new_size = (
                int(cursor_img.width * cursor_state.scale),
                int(cursor_img.height * cursor_state.scale),
            )
            cursor_img = cursor_img.resize(new_size, Image.Resampling.LANCZOS)

        # Calculate position (adjust for hotspot)
        x = int(cursor_state.position.x) - hotspot[0]
        y = int(cursor_state.position.y) - hotspot[1]

        # Paste with alpha mask
        try:
            if cursor_img.mode == "RGBA":
                frame.paste(cursor_img, (x, y), cursor_img)
            else:
                frame.paste(cursor_img, (x, y))
        except Exception:
            pass  # Ignore out-of-bounds paste

        return frame

    def _get_cursor_image(self, tool_type: str) -> Image.Image | None:
        """Get cached cursor image or load from asset provider."""
        if tool_type not in self._cursor_cache:
            cursor = self.asset_provider.get_cursor_icon(tool_type)
            if cursor is not None and isinstance(cursor, Image.Image):
                self._cursor_cache[tool_type] = cursor.convert("RGBA")
            else:
                self._cursor_cache[tool_type] = None
        return self._cursor_cache.get(tool_type)

    def clear_cache(self) -> None:
        """Clear cursor image cache."""
        self._cursor_cache.clear()


def draw_cursor_png(frame: Image.Image, cursor_img: Image.Image, x: int, y: int) -> None:
    """
    Simple function to paste cursor PNG onto frame.

    Args:
        frame: Target frame
        cursor_img: Cursor PNG image
        x, y: Position to paste
    """
    try:
        if cursor_img.mode == "RGBA":
            frame.paste(cursor_img, (x, y), cursor_img)
        else:
            frame.paste(cursor_img, (x, y))
    except Exception:
        pass
