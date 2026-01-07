"""
PSD Composition Module (Ops - Level 1 Staff)

This module is BLIND to:
- Infrastructure Adapters
- Port Interfaces
- Peer Modules (animator, etc.)

All dependencies are injected as arguments by the Orchestrator.
"""

from collections.abc import Callable
from typing import Any, Protocol

from PIL import Image

from ....entities.layer_entity import LayerEntity
from ....value_objects.geometry import Vector2
from ..services.layer_service import LayerRetrievalService
from .blur_module import apply_motion_blur
from .composite_module import safe_paste
from .opacity_module import apply_opacity
from .subpixel_module import apply_subpixel_shift

# ============================================================
# Protocol Definitions (Structural Typing for "Blindness")
# ============================================================


class MaskGeneratorProtocol(Protocol):
    """What the mask generator looks like to this module."""

    def __call__(
        self,
        layer_size: tuple[Any, ...],
        path: Any,
        progress: float,
        brush_size: int,
        blur_radius: int,
        layer_origin: Any,
        image_processor: Any,
    ) -> Image.Image: ...


class PathGeneratorProtocol(Protocol):
    """What the path generator looks like to this module."""

    def __call__(self, bounds: Any, duration: float, brush_size: int) -> Any: ...


class BrushToolFactoryProtocol(Protocol):
    """What the brush tool factory looks like to this module."""

    def __call__(self, bounds: Any) -> Any: ...


class ImageProcessorProtocol(Protocol):
    """What the image processor looks like to this module."""

    def apply_mask(self, image: Image.Image, mask: Image.Image) -> Image.Image: ...


# ============================================================
# Backward compatibility stubs
# ============================================================
def get_brush_cursor_position(*args):
    return 0, 0, 0


def draw_brush_cursor_ui(*args) -> None:
    pass


# ============================================================
# Main Composition Function (Blind to Dependencies)
# ============================================================


def compose_psd_content(
    layer_states: dict[str, Any],
    find_layer_func: Callable[[str], LayerEntity | None],
    layer_service: LayerRetrievalService,
    width: int,
    height: int,
    document: Any | None = None,
    # Injected Dependencies (Blind - we don't know what these ARE, just what they DO)
    image_processor: ImageProcessorProtocol | None = None,
    mask_generator_fn: MaskGeneratorProtocol | None = None,
    path_generator_fn: PathGeneratorProtocol | None = None,
    brush_tool_factory_fn: BrushToolFactoryProtocol | None = None,
) -> Image.Image:
    """
    Compose content based on PSD layer states.
    """
    # Create Canvas
    if document:
        psd = document.create_image()
    else:
        psd = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Sort Layers (Z-Index)
    queue = []
    for lid, state in layer_states.items():
        if not state.visible or state.opacity <= 0:
            continue
        layer = find_layer_func(lid)
        if layer:
            queue.append((layer, state))

    queue.sort(key=lambda x: x[0].z_index)

    # Track brush cursors to draw AFTER all layers
    brush_cursors = []

    # Compose
    for layer, state in queue:
        img = layer_service.get_layer_image(layer)
        if not img:
            continue

        # Position Calculation (Sub-pixel)
        raw_x = state.position.x - layer.bounds.width / 2
        raw_y = state.position.y - layer.bounds.height / 2

        # Integer paste position
        pos_x = int(raw_x)
        pos_y = int(raw_y)

        # Application order:
        # 1. Opacity
        # 2. Reveal Mask
        # 3. Motion Blur
        # 4. Sub-pixel Shift (Last before paste to preserve anti-aliasing)

        # Opacity
        img = apply_opacity(img, state.opacity)

        # Reveal mask (Brush actions)
        if hasattr(state, "reveal_progress") and state.reveal_progress < 1.0:
            if not all([path_generator_fn, brush_tool_factory_fn, mask_generator_fn]):
                # If we don't have generators, we can't do the complex mask logic.
                # Just skip or fail?
                # Fail safe: simple cut
                pass
            else:
                # Generate Deterministic Path for this layer
                path = path_generator_fn(
                    layer.bounds,
                    duration=1.0,
                    brush_size=state.brush_size if state.brush_size > 0 else 100,
                )

                # Create tool config
                tool = brush_tool_factory_fn(layer.bounds)
                if state.brush_size > 0:
                    tool.size_px = state.brush_size

                # Generate Mask
                if image_processor is None:
                    raise ValueError("image_processor required for mask generation")

                mask = mask_generator_fn(
                    layer_size=img.size,
                    path=path,
                    progress=state.reveal_progress,
                    brush_size=tool.size_px,
                    blur_radius=tool.blur_radius,
                    layer_origin=Vector2(layer.bounds.x, layer.bounds.y),
                    image_processor=image_processor,
                )

                # Apply Mask
                img = image_processor.apply_mask(img, mask)

                # Only show cursor when action is ACTIVELY running (0 < progress < 1)
                if state.reveal_progress > 0.0:
                    # Rough estimation for UI
                    if path.points:
                        idx = int(state.reveal_progress * (len(path.points) - 1))
                        idx = max(0, min(idx, len(path.points) - 1))
                        pt = path.points[idx]

                        # Use cached brush position if available, otherwise fallback to rough calc
                        # (Ideally `state` should have this from the generator phase)
                        if hasattr(state, "brush_position") and state.brush_position:
                            brush_cursors.append(
                                (state.brush_position.x, state.brush_position.y, tool.size_px / 2)
                            )
                        elif pt:
                            pass  # Placeholder if we needed pt

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
    for cursor_x, cursor_y, radius in brush_cursors:
        draw_brush_cursor_ui(psd, cursor_x, cursor_y, radius)

    return psd
