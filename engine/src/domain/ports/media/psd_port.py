from abc import ABC, abstractmethod
from typing import Any

from ...entities.world_entity import WorldEntity

"""
PsdPort: Interface for PSD file loading operations.
Dependencies: WorldEntity
"""




class PsdPort(ABC):
    """
    Port interface for loading PSD files into the domain.

    Adapters implementing this port:
    - psd_tools_adapter.py (uses psd-tools library)
    """

    @abstractmethod
    def load(self, file_path: str) -> WorldEntity:
        """
        Load a PSD file and convert it to a WorldEntity.

        Args:
            file_path: Absolute path to the .psd file.

        Returns:
            WorldEntity populated with layers from the PSD.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file is not a valid PSD.
        """
        pass

    @abstractmethod
    def can_load(self, file_path: str) -> bool:
        """
        Check if this adapter can load the given file.

        Args:
            file_path: Path to check.

        Returns:
            True if file appears to be a valid PSD.
        """
        pass

    @abstractmethod
    def get_metadata(self, file_path: str) -> dict[str, Any]:
        """
        Extract metadata without fully loading the PSD.

        Returns:
            Dict with keys: width, height, layer_count, dpi
        """
        pass
