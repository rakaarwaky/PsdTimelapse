"""
CompositorPort: Interface for GPU-accelerated blend operations.
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod
from typing import Any


class CompositorPort(ABC):
    """
    Port interface for GPU compositing operations.

    Abstracts low-level blend operations to allow swapping between
    different GPU backends (CuPy, OpenGL, etc).

    Adapters implementing this port:
    - cupy_compositor.py (CuPy-based GPU blending)
    """

    @abstractmethod
    def blend(self, target: Any, source: Any, x: int, y: int) -> None:
        """
        Blend source image onto target at position (in-place).

        Args:
            target: Destination image (GPU array).
            source: Source image to blend (GPU array).
            x: X position on target.
            y: Y position on target.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if GPU backend is available.

        Returns:
            True if GPU compositing is available.
        """
        pass
