"""
LayerClassification Value Object: Result of layer animation analysis.
Part of animation category - AI director classification results.
"""

from dataclasses import dataclass, field
from enum import Enum


class RecommendedAction(Enum):
    """Action types recommended by the Director/Classifier."""

    NONE = "none"
    STATIC = "static"
    DRAG = "drag"
    BRUSH = "brush"
    FADE = "fade"
    SCALE = "scale"


@dataclass(frozen=True)
class LayerClassification:
    """Result object containing the classification of a layer."""

    layer_id: str
    suggested_action: RecommendedAction
    confidence_score: float
    reasoning: str
    tags: list[str] = field(default_factory=list)

    def is_confident(self, threshold: float = 0.8) -> bool:
        """Check if classification is confident enough to use automatically."""
        return self.confidence_score >= threshold
