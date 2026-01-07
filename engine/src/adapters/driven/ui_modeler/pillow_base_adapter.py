"""
Base renderer with shared utilities.
"""

try:
    from PIL import Image, ImageDraw

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    Image = None
    ImageDraw = None

try:
    from mdi_pil import MDI

    HAS_MDI = True
except ImportError:
    HAS_MDI = False
    MDI = None

from .pillow_constants_adapter import load_font


class BaseRenderer:
    """Base class for all UI renderers."""

    def __init__(self) -> None:
        if not HAS_PILLOW:
            raise ImportError("Pillow not installed")

        self.fonts = {
            "std": load_font(12),
            "bold": load_font(12),
            "sm": load_font(11),
            "lg": load_font(13),
            "xs": load_font(10),
        }

    def draw_icon(self, frame: Image.Image, icon: Image.Image, x: int, y: int) -> None:
        """Helper to safely paste RGBA icons."""
        if icon:
            frame.paste(icon, (int(x), int(y)), icon)

    def draw_mdi_fallback(
        self,
        frame: Image.Image,
        name: str,
        x: int,
        y: int,
        size: int = 24,
        color: tuple[int, int, int] = (200, 200, 200),
    ) -> None:
        """Draw MDI icon as fallback."""
        if HAS_MDI:
            try:
                icon = MDI(name, size=size, color=color)
                pil_icon = icon.as_pil_image()
                frame.paste(pil_icon, (int(x), int(y)), pil_icon)
            except Exception:
                pass
