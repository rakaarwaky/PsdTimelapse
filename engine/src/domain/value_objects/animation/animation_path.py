"""
Animation Path Value Object.
"""

from dataclasses import dataclass

from ...geometry import Vector2


@dataclass
class AnimationPath:
    """Describes an animation path for a layer."""

    points: list[Vector2]
    duration: float  # seconds
    start_position: Vector2
    end_position: Vector2
