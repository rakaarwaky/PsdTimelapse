"""
TimelinePlanner: Schedule and sequence animation actions.
Dependencies: LayerEntity, DirectorProfile (BLIND MODULE - no peer imports)

BLIND LOGIC: This module is "Staff" level. It does NOT import from peer
submodules (analysis/, generators/). All external dependencies are injected
by the Orchestrator (Manager level).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

# Domain Entities (Canonical Models)
from ....entities.action_entity import Action, CameraAction
from ....entities.layer_entity import ActionHint, LayerEntity
from ....entities.timeline_entity import TimelineEntity
from ....value_objects.animation import DirectorProfile
from ....value_objects.animation.action_type_value import ActionType

# Domain Value Objects
from ....value_objects.animation.sequencing_strategy import SequencingStrategy
from ....value_objects.animation.timing_constants import (
    BRUSH_DURATION,
    DRAG_DURATION,
    FADE_DURATION,
    HOLD_DURATION,
    INTRO_DURATION,
    OUTRO_DURATION,
)

# Type alias for classifier function signature
ClassifyFn = Callable[[LayerEntity], Any]

# Re-export for backward compatibility
__all__ = [
    "BRUSH_DURATION",
    "DRAG_DURATION",
    "FADE_DURATION",
    "HOLD_DURATION",
    "INTRO_DURATION",
    "OUTRO_DURATION",
    "Action",
    "CameraAction",
    "SequencingStrategy",
    "TimelineEntity",
    "estimate_duration",
    "plan_timeline",
    "plan_timeline_v2",
]


def plan_timeline(
    layers: list[LayerEntity],
    classify_fn: ClassifyFn,
    strategy: SequencingStrategy = SequencingStrategy.STAGGERED,
) -> TimelineEntity:
    """
    Create an animation timeline for a list of layers.

    Background layers (ActionType.NONE) start at time 0.
    Other layers start after intro with their animations.
    """
    timeline = TimelineEntity()
    current_time = INTRO_DURATION
    last_action_type = None

    for layer in layers:
        classification = classify_fn(layer)
        action_type = classification.animation_type
        has_hint = layer.action_hint != ActionHint.NONE

        # Background layers
        if action_type == ActionType.NONE:
            timeline.add_action(
                Action(
                    layer_id=layer.id,
                    action_type=ActionType.NONE,
                    start_time=0.0,
                    duration=0.0,
                    target_position=layer.center,
                )
            )
            continue

        # Alternation Strategy (no explicit hint)
        if (
            not has_hint
            and last_action_type == ActionType.BRUSH
            and action_type == ActionType.BRUSH
        ):
            action_type = ActionType.DRAG

        last_action_type = action_type
        duration = _get_duration_for_action(action_type)
        start_time = _calculate_start_time(strategy, current_time, INTRO_DURATION)

        if strategy != SequencingStrategy.PARALLEL:
            current_time += duration + HOLD_DURATION

        timeline.add_action(
            Action(
                layer_id=layer.id,
                action_type=action_type,
                start_time=start_time,
                duration=duration,
                target_position=layer.center,
            )
        )

    return timeline


def plan_timeline_v2(
    layers: list[LayerEntity],
    classify_fn: ClassifyFn,
    profile: DirectorProfile,
    strategy: SequencingStrategy = SequencingStrategy.STAGGERED,
) -> TimelineEntity:
    """Create an animation timeline using DirectorProfile for rhythm control."""
    timeline = TimelineEntity()
    current_time = INTRO_DURATION
    consecutive_same_count = 0
    last_action_type = None

    for layer in layers:
        classification = classify_fn(layer)
        action_type = classification.action_type
        has_hint = layer.action_hint != ActionHint.NONE

        # Background layers
        if action_type == ActionType.NONE:
            timeline.add_action(
                Action(
                    layer_id=layer.id,
                    action_type=ActionType.NONE,
                    start_time=0.0,
                    duration=0.0,
                    target_position=layer.center,
                )
            )
            continue

        # DirectorProfile-based Rhythm Logic
        if not has_hint and last_action_type == action_type:
            consecutive_same_count += 1
            if profile.should_force_variation(consecutive_same_count):
                action_type = (
                    ActionType.DRAG if action_type == ActionType.BRUSH else ActionType.BRUSH
                )
                consecutive_same_count = 0
        else:
            consecutive_same_count = 0 if action_type != last_action_type else 1

        last_action_type = action_type
        duration = max(_get_duration_for_action(action_type), profile.min_layer_duration)
        start_time = _calculate_start_time(strategy, current_time, INTRO_DURATION)

        if strategy != SequencingStrategy.PARALLEL:
            current_time += duration + HOLD_DURATION

        timeline.add_action(
            Action(
                layer_id=layer.id,
                action_type=action_type,
                start_time=start_time,
                duration=duration,
                target_position=layer.center,
            )
        )

    return timeline


def estimate_duration(layer_count: int, strategy: SequencingStrategy) -> float:
    """Estimate total animation duration based on layer count."""
    avg_duration = (DRAG_DURATION + BRUSH_DURATION) / 2

    if strategy == SequencingStrategy.PARALLEL:
        return INTRO_DURATION + avg_duration + OUTRO_DURATION
    else:
        return INTRO_DURATION + layer_count * (avg_duration + HOLD_DURATION) + OUTRO_DURATION


def _get_duration_for_action(action_type: ActionType) -> float:
    """Get animation duration for action type."""
    if action_type == ActionType.DRAG:
        return DRAG_DURATION
    elif action_type == ActionType.BRUSH:
        return BRUSH_DURATION
    return FADE_DURATION


def _calculate_start_time(
    strategy: SequencingStrategy, current_time: float, intro_duration: float
) -> float:
    """Calculate start time based on strategy."""
    if strategy == SequencingStrategy.PARALLEL:
        return intro_duration
    return current_time
