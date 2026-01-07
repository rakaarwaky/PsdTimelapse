from dataclasses import dataclass

from ..value_objects.animation.action_type_value import ActionType
from ..value_objects.animation.easing_curve_value import EasingCurve
from ..value_objects.geometry.vector_value import Vector2


@dataclass
class Action:
    """Base action in the timeline."""

    layer_id: str
    action_type: ActionType
    start_time: float
    duration: float
    target_position: Vector2 | None = None
    easing: EasingCurve | None = None

    @property
    def end_time(self) -> float:
        return self.start_time + self.duration


@dataclass
class CameraAction:
    """Camera movement action."""

    start_time: float
    duration: float
    start_position: Vector2
    end_position: Vector2
    start_zoom: float
    end_zoom: float

    @property
    def end_time(self) -> float:
        return self.start_time + self.duration
