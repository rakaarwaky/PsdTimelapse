from __future__ import annotations

from typing import TYPE_CHECKING

from ...value_objects.configs import AnimatorConfig

if TYPE_CHECKING:
    from typing import Any

    from domain.value_objects.geometry import Vector2

    from ...value_objects.animation.animation_path import AnimationPath
    from ...value_objects.configs import LayerRenderConfig
    from .core.animator_controller_module import AnimationController
    from .generators.layer_state_generator_module import LayerStateGenerator


def create_animator(
    width: int = 1080,
    height: int = 1920,
    config: AnimatorConfig | None = None,
) -> AnimationController:
    """
    Factory: Create AnimationController with wired strategies.

    This is the Level 2 Manager (Orchestrator) responsibility:
    - Wire "Staff" (submodules) with "Tools" (strategies)
    - Inject dependencies following Blind Logic pattern
    """
    from .core.animator_controller_module import AnimationController
    from .motion.path_generator_module import generate_drag_path
    from .strategies.brush_strategy_module import animate_brush
    from .strategies.drag_strategy_module import animate_drag

    return AnimationController(
        viewport_width=width,
        viewport_height=height,
        animate_drag=animate_drag,
        animate_brush=animate_brush,
        generate_drag_path=generate_drag_path,
    )


def create_animation_path(
    target: Vector2,
    viewport_width: int,
    viewport_height: int,
    path_type: str = "bezier",
    **kwargs,
) -> AnimationPath:
    """
    Factory: Create animation path.
    """
    from ...value_objects.animation.animation_path import AnimationPath
    from .motion.path_generator_module import generate_drag_path

    if path_type == "linear":
        # For linear, start is usually assumed or handled differently,
        # but AnimationPath needs start/end.
        # If this is "create_path_to_target", we assume start
        # is handled elsewhere or needed in kwargs?
        # Let's assume kwargs has start for linear, or we default.
        start = kwargs.get("start_position", Vector2(0, 0))  # Fallback
        return AnimationPath(
            points=[start, target],
            duration=kwargs.get("duration", 1.0),
            start_position=start,
            end_position=target,
        )
    else:
        # Pass viewport dims to generator
        return generate_drag_path(target, viewport_width, viewport_height, **kwargs)


def create_layer_state_generator(config: LayerRenderConfig) -> LayerStateGenerator:
    """
    Factory: Create LayerStateGenerator.
    """
    from .generators.layer_state_generator_module import create_layer_state_generator as _create

    return _create(config)


def get_brush_strategy():
    """Access Brush Strategy functions."""
    from .strategies import brush_strategy_module

    return brush_strategy_module


def get_drag_strategy():
    """Access Drag Strategy functions."""
    from .strategies import drag_strategy_module

    return drag_strategy_module


def generate_reveal_mask(
    layer_size: tuple[int, int], path: AnimationPath, progress: float, brush_size: float, **kwargs
) -> Any:
    """
    Facade: Generate reveal mask.
    NOTE: Requires image_processor (Any) in kwargs for DI.
    """
    from .generators.mask_generator_module import generate_reveal_mask as _generate

    return _generate(layer_size, path, progress, brush_size, **kwargs)
