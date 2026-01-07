from enum import Enum


class LayerType(Enum):
    """Type of render layer."""

    STATIC = "static"  # Render once, reuse
    DYNAMIC = "dynamic"  # Render per frame
