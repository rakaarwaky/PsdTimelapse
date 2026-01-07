"""
ImageProcessingPort: Interface for pixel-level image operations.
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod
from typing import Any


class ImageProcessingPort(ABC):
    """
    Port interface for pixel-level image operations.

    Abstracts image manipulation to allow swapping between
    CPU (Pillow/OpenCV) and GPU (CuPy/PyImageCUDA) backends.

    Adapters implementing this port:
    - pillow_image_adapter.py (CPU-based, default)
    - opencv_image_adapter.py (optimized CPU)
    - cupy_image_adapter.py (GPU-accelerated)
    """

    @abstractmethod
    def create_canvas(
        self, width: int, height: int, color: tuple[int, int, int, int] = (0, 0, 0, 0)
    ) -> Any:
        """
        Create a blank canvas.

        Args:
            width: Canvas width in pixels.
            height: Canvas height in pixels.
            color: RGBA fill color.

        Returns:
            Image object (backend-specific type).
        """
        pass

    @abstractmethod
    def resize(self, image: Any, size: tuple[int, int], resample: str = "lanczos") -> Any:
        """
        Resize an image.

        Args:
            image: Source image.
            size: Target (width, height).
            resample: Resampling method.

        Returns:
            Resized image.
        """
        pass

    @abstractmethod
    def paste(
        self, target: Any, source: Any, position: tuple[int, int], mask: Any | None = None
    ) -> Any:
        """
        Paste source onto target at position.

        Args:
            target: Destination image.
            source: Image to paste.
            position: (x, y) top-left position.
            mask: Optional alpha mask.

        Returns:
            Composited image.
        """
        pass

    @abstractmethod
    def apply_mask(self, image: Any, mask: Any) -> Any:
        """
        Apply alpha mask to image.

        Args:
            image: Source RGBA image.
            mask: Grayscale mask (L mode).

        Returns:
            Masked image.
        """
        pass

    @abstractmethod
    def gaussian_blur(self, image: Any, radius: float) -> Any:
        """
        Apply Gaussian blur to image.

        Args:
            image: Source image.
            radius: Blur radius.

        Returns:
            Blurred image.
        """
        pass

    @abstractmethod
    def draw_ellipse(
        self, image: Any, bbox: tuple[float, float, float, float], fill: tuple[int, ...]
    ) -> Any:
        """
        Draw filled ellipse on image.

        Args:
            image: Target image.
            bbox: Bounding box (x1, y1, x2, y2).
            fill: Fill color.

        Returns:
            Image with ellipse drawn.
        """
        pass

    @abstractmethod
    def get_size(self, image: Any) -> tuple[int, int]:
        """
        Get image dimensions.

        Returns:
            (width, height)
        """
        pass

    @abstractmethod
    def copy(self, image: Any) -> Any:
        """Create a copy of the image."""
        pass

    @abstractmethod
    def to_numpy(self, image: Any) -> Any:
        """Convert to numpy array."""
        pass

    @abstractmethod
    def from_numpy(self, array: Any) -> Any:
        """Create image from numpy array."""
        pass

    @abstractmethod
    def split_channels(self, image: Any) -> tuple[Any, ...]:
        """Split image into individual channels."""
        pass

    @abstractmethod
    def merge_channels(self, channels: tuple[Any, ...], mode: str = "RGBA") -> Any:
        """Merge channels back into image."""
        pass
