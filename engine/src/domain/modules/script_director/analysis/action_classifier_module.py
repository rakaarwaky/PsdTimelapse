"""
ActionClassifier: Determine animation type for layers.
Dependencies: LayerEntity, LayerClassification
"""

from __future__ import annotations

from ....entities.layer_entity import ActionHint, LayerEntity
from ....value_objects.analysis.classification_result_value import ClassificationResult
from ....value_objects.animation.action_type_value import ActionType
from ....value_objects.animation.layer_classification_value import (
    LayerClassification,
    RecommendedAction,
)

# Threshold constants (per 03_FEATURES.md specification)
SMALL_THRESHOLD = 100  # Pixels - below this = DRAG
LARGE_THRESHOLD = 500  # Pixels - above this = BRUSH


# Auto-extracted constants
MAGIC_0_3 = 0.3
TRIPLE_FACTOR = 3.0


def classify_action(layer: LayerEntity) -> ClassificationResult:
    """
    Classify a layer to determine its animation type.
    """
    # Priority 1: Manual override
    if override := _check_manual_override(layer):
        return override

    # Priority 2: Background layer
    if layer.z_index == 0:
        return ClassificationResult(
            animation_type=ActionType.NONE,
            confidence=1.0,
            reason="Background layer (z_index=0) - instant visible",
        )

    # Priority 3: Size-based classification
    return _classify_by_size(layer)


def _check_manual_override(layer: LayerEntity) -> ClassificationResult | None:
    if layer.action_hint == ActionHint.DRAG:
        return ClassificationResult(
            animation_type=ActionType.DRAG,
            confidence=1.0,
            reason="Manual override: layer name starts with [D]",
        )
    if layer.action_hint == ActionHint.BRUSH:
        return ClassificationResult(
            animation_type=ActionType.BRUSH,
            confidence=1.0,
            reason="Manual override: layer name starts with [B]",
        )
    return None


def _classify_by_size(layer: LayerEntity) -> ClassificationResult:
    max_dimension = max(layer.bounds.width, layer.bounds.height)
    min_dimension = min(layer.bounds.width, layer.bounds.height)

    if layer.is_small(SMALL_THRESHOLD):
        return ClassificationResult(
            animation_type=ActionType.DRAG,
            confidence=0.9,
            reason=f"Small layer ({max_dimension:.0f}px < {SMALL_THRESHOLD}px)",
        )

    if layer.is_large(LARGE_THRESHOLD):
        return ClassificationResult(
            animation_type=ActionType.BRUSH,
            confidence=0.9,
            reason=f"Large layer ({min_dimension:.0f}px > {LARGE_THRESHOLD}px)",
        )

    return _classify_medium_layer(layer, max_dimension)


def _classify_medium_layer(layer: LayerEntity, max_dimension: float) -> ClassificationResult:
    aspect = layer.bounds.width / max(layer.bounds.height, 1)
    if MAGIC_0_3 < aspect < TRIPLE_FACTOR:
        return ClassificationResult(
            animation_type=ActionType.DRAG,
            confidence=0.6,
            reason=f"Medium layer ({max_dimension:.0f}px), balanced aspect",
        )

    return ClassificationResult(
        animation_type=ActionType.BRUSH,
        confidence=0.7,
        reason=f"Medium layer with extreme aspect ratio ({aspect:.1f})",
    )


def classify_layer_v2(layer: LayerEntity) -> LayerClassification:
    """
    Classify a layer using the new LayerClassification value object.

    Args:
        layer: The layer to classify.

    Returns:
        LayerClassification with recommended action and reasoning.
    """
    result = classify_action(layer)

    # Map ActionType to RecommendedAction
    action_map = {
        ActionType.DRAG: RecommendedAction.DRAG,
        ActionType.BRUSH: RecommendedAction.BRUSH,
        ActionType.FADE: RecommendedAction.FADE,
        ActionType.NONE: RecommendedAction.STATIC,
    }

    return LayerClassification(
        layer_id=layer.id,
        suggested_action=action_map.get(result.animation_type, RecommendedAction.NONE),
        confidence_score=result.confidence,
        reasoning=result.reason,
        tags=[],  # Could add tags like ["hero", "background"] later
    )


def classify_all_layers(layers: list[LayerEntity]) -> dict[str, ClassificationResult]:
    """
    Classify all layers in a list.

    Returns:
        Dict mapping layer ID to ClassificationResult.
    """
    return {layer.id: classify_action(layer) for layer in layers}
