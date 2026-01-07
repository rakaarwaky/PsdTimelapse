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


def classify_action(layer: LayerEntity) -> ClassificationResult:
    """
    Classify a layer to determine its animation type.

    Priority:
    1. Manual override via naming convention ([D] or [B] prefix)
    2. Background layer (z_index=0) = instant appear
    3. Size-based heuristic (small=drag, large=brush)

    Args:
        layer: The layer to classify.

    Returns:
        ClassificationResult with action type and reasoning.
    """
    # Priority 1: Manual override
    if layer.action_hint == ActionHint.DRAG:
        return ClassificationResult(
            animation_type=ActionType.DRAG,
            confidence=1.0,
            reason="Manual override: layer name starts with [D]",
        )
    elif layer.action_hint == ActionHint.BRUSH:
        return ClassificationResult(
            animation_type=ActionType.BRUSH,
            confidence=1.0,
            reason="Manual override: layer name starts with [B]",
        )

    # Priority 2: Background layer detection (z_index=0 = bottom layer)
    if layer.z_index == 0:
        return ClassificationResult(
            animation_type=ActionType.NONE,
            confidence=1.0,
            reason="Background layer (z_index=0) - instant visible",
        )

    # Priority 2: Size-based classification
    max_dimension = max(layer.bounds.width, layer.bounds.height)
    min_dimension = min(layer.bounds.width, layer.bounds.height)

    if layer.is_small(SMALL_THRESHOLD):
        return ClassificationResult(
            animation_type=ActionType.DRAG,
            confidence=0.9,
            reason=f"Small layer ({max_dimension:.0f}px < {SMALL_THRESHOLD}px)",
        )
    elif layer.is_large(LARGE_THRESHOLD):
        return ClassificationResult(
            animation_type=ActionType.BRUSH,
            confidence=0.9,
            reason=f"Large layer ({min_dimension:.0f}px > {LARGE_THRESHOLD}px)",
        )
    else:
        # Medium-sized: use aspect ratio or default to drag
        aspect = layer.bounds.width / max(layer.bounds.height, 1)
        if 0.3 < aspect < 3.0:
            # Roughly square or regular proportions
            return ClassificationResult(
                animation_type=ActionType.DRAG,
                confidence=0.6,
                reason=f"Medium layer ({max_dimension:.0f}px), balanced aspect",
            )
        else:
            # Long/thin elements
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
