"""
LayerEntity: Represents a single layer in the design.
Dependencies: Vector2, Rect, Color
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..value_objects.geometry import Rect, Vector2
from ..value_objects.visual import BlendMode, Opacity

if False:
    # Type checking only to avoid circular imports
    from .asset_entity import AssetEntity

__all__ = ["ActionHint", "BlendMode", "LayerEntity", "Opacity"]


class ActionHint(Enum):
    """Manual action type override via layer naming convention."""

    NONE = ""
    DRAG = "[D]"  # Force drag animation
    BRUSH = "[B]"  # Force brush reveal animation


@dataclass
class LayerEntity:
    """Domain entity representing a design layer (sprite/actor)."""

    id: str
    name: str
    z_index: int = 0  # Stacking order from PSD (0 = bottom)
    position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    bounds: Rect = field(default_factory=lambda: Rect(0, 0, 0, 0))
    opacity: Opacity = field(default_factory=lambda: Opacity.OPAQUE)
    visible: bool = True
    blend_mode: BlendMode = field(default_factory=lambda: BlendMode.NORMAL)
    parent_id: str | None = None
    is_group: bool = False
    image_data: Any | None = None  # PIL Image or raw bytes
    asset: AssetEntity | None = None  # Linked source asset

    @property
    def size(self) -> tuple[float, float]:
        """Get layer width and height."""
        return (self.bounds.width, self.bounds.height)

    @property
    def center(self) -> Vector2:
        """Get the center point of this layer."""
        return self.bounds.center()

    @property
    def action_hint(self) -> ActionHint:
        """Extract action hint from layer name prefix."""
        if self.name.startswith("[D]"):
            return ActionHint.DRAG
        elif self.name.startswith("[B]"):
            return ActionHint.BRUSH
        return ActionHint.NONE

    @property
    def clean_name(self) -> str:
        """Get name without action hint prefix."""
        for hint in ActionHint:
            if hint.value and self.name.startswith(hint.value):
                return self.name[len(hint.value) :].strip()
        return self.name

    @property
    def area(self) -> float:
        """Get the area of this layer in pixels."""
        return self.bounds.area()

    def is_small(self, threshold: int = 100) -> bool:
        """Check if layer is considered 'small' (< threshold px)."""
        return max(self.bounds.width, self.bounds.height) < threshold

    def is_large(self, threshold: int = 500) -> bool:
        """Check if layer is considered 'large' (> threshold px)."""
        return min(self.bounds.width, self.bounds.height) > threshold

    def __repr__(self) -> str:
        visible_str = "✓" if self.visible else "✗"
        return f"Layer[{visible_str}]({self.name}, {self.bounds})"
