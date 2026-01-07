from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from PIL import Image

from ....entities.layer_entity import LayerEntity
from ....value_objects.animation import RenderState
from ..services.layer_service import LayerRetrievalService
from .blur_module import apply_motion_blur
from .composite_module import safe_paste
from .opacity_module import apply_opacity
from .subpixel_module import apply_subpixel_shift

# ============================================================
# Protocols (Blind Logic)
# ============================================================


class RevealMaskFn(Protocol):
    def __call__(self, img: Image.Image, progress: float) -> Image.Image: ...


class BrushCursorPosFn(Protocol):
    def __call__(self, w: float, h: float, progress: float) -> tuple[float, float, float]: ...


class DrawCursorUIFn(Protocol):
    def __call__(self, target: Image.Image, x: float, y: float, r: float) -> None: ...


# noqa: PLR0913


def compose_from_render_states(  # noqa: PLR0913
    states: list[RenderState],
    find_layer_func: Callable[[str], LayerEntity | None],
    layer_service: LayerRetrievalService,
    width: int,
    height: int,
    document: Any | None = None,
    # Injected Dependencies
    apply_reveal_mask_fn: RevealMaskFn | None = None,
    get_brush_cursor_pos_fn: BrushCursorPosFn | None = None,
    draw_brush_cursor_ui_fn: DrawCursorUIFn | None = None,
) -> Image.Image:
    """
    Type-safe compositing using RenderState value objects.
    """
    # Create Canvas
    if document:
        psd = document.create_image()
    else:
        psd = Image.new("RGBA", (width, height), (255, 255, 255, 255))

    # Filter and sort by z_index
    visible_states = [s for s in states if s.visible and s.opacity > 0]  # type: ignore[operator]
    visible_states.sort(key=lambda s: s.z_index)

    # Track brush cursors to draw AFTER all layers
    brush_cursors = []

    for state in visible_states:
        layer = find_layer_func(state.layer_id)
        if not layer:
            continue

        img = layer_service.get_layer_image(layer)
        if not img:
            continue

        # Position Calculation (Sub-pixel)
        raw_x = state.position.x - layer.bounds.width / 2
        raw_y = state.position.y - layer.bounds.height / 2

        # Integer paste position
        pos_x = int(raw_x)
        pos_y = int(raw_y)

        # Apply opacity
        img = apply_opacity(img, state.opacity)  # type: ignore[arg-type]

        # Reveal mask (Brush actions)
        if hasattr(state, "reveal_progress") and state.reveal_progress < 1.0:
            if apply_reveal_mask_fn:
                img = apply_reveal_mask_fn(img, state.reveal_progress)
                # Only show cursor when action is ACTIVELY running (0 < progress < 1)
                if state.reveal_progress > 0.0 and get_brush_cursor_pos_fn:
                    local_x, local_y, radius = get_brush_cursor_pos_fn(
                        layer.bounds.width, layer.bounds.height, state.reveal_progress
                    )
                    brush_cursors.append((pos_x + local_x, pos_y + local_y, radius))

        # Blur
        if hasattr(state, "velocity"):
            img, blur_offset = apply_motion_blur(img, state.velocity)
            # Accumulate offset from blur (padding)
            pos_x += blur_offset[0]
            pos_y += blur_offset[1]

        # Sub-pixel Shift
        shift_x = raw_x - int(raw_x)  # Re-calculate fraction from ORIGINAL pos.
        shift_y = raw_y - int(raw_y)

        img, sp_offset = apply_subpixel_shift(img, shift_x, shift_y)
        pos_x += sp_offset[0]
        pos_y += sp_offset[1]

        # Composite
        safe_paste(psd, img, (pos_x, pos_y))

    # Draw brush cursors ON TOP of everything (complete circles)
    if draw_brush_cursor_ui_fn:
        for cursor_x, cursor_y, radius in brush_cursors:
            draw_brush_cursor_ui_fn(psd, cursor_x, cursor_y, radius)

    return psd  # type: ignore[no-any-return]
