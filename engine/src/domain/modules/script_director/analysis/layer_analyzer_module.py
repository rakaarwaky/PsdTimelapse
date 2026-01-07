"""
LayerAnalyzerModule: Analyze layer properties for smart animation assignment.
Dependencies: LayerEntity, WorldEntity
"""

from __future__ import annotations

from ....entities.layer_entity import LayerEntity
from ....value_objects.analysis.layer_analysis_value import LayerAnalysis
from ....value_objects.visual.orientation_value import Orientation

# Duration constants
MIN_DURATION = 2.0
MAX_DURATION = 6.0


def get_orientation(layer: LayerEntity) -> Orientation:
    """
    Determine layer orientation from bounding box.

    Args:
        layer: LayerEntity to analyze.

    Returns:
        Orientation enum value.
    """
    width = layer.bounds.width
    height = layer.bounds.height

    if width > height:
        return Orientation.HORIZONTAL
    elif height > width:
        return Orientation.VERTICAL
    else:
        return Orientation.SQUARE  # Treated as HORIZONTAL for animation


def calculate_duration(layer: LayerEntity, canvas_width: int, canvas_height: int) -> float:
    """
    Calculate adaptive animation duration based on layer size.

    Formula: duration = MIN + (ratio * (MAX - MIN))
    Range: 2-6 seconds

    Args:
        layer: LayerEntity to calculate duration for.
        canvas_width: Total canvas width.
        canvas_height: Total canvas height.

    Returns:
        Duration in seconds (2.0 - 6.0).
    """
    layer_area = layer.bounds.width * layer.bounds.height
    canvas_area = canvas_width * canvas_height

    if canvas_area == 0:
        return MIN_DURATION

    ratio = min(1.0, layer_area / canvas_area)  # Clamp to 1.0 max
    duration = MIN_DURATION + (ratio * (MAX_DURATION - MIN_DURATION))

    return round(duration, 2)


def analyze_layer(layer: LayerEntity, canvas_width: int, canvas_height: int) -> LayerAnalysis:
    """
    Perform full analysis on a single layer.

    Args:
        layer: LayerEntity to analyze.
        canvas_width: Total canvas width.
        canvas_height: Total canvas height.

    Returns:
        LayerAnalysis with orientation, duration, and area ratio.
    """
    layer_area = layer.bounds.width * layer.bounds.height
    canvas_area = canvas_width * canvas_height
    area_ratio = layer_area / canvas_area if canvas_area > 0 else 0.0

    return LayerAnalysis(
        layer_id=layer.id,
        orientation=get_orientation(layer),
        duration=calculate_duration(layer, canvas_width, canvas_height),
        area_ratio=round(area_ratio, 4),
    )


def analyze_layers(
    layers: list[LayerEntity], canvas_width: int, canvas_height: int
) -> list[LayerAnalysis]:
    """
    Analyze all layers for animation planning.

    Args:
        layers: List of LayerEntity objects.
        canvas_width: Total canvas width.
        canvas_height: Total canvas height.

    Returns:
        List of LayerAnalysis objects.
    """
    return [analyze_layer(layer, canvas_width, canvas_height) for layer in layers]
