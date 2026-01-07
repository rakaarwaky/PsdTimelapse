"""
WorldEntity: The infinite canvas where the design lives.
Dependencies: SceneEntity, Rect, DocumentEntity
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..value_objects.geometry import Rect
from .document_entity import DocumentEntity
from .scene_entity import SceneEntity
from .timeline_entity import TimelineEntity


@dataclass
class WorldEntity:
    """Domain entity representing the design canvas (the 'truth')."""

    width: int
    height: int
    dpi: int = 72
    name: str = "Untitled"
    scene: SceneEntity = field(default_factory=SceneEntity)
    timeline: TimelineEntity = field(default_factory=TimelineEntity)
    document: DocumentEntity | None = field(default=None)

    @property
    def bounds(self) -> Rect:
        """Get the world boundary as a Rect."""
        return Rect(0, 0, float(self.width), float(self.height))

    @property
    def center(self):
        """Get the center point of the world."""
        return self.bounds.center()

    @property
    def aspect_ratio(self) -> float:
        """Get width/height ratio."""
        if self.height == 0:
            return 0.0
        return self.width / self.height

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is within world bounds."""
        from ..value_objects.geometry import Vector2

        return self.bounds.contains_point(Vector2(x, y))

    def __repr__(self) -> str:
        return f"World('{self.name}', {self.width}x{self.height} @{self.dpi}dpi)"
