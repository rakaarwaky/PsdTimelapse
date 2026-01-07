from ....value_objects.animation.layer_anim_state import LayerAnimState
from ....value_objects.geometry import Vector2

# NOTE: Path generation removed - injected via state.path by Orchestrator (Blind Logic)


def animate_drag(
    state: LayerAnimState,
    target_pos: Vector2,
    eased_progress: float,
    raw_progress: float,
    viewport_width: int,
    viewport_height: int,
    direction: str = "auto",
) -> None:
    """
    Execute Drag Animation Strategy.

    REQUIRES: state.path must be pre-injected by Orchestrator.
    This function is "Blind" - it only processes, doesn't generate paths.
    """
    # 1. Validate path is injected (Blind Logic)
    if not state.path:
        raise ValueError("state.path must be set by Orchestrator before calling animate_drag")

    # Snap to start position on first frame
    if eased_progress == 0.0 and len(state.path.points) > 0:
        state.position = state.path.points[0]

    # 2. Position & Velocity
    if state.path:
        path_len = len(state.path.points)
        if path_len > 1:
            # Float index
            f_idx = eased_progress * (path_len - 1)

            # Base index and next index
            idx = int(f_idx)
            idx = max(0, min(idx, path_len - 1))

            next_idx = min(idx + 1, path_len - 1)

            # Fraction for interpolation
            t = f_idx - idx

            prev_pos = state.position  # Previous frame position

            # Lerp Position
            p1 = state.path.points[idx]
            p2 = state.path.points[next_idx]
            new_pos = p1.lerp(p2, t)

            # Calculate velocity before updating position
            # Note: Velocity might be very small, but continuous now.
            state.velocity = Vector2(new_pos.x - prev_pos.x, new_pos.y - prev_pos.y)
            state.position = new_pos

    # 3. Opacity (Removed fade-in as per user request)
    # state.opacity = min(1.0, raw_progress * 3)
