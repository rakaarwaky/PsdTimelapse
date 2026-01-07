"""
RenderState Value Object: Snapshot of layer's visual state at a frame.
Part of animation category - frame render state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..geometry.vector_value import Vector2
from ..visual.opacity_value import Opacity


@dataclass(frozen=True)
class RenderState:
    """Immutable snapshot of a layer's transform and visual state."""

    layer_id: str
    position: Vector2
    opacity: Opacity = field(default_factory=lambda: Opacity.OPAQUE)
    scale: Vector2 = field(default_factory=lambda: Vector2(1.0, 1.0))
    rotation: float = 0.0
    visible: bool = True
    z_index: int = 0


@dataclass(frozen=True)
class RenderFrame:
    """
    Immutable rendered frame data.
    Acts as a DTO between Animator and Pipeline.
    """

    frame_number: int
    layer_id: str
    image: Any  # PIL.Image
    frame_type: str  # "blank", "active", "hold"
    state: Any = None  # Generic metadata / LayerAnimState
