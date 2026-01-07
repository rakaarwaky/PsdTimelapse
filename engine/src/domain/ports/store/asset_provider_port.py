"""
AssetProviderPort: Interface for system asset loading.
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod
from typing import Any


class AssetProviderPort(ABC):
    """
    Port interface for system asset loading.

    Provides icons, fonts, textures, and other system resources
    needed for UI rendering.

    Adapters implementing this port:
    - file_asset_provider.py (loads from disk)
    - embedded_asset_provider.py (bundled resources)
    """

    @abstractmethod
    def get_cursor_icon(self, cursor_type: str) -> Any | None:
        """
        Get cursor icon image.

        Args:
            cursor_type: Type of cursor (hand, brush, pointer).

        Returns:
            Cursor image or None if not found.
        """
        pass

    @abstractmethod
    def get_font(self, style: str, size: int) -> Any:
        """
        Get font object for text rendering.

        Args:
            style: Font style (regular, bold, mono).
            size: Font size in points.

        Returns:
            Font object (backend-specific).
        """
        pass

    @abstractmethod
    def get_texture(self, name: str) -> Any | None:
        """
        Get named texture asset.

        Args:
            name: Texture identifier.

        Returns:
            Texture image or None if not found.
        """
        pass

    @abstractmethod
    def get_icon(self, name: str, size: int = 24) -> Any | None:
        """
        Get UI icon by name.

        Args:
            name: Icon identifier.
            size: Desired icon size.

        Returns:
            Icon image or None if not found.
        """
        pass

    @abstractmethod
    def list_available_fonts(self) -> list[str]:
        """
        List all available font styles.

        Returns:
            List of font style names.
        """
        pass


class NullAssetProvider(AssetProviderPort):
    """No-op asset provider for testing."""

    def get_cursor_icon(self, cursor_type: str) -> Any | None:
        return None

    def get_font(self, style: str, size: int) -> Any:
        return None

    def get_texture(self, name: str) -> Any | None:
        return None

    def get_icon(self, name: str, size: int = 24) -> Any | None:
        return None

    def list_available_fonts(self) -> list[str]:
        return []
