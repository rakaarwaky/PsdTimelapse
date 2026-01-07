"""
GPU Backend for PipelineManager.
Uses CuPy for accelerated compositing operations.

NOTE: Compositor implementation is now injected via CompositorPort (Hexagonal Architecture).
"""

from typing import Any

import numpy as np  # type: ignore[unused-ignore]

from ....ports.render.compositor_port import CompositorPort

try:
    import cupy as cp  # type: ignore[import-not-found]
    import cupyx.scipy.ndimage  # type: ignore[import-not-found]

    HAS_GPU_BACKEND = True
except ImportError:
    HAS_GPU_BACKEND = False

try:
    from PIL import Image
except ImportError:
    pass  # Should be available

from ..orchestrator.pipeline_manager_module import CompositingBackend


class GpuBackend(CompositingBackend):
    """
    CuPy-based backend for PipelineManager.
    Performs all operations on GPU.

    Args:
        compositor: Injected compositor implementation (e.g., CupyCompositor).
    """

    RGBA_CHANNELS = 4

    def __init__(self, compositor: CompositorPort):
        if not HAS_GPU_BACKEND:
            raise ImportError("CuPy not installed or GPU not available")
        self.compositor = compositor

    def copy(self, image: Any) -> Any:
        """Copy CuPy array."""
        return cp.copy(image)

    def resize(self, image: Any, size: tuple[int, int]) -> Any:
        """
        Resize CuPy array using spline interpolation (order=1 for speed, or 3 for quality).
        PIL Lanczos is sinc-based. Bicubic (order=3) is closest standard approximation.
        """
        target_w, target_h = size
        h, w, _ = image.shape

        # Calculate zoom factors
        zoom_h = target_h / h
        zoom_w = target_w / w

        # Perform resize
        # order=1 (bilinear) is fast. order=3 (bicubic) looks better.
        # mode='constant', cval=0.0 handles edges transparency.
        # We process channels independently or together?
        # zoom supports multi-channel if zoom factor 1 for channel dim.
        return cupyx.scipy.ndimage.zoom(
            image, (zoom_h, zoom_w, 1), order=1, mode="constant", cval=0.0
        )

    def paste(self, target: Any, source: Any, pos: tuple[int, int]) -> None:
        """Paste source onto target at pos (in-place) using GPU blend."""
        x, y = pos
        self.compositor.blend(target, source, int(x), int(y))

    def get_size(self, image: Any) -> tuple[int, int]:
        """Return (width, height) from shape (H, W, C)."""
        h, w, _ = image.shape
        return w, h

    def is_rgba(self, image: Any) -> bool:
        """Check if 4 channels."""
        return bool(image.shape[2] == self.RGBA_CHANNELS)

    def to_device(self, image: Any) -> Any:
        """Convert PIL/Numpy/Other to GPU array."""
        if hasattr(image, "convert"):
            # Convert PIL to Numpy first
            arr = np.array(image.convert("RGBA")).astype(np.float32) / 255.0
        elif isinstance(image, np.ndarray):
            arr = image.astype(np.float32)
            if arr.dtype == np.uint8:
                arr /= 255.0
        elif isinstance(image, cp.ndarray):
            return image
        else:
            arr = image

        return cp.asarray(arr)

    def to_cpu(self, image: Any) -> Any:
        """Convert GPU array to PIL Image."""
        arr = cp.asnumpy(image)
        arr_u8 = (arr * 255).astype(np.uint8)
        return Image.fromarray(arr_u8, mode="RGBA")
