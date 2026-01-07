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

    Args:
        layer_img: Input layer image (type agnostic)
        layer: Layer entity with bounds info
        state: Animation state (optional)
        canvas_width: Output canvas width
        canvas_height: Output canvas height
        cumulative_masks: Mask cache by layer ID
        image_processor: Injected image processor (PIL.Image compatible)

    Returns:
        Canvas image with layer rendered
    """
    # Fallback to PIL if no processor injected (backward compatibility)
    if image_processor is None:
        try:
            from PIL import Image as PILImage
            from PIL import ImageDraw as PILImageDraw

            # Create wrapper for PIL
            class PILProcessor:
                Image = PILImage
                ImageDraw = PILImageDraw

                def new(
                    self, mode: str, size: tuple[int, int], color: tuple[int, ...] | int
                ) -> Any:
                    return PILImage.new(mode, size, color)

                def draw(self, image: Any) -> Any:
                    return PILImageDraw.Draw(image)

                def composite(self, im1: Any, im2: Any, mask: Any) -> Any:
                    return PILImage.composite(im1, im2, mask)

            image_processor = PILProcessor()
        except ImportError:
            raise RuntimeError("No image_processor provided and PIL not available") from None

    # Create blank canvas
    canvas = image_processor.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

    if layer_img and (not state or state.visible):
        pos_x = state.position.x if state else layer.position.x
        pos_y = state.position.y if state else layer.position.y
        opacity = state.opacity if state else layer.opacity.value

        # Process image (Opacity)
        processed_img = layer_img.convert("RGBA")

        # Apply Reveal Mask
        if state and state.reveal_progress < 1.0:
            # Decide Mask Strategy: Wipe vs Circle Brush
            if state.brush_size > 0:
                # Cumulative Mask Strategy
                mask = cumulative_masks.get(layer.id)
                if mask:
                    # Draw brush TIP at current confirmed brush_position
                    draw = image_processor.draw(mask)
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
                    # Fallback if somehow missing
                    mask = image_processor.new("L", processed_img.size, 255)
            else:
                # Wipe Strategy
                mask = image_processor.new("L", processed_img.size, 0)
                draw = image_processor.draw(mask)
                w, h = processed_img.size

                if state.reveal_direction == "vertical":
                    h_reveal = int(h * state.reveal_progress)
                    draw.rectangle([0, 0, w, h_reveal], fill=255)
                else:
                    w_reveal = int(w * state.reveal_progress)
                    draw.rectangle([0, 0, w_reveal, h], fill=255)

            # Apply Opacity
            if opacity != 1.0:
                alpha = processed_img.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                processed_img.putalpha(alpha)

            # Position
            x = int(pos_x - layer.bounds.width / 2)
            y = int(pos_y - layer.bounds.height / 2)

            # Apply Mask during Paste
            if state.reveal_progress < 1.0 and state.brush_size > 0:
                # Circle Brush Global Mask
                global_mask = cumulative_masks.get(layer.id)
                if global_mask:
                    layer_mask = global_mask.crop(
                        (x, y, x + processed_img.width, y + processed_img.height)
                    )
                    layer_alpha = processed_img.split()[3]
                    final_alpha = image_processor.composite(
                        layer_alpha, image_processor.new("L", layer_mask.size, 0), layer_mask
                    )
                    processed_img.putalpha(final_alpha)

            elif state.reveal_progress < 1.0 and not (state.brush_size > 0):
                # Wipe Logic
                mask = image_processor.new("L", processed_img.size, 0)
                draw = image_processor.draw(mask)
                w, h = processed_img.size
                if state.reveal_direction == "vertical":
                    h_reveal = int(h * state.reveal_progress)
                    draw.rectangle([0, 0, w, h_reveal], fill=255)
                else:
                    w_reveal = int(w * state.reveal_progress)
                    draw.rectangle([0, 0, w_reveal, h], fill=255)

                current_alpha = processed_img.split()[3]
                composite_alpha = image_processor.composite(
                    current_alpha, image_processor.new("L", processed_img.size, 0), mask
                )
                processed_img.putalpha(composite_alpha)

            canvas.paste(processed_img, (x, y), processed_img)
        else:
            # Simple render without reveal logic
            if state and opacity != 1.0:
                processed_img = layer_img.convert("RGBA")
                alpha = processed_img.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                processed_img.putalpha(alpha)
                layer_img = processed_img

            pos_x = state.position.x if state else layer.position.x
            pos_y = state.position.y if state else layer.position.y
            x = int(pos_x - layer.bounds.width / 2)
            y = int(pos_y - layer.bounds.height / 2)
            canvas.paste(layer_img, (x, y), layer_img)

    return canvas
