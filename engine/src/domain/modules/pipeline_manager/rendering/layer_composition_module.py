"""
Layer Composition Module - Blind Logic Compliant

Renders layers onto canvas. Uses injected image_processor (PIL-agnostic).
"""

from typing import Any, Protocol

from ....entities.layer_entity import LayerEntity
from ....value_objects.animation.layer_anim_state import LayerAnimState


class ImageProcessorProtocol(Protocol):
    """Protocol for image processing (PIL or compatible)."""

    def new(self, mode: str, size: tuple[int, int], color: tuple[int, ...] | int) -> Any: ...
    def draw(self, image: Any) -> Any: ...
    def composite(self, im1: Any, im2: Any, mask: Any) -> Any: ...


def _get_processor(image_processor: Any = None) -> Any:
    """Get image processor or fallback to PIL."""
    if image_processor is not None:
        return image_processor

    try:
        from PIL import Image as PILImage
        from PIL import ImageDraw as PILImageDraw

        class PILProcessor:
            Image = PILImage
            ImageDraw = PILImageDraw

            def new(self, mode: str, size: tuple[int, int], color: tuple[int, ...] | int) -> Any:
                return PILImage.new(mode, size, color)  # type: ignore

            def draw(self, image: Any) -> Any:
                return PILImageDraw.Draw(image)

            def composite(self, im1: Any, im2: Any, mask: Any) -> Any:
                return PILImage.composite(im1, im2, mask)

        return PILProcessor()
    except ImportError:
        raise RuntimeError("No image_processor provided and PIL not available") from None


def _create_wipe_mask(processor: Any, size: tuple[int, int], state: LayerAnimState) -> Any:
    """Create a wipe transition mask."""
    mask = processor.new("L", size, 0)
    draw = processor.draw(mask)
    w, h = size

    if state.reveal_direction == "vertical":
        h_reveal = int(h * state.reveal_progress)
        draw.rectangle([0, 0, w, h_reveal], fill=255)
    else:
        w_reveal = int(w * state.reveal_progress)
        draw.rectangle([0, 0, w_reveal, h], fill=255)
    return mask


def _create_brush_mask(
    processor: Any,
    size: tuple[int, int],
    state: LayerAnimState,
    cumulative_masks: dict[str, Any],
    layer_id: str,
) -> Any:
    """Create or update a brush-based mask."""
    mask = cumulative_masks.get(layer_id)
    if mask:
        # Draw brush TIP at current confirmed brush_position
        draw = processor.draw(mask)
        radius = state.brush_size / 2
        draw.ellipse(
            [
                state.brush_position.x - radius,
                state.brush_position.y - radius,
                state.brush_position.x + radius,
                state.brush_position.y + radius,
            ],
            fill=255,
        )
    else:
        # Fallback (shouldn't happen if initialized correctly)
        mask = processor.new("L", size, 255)
    return mask


def _apply_mask_to_image(
    processor: Any,
    image: Any,
    state: LayerAnimState,
    mask: Any,
    cumulative_masks: dict[str, Any],
    layer: LayerEntity,
    pos: tuple[int, int],
) -> Any:
    """Apply mask to image alpha channel."""
    x, y = pos

    # Logic for specialized masking (Brush vs Wipe)
    if state.brush_size > 0:
        # Circle Brush Global Mask
        global_mask = cumulative_masks.get(layer.id)
        if global_mask:
            layer_mask = global_mask.crop((x, y, x + image.width, y + image.height))
            layer_alpha = image.split()[3]
            final_alpha = processor.composite(
                layer_alpha, processor.new("L", layer_mask.size, 0), layer_mask
            )
            image.putalpha(final_alpha)
    else:
        # Wipe Logic
        # Note: wipe mask passed in is the general mask, but we might need to recreate it for local application
        # or use composite.
        # The original code recreated the wipe mask locally relative to the image size.
        local_mask = _create_wipe_mask(processor, image.size, state)

        current_alpha = image.split()[3]
        composite_alpha = processor.composite(
            current_alpha, processor.new("L", image.size, 0), local_mask
        )
        image.putalpha(composite_alpha)

    return image


def render_layer_to_image(
    layer_img: Any,
    layer: LayerEntity,
    state: LayerAnimState | None,
    canvas_width: int,
    canvas_height: int,
    cumulative_masks: dict[str, Any],
    image_processor: Any = None,
) -> Any:
    """
    Renders the layer onto a canvas and returns image.

    Refactored to reduce complexity.
    """
    processor = _get_processor(image_processor)
    canvas = processor.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

    if not layer_img:
        return canvas

    is_visible = state.visible if state else True
    if not is_visible:
        return canvas

    # Determine render properties
    pos_x = state.position.x if state else layer.position.x
    pos_y = state.position.y if state else layer.position.y
    opacity = state.opacity if state else layer.opacity.value

    # Process Base Image
    processed_img = layer_img.convert("RGBA")

    # Handle Reveal State (The most complex part)
    if state and state.reveal_progress < 1.0:
        # UPADTE MASKS PHASE
        if state.brush_size > 0:
            _create_brush_mask(processor, processed_img.size, state, cumulative_masks, layer.id)

        # APPLY MASKS PHASE
        # Calculate paste position first as it's needed for cropping global masks
        x = int(pos_x - layer.bounds.width / 2)
        y = int(pos_y - layer.bounds.height / 2)

        processed_img = _apply_mask_to_image(
            processor, processed_img, state, None, cumulative_masks, layer, (x, y)
        )
    else:
        # Standard positioning
        x = int(pos_x - layer.bounds.width / 2)
        y = int(pos_y - layer.bounds.height / 2)

    # 4. Apply Opacity (Global)
    if opacity != 1.0:
        alpha = processed_img.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        processed_img.putalpha(alpha)

    # 5. Composite
    canvas.paste(processed_img, (x, y), processed_img)

    return canvas
