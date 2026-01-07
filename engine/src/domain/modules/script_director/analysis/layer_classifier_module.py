"""
LayerClassifierModule: Intelligent layer classification for animation selection.
Dependencies: LayerEntity, VideoConstants
"""

from __future__ import annotations

from ....entities.layer_entity import LayerEntity
from ....value_objects.analysis.classification_result_value import ClassificationResult
from ....value_objects.animation.action_type_value import ActionType
from ....value_objects.visual.video_constants_value import VIDEO_HEIGHT, VIDEO_WIDTH

# Alias for backward compatibility if needed, though strictly we should update usage.
AnimationType = ActionType

# Classification thresholds
BACKGROUND_COVERAGE_THRESHOLD = 0.8
HORIZONTAL_ASPECT_RATIO_THRESHOLD = 3.0
VERTICAL_ASPECT_RATIO_THRESHOLD = 0.33


def classify_layer(layer: LayerEntity) -> ClassificationResult:
    """
    Intelligent layer classification based on image heuristics.

    Rules:
    1. BACKGROUND: z_index == 0 AND covers >80% canvas → No animation
    2. TEXTURE: aspect ratio elongated (>3:1 or <1:3) → Brush reveal
    3. LOGO/ELEMENT: centered, square-ish → Drag from direction

    Args:
        layer: LayerEntity to classify

    Returns:
        ClassificationResult with animation type and reason
    """
    # Check manual override from layer name
    if layer.action_hint.value == "[D]":
        return ClassificationResult(ActionType.DRAG, "Manual [D] override", "top")
    if layer.action_hint.value == "[B]":
        return ClassificationResult(ActionType.BRUSH, "Manual [B] override")

    # Rule 1: Background detection (bottom layer + large coverage)
    canvas_area = VIDEO_WIDTH * VIDEO_HEIGHT
    layer_coverage = layer.area / canvas_area if canvas_area > 0 else 0

    if layer.z_index == 0 and layer_coverage > BACKGROUND_COVERAGE_THRESHOLD:
        return ClassificationResult(ActionType.NONE, "Background layer (z=0, >80% coverage)")

    # Rule 2: Texture detection (elongated aspect ratio)
    if layer.bounds.width > 0 and layer.bounds.height > 0:
        aspect_ratio = layer.bounds.width / layer.bounds.height

        if aspect_ratio > HORIZONTAL_ASPECT_RATIO_THRESHOLD:
            return ClassificationResult(
                ActionType.BRUSH, f"Horizontal texture (aspect {aspect_ratio:.1f}:1)"
            )
        if aspect_ratio < VERTICAL_ASPECT_RATIO_THRESHOLD:
            return ClassificationResult(
                ActionType.BRUSH, f"Vertical texture (aspect 1:{1 / aspect_ratio:.1f})"
            )

    # Rule 3: Default to drag animation with direction based on position
    direction = _determine_drag_direction(layer)
    return ClassificationResult(ActionType.DRAG, "Standard element", direction)


def _determine_drag_direction(layer: LayerEntity) -> str:
    """
    Determine drag direction based on layer position in canvas.

    - Top half → drag from top
    - Bottom half → drag from bottom
    - Far left → drag from left
    - Far right → drag from right
    """
    center = layer.center
    canvas_center_x = VIDEO_WIDTH / 2
    canvas_center_y = VIDEO_HEIGHT / 2

    # Calculate distance from center
    dx = center.x - canvas_center_x
    dy = center.y - canvas_center_y

    # Determine primary direction (prefer vertical for vertical video)
    if abs(dy) > abs(dx):
        return "top" if dy < 0 else "bottom"
    else:
        return "left" if dx < 0 else "right"


def classify_all_layers(layers: list[LayerEntity]) -> dict[str, ClassificationResult]:
    """
    Classify all layers in a scene.

    Args:
        layers: List of LayerEntity objects

    Returns:
        Dict mapping layer_id to ClassificationResult
    """
    return {layer.id: classify_layer(layer) for layer in layers}
