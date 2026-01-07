from dataclasses import dataclass

from ..visual.orientation_value import Orientation


@dataclass
class LayerAnalysis:
    """Analysis result for a single layer."""

    layer_id: str
    orientation: Orientation
    duration: float  # Calculated animation duration (2-6s)
    area_ratio: float  # layer_area / canvas_area
