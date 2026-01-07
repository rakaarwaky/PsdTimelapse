import math

# NOTE: generate_brush_path removed - path generation handled by Orchestrator (Blind Logic)
from ....value_objects.animation import BrushPathType, BrushTool
from ....value_objects.animation.layer_anim_state import LayerAnimState
from ....value_objects.geometry import Vector2


def get_brush_position_on_path(
    layer_width: float,
    layer_height: float,
    progress: float,
    path_type: BrushPathType = BrushPathType.STRAIGHT,
    brush_radius: float = None,
) -> Vector2:
    """
    Calculate brush position based on path type.
    Migrated from compositor/reveal_op.py.
    """
    if brush_radius is None:
        brush_radius = max(layer_height / 3, 40)

    total_travel = layer_width + (2 * brush_radius)
    x = -brush_radius + (progress * total_travel)

    if path_type == BrushPathType.STRAIGHT:
        y = layer_height / 2

    elif path_type == BrushPathType.CURVE_DOWN:
        # Arc curving downward (sine wave half cycle)
        amplitude = layer_height * 0.35
        y = layer_height / 2 + amplitude * math.sin(progress * math.pi)

    elif path_type == BrushPathType.CURVE_UP:
        # Arc curving upward
        amplitude = layer_height * 0.35
        y = layer_height / 2 - amplitude * math.sin(progress * math.pi)

    elif path_type == BrushPathType.ZIGZAG:
        # Zigzag pattern (3 peaks)
        peaks = 3
        zigzag_t = (progress * peaks) % 1.0
        amplitude = layer_height * 0.35
        # Triangle wave
        if zigzag_t < 0.5:
            wave = 4 * zigzag_t - 1  # -1 to 1
        else:
            wave = 3 - 4 * zigzag_t  # 1 to -1
        y = layer_height / 2 + amplitude * wave
    else:
        y = layer_height / 2

    return Vector2(x, y)


def animate_brush(
    state: LayerAnimState, progress: float, brush_tool: BrushTool | None = None
) -> None:
    """
    Execute Brush Animation Strategy.
    Target Size: < 30 lines.
    """
    state.reveal_progress = progress
    state.opacity = 1.0
    state.velocity = Vector2(0, 0)

    # Calculate brush position based on type (Task 12)
    # Use bounds dimensions
    w = state.bounds.width
    h = state.bounds.height

    # Initialize brush size if not set (Fix for Wipe Fallback)
    # Initialize brush size from BrushTool if provided, else Default
    if brush_tool:
        state.brush_size = brush_tool.size_px
        # We could also apply soft/hardness to opacity or mask logic here if we had that state
    elif state.brush_size <= 0:
        # Default logic
        radius = max(h / 3, 40)
        state.brush_size = radius * 2

    # Calculate relative position (center based? No, function assumes 0,0 top-left of layer rect)
    rel_pos = get_brush_position_on_path(
        w, h, progress, state.brush_path_type, state.brush_size / 2
    )

    # Transform to absolute canvas coordinates
    # Layer bounds.x/y is top-left
    state.brush_position = Vector2(state.bounds.x + rel_pos.x, state.bounds.y + rel_pos.y)
