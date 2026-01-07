"""
Layer Animation State: Runtime mutable state for animation playback.
"""

import typing
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..animation import BrushPathType
from ..geometry import Rect, Vector2, rect

if TYPE_CHECKING:
    # Forward ref to avoid circular import if path generator needs this
    # Typically this VO shouldn't depend on heavy modules
    pass


@dataclass
class LayerAnimState:
    """
    Mutable runtime state for a single layer's animation.
    Used by AnimationController during playback.
    """

    visible: bool = True
    path: typing.Any = None  # Typed as Any to avoid circular dependency with AnimationPath
    velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    opacity: float = 1.0
    reveal_progress: float = 1.0
    brush_size: float = 0.0
    position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    reveal_direction: str = "horizontal"
    bounds: Rect = field(default_factory=lambda: rect(0, 0, 0, 0))
    brush_position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    brush_path_type: BrushPathType = BrushPathType.STRAIGHT
