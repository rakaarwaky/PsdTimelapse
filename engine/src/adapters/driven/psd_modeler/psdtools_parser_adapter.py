"""
PsdToolsAdapter: Concrete implementation of PsdPort using psd-tools library.
Dependencies: psd-tools, Domain.Ports.PsdPort
"""

from __future__ import annotations

import os
from typing import Any

from domain.entities.document_entity import DocumentEntity
from domain.entities.layer_entity import BlendMode, LayerEntity
from domain.entities.scene_entity import SceneEntity
from domain.entities.world_entity import WorldEntity
from domain.ports.media.psd_port import PsdPort
from domain.value_objects.geometry.rect_value import Rect
from domain.value_objects.geometry.vector_value import Vector2
from domain.value_objects.visual.opacity_value import Opacity

try:
    from psd_tools import PSDImage
    from psd_tools.api.layers import Group, Layer

    HAS_PSD_TOOLS = True
except ImportError:
    HAS_PSD_TOOLS = False
    PSDImage = None


BLEND_MODE_MAP = {
    "normal": BlendMode.NORMAL,
    "multiply": BlendMode.MULTIPLY,
    "screen": BlendMode.SCREEN,
    "overlay": BlendMode.OVERLAY,
    "darken": BlendMode.DARKEN,
    "lighten": BlendMode.LIGHTEN,
    "color_dodge": BlendMode.COLOR_DODGE,
    "color_burn": BlendMode.COLOR_BURN,
    "soft_light": BlendMode.SOFT_LIGHT,
    "hard_light": BlendMode.HARD_LIGHT,
}


class PsdToolsAdapter(PsdPort):
    """
    Adapter for loading PSD files using psd-tools library.

    Converts PSD layer hierarchy to WorldEntity domain model.
    """

    def __init__(self):
        if not HAS_PSD_TOOLS:
            raise ImportError("psd-tools not installed. Run: pip install psd-tools")

    def load(self, file_path: str) -> WorldEntity:
        """Load PSD file and convert to WorldEntity."""
        if not self.can_load(file_path):
            raise ValueError(f"Cannot load file: {file_path}")

        psd = PSDImage.open(file_path)

        world = WorldEntity(
            width=psd.width,
            height=psd.height,
            name=os.path.basename(file_path),
            dpi=72,  # Default DPI, psd-tools doesn't expose this easily
        )

        # Create document with 1:1 aspect ratio and white background
        world.document = DocumentEntity.from_psd_dimensions(psd.width, psd.height)

        scene = SceneEntity()
        self._parse_layers(psd, scene, parent_id=None)
        world.scene = scene

        return world

    def _parse_layers(self, container, scene: SceneEntity, parent_id: str | None) -> None:
        """Recursively parse PSD layers into scene entities."""
        for idx, layer in enumerate(container):
            layer_id = f"{parent_id or 'root'}_{idx}"

            # Get bounding box
            try:
                left, top, right, bottom = layer.bbox
                bounds = Rect(float(left), float(top), float(right - left), float(bottom - top))
            except Exception:
                bounds = Rect(0, 0, 0, 0)

            # Map blend mode
            blend_str = getattr(layer, "blend_mode", "normal")
            if hasattr(blend_str, "value"):
                blend_str = blend_str.value
            blend_mode = BLEND_MODE_MAP.get(str(blend_str).lower(), BlendMode.NORMAL)

            # Check if group
            is_group = layer.is_group() if hasattr(layer, "is_group") else False

            # Get image data for pixel layers
            image_data = None
            if not is_group and hasattr(layer, "composite"):
                try:
                    image_data = layer.composite()
                except Exception:
                    pass

            # Calculate Center Position for the Entity
            # FrameCompositor expects position to be the CENTER of the layer
            center_x = bounds.x + (bounds.width / 2)
            center_y = bounds.y + (bounds.height / 2)

            entity = LayerEntity(
                id=layer_id,
                name=layer.name,
                z_index=idx,  # From enumerate iteration order
                position=Vector2(center_x, center_y),
                bounds=bounds,
                opacity=Opacity(layer.opacity / 255.0)
                if hasattr(layer, "opacity")
                else Opacity.OPAQUE,
                visible=layer.visible if hasattr(layer, "visible") else True,
                blend_mode=blend_mode,
                parent_id=parent_id,
                is_group=is_group,
                image_data=image_data,
            )

            scene.add_layer(entity)

            # Recursively parse children for groups
            if is_group:
                self._parse_layers(layer, scene, layer_id)

    def can_load(self, file_path: str) -> bool:
        """Check if file is a valid PSD."""
        if not os.path.exists(file_path):
            return False
        ext = os.path.splitext(file_path)[1].lower()
        return ext in (".psd", ".psb")

    def get_metadata(self, file_path: str) -> dict[str, Any]:
        """Get PSD metadata without full load."""
        if not self.can_load(file_path):
            return {}

        psd = PSDImage.open(file_path)
        layer_count = sum(1 for _ in psd.descendants())

        return {
            "width": psd.width,
            "height": psd.height,
            "layer_count": layer_count,
            "dpi": 72,
            "color_mode": str(psd.color_mode) if hasattr(psd, "color_mode") else "unknown",
        }
