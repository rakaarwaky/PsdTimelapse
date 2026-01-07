from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from .layer_type_value import LayerType


@dataclass
class CompositeLayer:
    """A single layer in the composition stack."""

    name: str
    layer_type: LayerType
    z_index: int = 0

    # Static layer data
    static_image: Optional["Image.Image"] = None

    # Dynamic layer data
    frame_count: int = 0
    _frame_generator: Callable[[int], "Image.Image"] | None = None


# Backward compatibility alias
RenderLayer = CompositeLayer
