from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

try:
    from PIL import Image as PILImage
    from PIL import ImageDraw as PILImageDraw
except ImportError:
    PILImage: Any = None  # type: ignore
    PILImageDraw: Any = None  # type: ignore

from ....entities.layer_entity import LayerEntity
from ....value_objects.animation.layer_anim_state import LayerAnimState


class ImageProcessorProtocol(Protocol):
    """Protocol for image processing (PIL or compatible)."""

    def new(self, mode: str, size: tuple[int, int], color: tuple[int, ...] | int) -> Any: ...
    def draw(self, image: Any) -> Any: ...
    def composite(self, im1: Any, im2: Any, mask: Any) -> Any: ...


@dataclass
class RenderContext:
    """Context object to reduce argument clutter in helper functions."""

    processor: Any
    cumulative_masks: dict[str, Any]
    layer_id: str
    canvas_size: tuple[int, int]


def _get_processor(image_processor: Any = None) -> Any:
    """Get image processor or fallback to PIL."""
    if image_processor is not None:
        return image_processor

    if PILImage is None:
        raise RuntimeError("No image_processor provided and PIL not available") from None

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


def _create_wipe_mask(ctx: RenderContext, size: tuple[int, int], state: LayerAnimState) -> Any:
    """Create a wipe transition mask."""
    mask = ctx.processor.new("L", size, 0)
    draw = ctx.processor.draw(mask)
    w, h = size

    if state.reveal_direction == "vertical":
        h_reveal = int(h * state.reveal_progress)
        draw.rectangle([0, 0, w, h_reveal], fill=255)
    else:
        w_reveal = int(w * state.reveal_progress)
        draw.rectangle([0, 0, w_reveal, h], fill=255)
    return mask


def _create_brush_mask(
    ctx: RenderContext,
    size: tuple[int, int],
    state: LayerAnimState,
) -> Any:
    """Create or update a brush-based mask."""
    mask = ctx.cumulative_masks.get(ctx.layer_id)
    if mask:
        # Draw brush TIP at current confirmed brush_position
        draw = ctx.processor.draw(mask)
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
        mask = ctx.processor.new("L", size, 255)
    return mask


def _apply_mask_to_image(
    ctx: RenderContext,
    image: Any,
    state: LayerAnimState,
    pos: tuple[int, int],
) -> Any:
    """Apply mask to image alpha channel."""
    x, y = pos

    # Logic for specialized masking (Brush vs Wipe)
    if state.brush_size > 0:
        # Circle Brush Global Mask
        global_mask = ctx.cumulative_masks.get(ctx.layer_id)
        if global_mask:
            layer_mask = global_mask.crop((x, y, x + image.width, y + image.height))
            layer_alpha = image.split()[3]
            final_alpha = ctx.processor.composite(
                layer_alpha, ctx.processor.new("L", layer_mask.size, 0), layer_mask
            )
            image.putalpha(final_alpha)
    else:
        # Wipe Logic
        local_mask = _create_wipe_mask(ctx, image.size, state)

        current_alpha = image.split()[3]
        composite_alpha = ctx.processor.composite(
            current_alpha, ctx.processor.new("L", image.size, 0), local_mask
        )
        image.putalpha(composite_alpha)

    return image


@dataclass
class LayerRenderContext:
    """Dataclass to encapsulate render arguments and reduce complexity."""

    layer_img: Any
    layer: LayerEntity
    state: LayerAnimState | None
    canvas_size: tuple[int, int]
    cumulative_masks: dict[str, Any]
    image_processor: Any = None


def render_layer_to_image(ctx: LayerRenderContext) -> Any:
    """
    Renders the layer onto a canvas and returns image.
    Refactored to use LayerRenderContext.
    """
    processor = _get_processor(ctx.image_processor)
    canvas = processor.new("RGBA", ctx.canvas_size, (0, 0, 0, 0))

    if not ctx.layer_img:
        return canvas

    is_visible = ctx.state.visible if ctx.state else True
    if not is_visible:
        return canvas

    # Determine render properties
    pos_x = ctx.state.position.x if ctx.state else ctx.layer.position.x
    pos_y = ctx.state.position.y if ctx.state else ctx.layer.position.y
    opacity = ctx.state.opacity if ctx.state else ctx.layer.opacity.value

    # Prepare Internal Context
    internal_ctx = RenderContext(
        processor=processor,
        cumulative_masks=ctx.cumulative_masks,
        layer_id=ctx.layer.id,
        canvas_size=ctx.canvas_size,
    )

    # Process Base Image
    processed_img = ctx.layer_img.convert("RGBA")

    # Handle Reveal State
    if ctx.state and ctx.state.reveal_progress < 1.0:
        if ctx.state.brush_size > 0:
            _create_brush_mask(internal_ctx, processed_img.size, ctx.state)

        x = int(pos_x - ctx.layer.bounds.width / 2)
        y = int(pos_y - ctx.layer.bounds.height / 2)

        processed_img = _apply_mask_to_image(internal_ctx, processed_img, ctx.state, (x, y))
    else:
        x = int(pos_x - ctx.layer.bounds.width / 2)
        y = int(pos_y - ctx.layer.bounds.height / 2)

    # Apply Opacity
    if opacity != 1.0:
        alpha = processed_img.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        processed_img.putalpha(alpha)

    # Composite
    canvas.paste(processed_img, (x, y), processed_img)

    return canvas
