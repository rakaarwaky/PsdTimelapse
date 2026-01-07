from dataclasses import dataclass, field

from ..value_objects.analysis.layer_analysis_value import LayerAnalysis
from ..value_objects.animation.brush_path_type_value import BrushPathType
from ..value_objects.animation.path_direction_value import PathDirection
from .action_entity import Action


@dataclass
class SmartAction(Action):
    """Extended action with smart planning metadata."""

    path_direction: PathDirection = PathDirection.HORIZONTAL
    analysis: LayerAnalysis | None = None
    brush_path_type: BrushPathType | None = field(default=None)
