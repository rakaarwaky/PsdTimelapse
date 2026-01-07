"""
SmartTimelinePlannerModule: Intelligent timeline planning with alternating animations.
Dependencies: LayerEntity, Timeline, LayerAnalysis (BLIND MODULE - no peer imports)

BLIND LOGIC: This module is "Staff" level. It does NOT import from peer
submodules (analysis/, generators/). All external dependencies are injected
by the Orchestrator (Manager level).
"""

from __future__ import annotations

from collections.abc import Callable

from ....entities.layer_entity import LayerEntity
from ....entities.smart_action_entity import SmartAction
from ....entities.timeline_entity import TimelineEntity
from ....entities.world_entity import WorldEntity
from ....value_objects.analysis.layer_analysis_value import LayerAnalysis
from ....value_objects.animation.action_type_value import ActionType
from ....value_objects.animation.brush_path_type_value import BrushPathType
from ....value_objects.animation.path_direction_value import PathDirection
from ....value_objects.visual.orientation_value import Orientation

# Type alias for analyzer function signature
AnalyzeFn = Callable[[LayerEntity, int, int], LayerAnalysis]


def sort_layers_by_z_index(layers: list[LayerEntity]) -> list[LayerEntity]:
    """Sort layers by z_index ascending (bottom layer first)."""
    return sorted(layers, key=lambda layer: layer.z_index)


def get_alternating_action_type(index: int) -> ActionType:
    """
    Get animation type based on index for alternating pattern.

    Pattern: DRAG, BRUSH, DRAG, BRUSH, ...

    Args:
        index: Layer index (0-based).

    Returns:
        ActionType.DRAG or ActionType.BRUSH
    """
    if index % 2 == 0:
        return ActionType.DRAG
    else:
        return ActionType.BRUSH


def get_path_direction(orientation: Orientation, action_type: ActionType) -> PathDirection:
    """
    Determine path direction based on layer orientation and animation type.

    Rules:
    - DRAG on Horizontal layer → Vertical path
    - DRAG on Vertical layer → Horizontal path
    - BRUSH on Horizontal layer → Horizontal path
    - BRUSH on Vertical layer → Vertical path

    Args:
        orientation: Layer orientation.
        action_type: Animation type.

    Returns:
        PathDirection for the animation.
    """
    is_horizontal = orientation in (Orientation.HORIZONTAL, Orientation.SQUARE)

    if action_type == ActionType.DRAG:
        # Drag moves opposite to orientation
        return PathDirection.VERTICAL if is_horizontal else PathDirection.HORIZONTAL
    else:
        # Brush reveals along orientation
        return PathDirection.HORIZONTAL if is_horizontal else PathDirection.VERTICAL


def plan_smart_timeline(  # noqa: PLR0913, PLR0912
    layers: list[LayerEntity],
    analyze_fn: AnalyzeFn,
    canvas_width: int,
    canvas_height: int,
    gap_seconds: float = 0.5,
    exclude_bottom_layer: bool = True,
) -> TimelineEntity:
    """
    Create smart timeline with alternating animations.

    Args:
        layers: List of LayerEntity objects.
        canvas_width: Canvas width for duration calculation.
        canvas_height: Canvas height for duration calculation.
        gap_seconds: Gap between layer animations.
        exclude_bottom_layer: If True, do not animate the bottom-most layer.

    Returns:
        TimelineEntity with intelligently planned actions.
    """
    timeline = TimelineEntity()

    # Sort by z_index (bottom first)
    sorted_layers = sort_layers_by_z_index(layers)

    # Filter out groups (animate only leaf layers or treat groups as units)
    animatable_layers = [layer for layer in sorted_layers if not layer.is_group]

    # Exclude bottom layer (Task 4)
    if exclude_bottom_layer and animatable_layers:
        # The first layer in sorted list is the bottom one
        # We assume this is the background/product base
        print(f"Skipping animation for bottom layer: {animatable_layers[0].id}")
        animatable_layers = animatable_layers[1:]

    current_time = 0.0

    for idx, layer in enumerate(animatable_layers):
        # Skip invisible layers
        if not layer.visible:
            continue

        # Analyze layer
        analysis = analyze_fn(layer, canvas_width, canvas_height)

        # Get alternating animation type
        action_type = get_alternating_action_type(idx)

        # Determine path direction
        path_direction = get_path_direction(analysis.orientation, action_type)

        # Calculate target position (center of layer)
        target_pos = layer.position

        if action_type == ActionType.BRUSH:
            # Randomly select a brush path type (Task 13 + User Request)
            import random

            brush_type = random.choice(list(BrushPathType))
        else:
            brush_type = BrushPathType.STRAIGHT

        # Create action
        action = SmartAction(
            layer_id=layer.id,
            action_type=action_type,
            start_time=current_time,
            duration=analysis.duration,
            target_position=target_pos,
            path_direction=path_direction,
            analysis=analysis,
            brush_path_type=brush_type,
        )

        timeline.add_action(action)

        # Move to next layer's start time
        current_time += analysis.duration + gap_seconds

    return timeline


def plan_smart_timeline_from_world(
    world: WorldEntity, analyze_fn: AnalyzeFn, gap_seconds: float = 0.5
) -> TimelineEntity:
    """
    Convenience function to plan timeline from WorldEntity.

    Args:
        world: WorldEntity containing scene and layers.
        gap_seconds: Gap between layer animations.

    Returns:
        Timeline with intelligently planned actions.
    """
    all_layers = list(world.scene.iterate_all())
    return plan_smart_timeline(
        layers=all_layers,
        analyze_fn=analyze_fn,
        canvas_width=world.width,
        canvas_height=world.height,
        gap_seconds=gap_seconds,
        exclude_bottom_layer=True,
    )
