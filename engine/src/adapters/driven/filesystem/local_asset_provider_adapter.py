"""
LocalAssetProviderAdapter: File-system based implementation of AssetProviderPort.
Dependencies: pillow, os, Domain.Ports.AssetProviderPort
"""

import os
from typing import Any

try:
    from PIL import Image, ImageFont

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from domain.ports.store.asset_provider_port import AssetProviderPort


class LocalAssetProviderAdapter(AssetProviderPort):
    """
    Adapter for loading assets from the local file system.
    Expects an 'assets' directory structure.
    """

    def __init__(self, assets_dir: str = "assets"):
        self._assets_dir = assets_dir

    def get_cursor_icon(self, cursor_type: str) -> Any | None:
        """Load cursor icon from assets/cursors/."""
        path = os.path.join(self._assets_dir, "cursors", f"{cursor_type}.png")
        return self._load_image(path)

    def get_font(self, style: str, size: int) -> Any:
        """Load font from assets/fonts/."""
        if not HAS_PILLOW:
            return None

        font_name = f"{style.lower()}.ttf"
        path = os.path.join(self._assets_dir, "fonts", font_name)

        try:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
            else:
                return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()

    def get_texture(self, name: str) -> Any | None:
        """Load texture from assets/textures/."""
        path = os.path.join(self._assets_dir, "textures", f"{name}.png")
        return self._load_image(path)

    def get_icon(self, name: str, size: int = 24) -> Any | None:
        """Load icon from assets/icons/."""
        path = os.path.join(self._assets_dir, "icons", f"{name}.png")
        img = self._load_image(path)
        if img:
            try:
                img = img.resize((size, size))
            except Exception:
                pass
        return img

    def list_available_fonts(self) -> list[str]:
        fonts_dir = os.path.join(self._assets_dir, "fonts")
        if not os.path.exists(fonts_dir):
            return []

        fonts = []
        for f in os.listdir(fonts_dir):
            if f.endswith((".ttf", ".otf")):
                fonts.append(os.path.splitext(f)[0])
        return sorted(fonts)

    def _load_image(self, path: str) -> Any | None:
        if not HAS_PILLOW or not os.path.exists(path):
            return None
        try:
            return Image.open(path)
        except Exception:
            return None
