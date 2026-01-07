"""
ExrExportPort: Interface for exporting frames to EXR format.
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod
from typing import Any


class ExrExportPort(ABC):
    """
    Port interface for exporting High Dynamic Range (EXR) images.

    Used for:
    - Beauty pass (RGB Float32)
    - Motion Vectors (Velocity XY Float32)
    - Depth pass (Z Float32)

    Adapters implementing this port:
    - exr_renderer_adapter.py (uses OpenCV)
    """

    @abstractmethod
    def export(self, file_path: str, image_data: Any, compression: str = "ZIP") -> bool:
        """
        Export image data to an EXR file.

        Args:
            file_path: Absolute path to output file (must end in .exr).
            image_data: Image data (typically numpy array or compliant object).
                        Must be convertible to Float32.
            compression: Compression type hint (ZIP, PIZ, RLE, NONE).

        Returns:
            True if export succeeded, False otherwise.

        Raises:
            IOError: If file cannot be written.
            ValueError: If image data is incompatible.
        """
        pass
