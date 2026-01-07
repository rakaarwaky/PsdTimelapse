from dataclasses import dataclass

from ..animation.action_type_value import ActionType


@dataclass
class ClassificationResult:
    """Result of layer classification."""

    animation_type: ActionType
    reason: str
    drag_direction: str | None = None  # "top", "bottom", "left", "right"
    confidence: float = 1.0  # Added primarily for compatibility with legacy usage
