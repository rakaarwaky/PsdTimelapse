"""
MultiLayerCompositor: Orchestrates multi-layer composition for speed optimization.
Separates static layers (compose 1x) from dynamic layers (compose per frame).
Dependencies: PIL Image
"""

from __future__ import annotations

from collections.abc import Callable, Generator
from typing import Any

from ....value_objects.compositor import CompositeFrame, CompositeLayer, LayerType

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class MultiLayerCompositor:
    """
    Orchestrates multi-layer composition for speed optimization.

    Separates static layers (UI chrome) from dynamic layers (animated content).
    Static layers are composed once and reused for all frames.
    """

    def __init__(self, width: int, height: int, background_color: tuple[Any, ...] = (0, 0, 0, 0)):
        if not HAS_PILLOW:
            raise ImportError("Pillow required for MultiLayerCompositor")

        self.width = width
        self.height = height
        self.background_color = background_color
        self._layers: list[CompositeLayer] = []
        self._static_cache: dict[str, Image.Image] = {}

    def add_static_layer(self, name: str, image: Image.Image, z_index: int = 0) -> None:
        """
        Add a static layer that composes once and is reused.

        Args:
            name: Layer identifier
            image: Pre-composed image for this layer
            z_index: Stacking order (higher = on top)
        """
        layer = CompositeLayer(
            name=name, layer_type=LayerType.STATIC, z_index=z_index, static_image=image
        )
        self._layers.append(layer)
        self._static_cache[name] = image

    def add_dynamic_layer(
        self,
        name: str,
        frame_generator: Callable[[int], Image.Image],
        frame_count: int,
        z_index: int = 0,
    ) -> None:
        """
        Add a dynamic layer that composes each frame.

        Args:
            name: Layer identifier
            frame_generator: Function that generates frame image given frame number
            frame_count: Total number of frames
            z_index: Stacking order (higher = on top)
        """
        layer = CompositeLayer(
            name=name,
            layer_type=LayerType.DYNAMIC,
            z_index=z_index,
            frame_count=frame_count,
            _frame_generator=frame_generator,
        )
        self._layers.append(layer)

    def _get_sorted_layers(self) -> list[CompositeLayer]:
        """Get layers sorted by z_index (lowest first)."""
        return sorted(self._layers, key=lambda layer: layer.z_index)

    def compose_frame(self, frame_number: int) -> Image.Image:
        """
        Compose a single frame by merging all layers.

        Args:
            frame_number: Current frame index

        Returns:
            Composed PIL Image
        """
        # Create base frame
        frame = Image.new("RGBA", (self.width, self.height), self.background_color)

        # Composite each layer in z-order
        for layer in self._get_sorted_layers():
            layer_image = self._get_layer_image(layer, frame_number)
            if layer_image:
                # Ensure RGBA for alpha compositing
                if layer_image.mode != "RGBA":
                    layer_image = layer_image.convert("RGBA")
                frame = Image.alpha_composite(frame, layer_image)

        return frame

    def _get_layer_image(self, layer: CompositeLayer, frame_number: int) -> Image.Image | None:
        """Get image for a layer at given frame."""
        if layer.layer_type == LayerType.STATIC:
            return layer.static_image
        elif layer.layer_type == LayerType.DYNAMIC:
            if layer._frame_generator:
                return layer._frame_generator(frame_number)
        return None

    def iterate_frames(self, total_frames: int) -> Generator[CompositeFrame, None, None]:
        """
        Iterate and compose all frames.

        Args:
            total_frames: Total number of frames to generate

        Yields:
            CompositeFrame with frame number and composed image
        """
        for frame_num in range(total_frames):
            image = self.compose_frame(frame_num)
            yield CompositeFrame(frame_number=frame_num, image=image)

    def get_layer_count(self) -> dict[str, Any]:
        """Get count of layers by type."""
        static_count = sum(1 for layer in self._layers if layer.layer_type == LayerType.STATIC)
        dynamic_count = sum(1 for layer in self._layers if layer.layer_type == LayerType.DYNAMIC)
        return {"static": static_count, "dynamic": dynamic_count, "total": len(self._layers)}

    def clear(self) -> None:
        """Clear all layers and cache."""
        self._layers.clear()
        self._static_cache.clear()
