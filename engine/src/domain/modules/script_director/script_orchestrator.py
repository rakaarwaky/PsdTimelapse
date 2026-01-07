from __future__ import annotations

from typing import TYPE_CHECKING

from ...value_objects.configs import ScriptDirectorConfig

if TYPE_CHECKING:
    from ...entities.layer_entity import LayerEntity
    from ...entities.timeline_entity import TimelineEntity
    from ...value_objects.animation.sequencing_strategy_value import SequencingStrategy


def create_timeline(
    layers: list[LayerEntity],
    strategy: SequencingStrategy | None = None,
    config: ScriptDirectorConfig | None = None,
) -> TimelineEntity:
    """
    Factory: Generate timeline from layers with specified strategy.

    Args:
        layers: List of LayerEntity objects to animate
        strategy: Sequencing strategy (SEQUENTIAL, PARALLEL, STAGGERED)
        config: Optional configuration overrides

    Returns:
        Populated Timeline with actions

    Example:
        timeline = create_timeline(world.scene.layers, SequencingStrategy.STAGGERED)
    """
    from .analysis.layer_classifier_module import classify_layer
    from .planners.timeline_planner_module import SequencingStrategy as SeqStrat
    from .planners.timeline_planner_module import plan_timeline

    if strategy is None:
        strategy = SeqStrat.STAGGERED  # type: ignore[assignment]

    # ORCHESTRATION: Inject Staff (Classifier) into Planner
    return plan_timeline(layers, classify_layer, strategy)  # type: ignore[arg-type]


def plan_production(
    layers: list[LayerEntity],
    strategy: str = "STAGGERED",
    config: ScriptDirectorConfig | None = None,
) -> TimelineEntity:
    """
    High-level orchestration: Classify layers and generate timeline.

    This is the recommended entry point for the script director module.

    Args:
        layers: Raw layer list from PSD
        strategy: Strategy name as string
        config: Optional configuration

    Returns:
        Complete production timeline
    """
    from .analysis.layer_classifier_module import classify_layer
    from .planners.timeline_planner_module import SequencingStrategy, plan_timeline

    # Get strategy enum
    strat = getattr(SequencingStrategy, strategy.upper(), SequencingStrategy.STAGGERED)

    # Generate timeline with injected dependency
    return plan_timeline(layers, classify_layer, strat)


def create_smart_timeline(
    layers: list[LayerEntity],
    canvas_width: int,
    canvas_height: int,
) -> TimelineEntity:
    """
    Orchestrate smart timeline creation.
    Injects LayerAnalyzer into SmartPlanner.
    """
    from .analysis.layer_analyzer_module import analyze_layer
    from .planners.smart_timeline_planner_module import plan_smart_timeline

    return plan_smart_timeline(
        layers=layers,
        analyze_fn=analyze_layer,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
    )


def generate_script(timeline: TimelineEntity, output_path: str | None = None) -> str:
    """
    Facade: Generate Python script from timeline.

    Delegates to the script generator staff submodule.
    """
    from .generators.script_generator_module import generate_python_script

    return generate_python_script(timeline, output_path)  # type: ignore[unused-ignore]
