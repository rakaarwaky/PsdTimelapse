from collections.abc import Callable

from PIL import Image

from ....entities.layer_entity import LayerEntity
from ....entities.viewport_entity import ViewportEntity
from ....entities.world_entity import WorldEntity
from ....value_objects.geometry import Vector2
from ..services.layer_service import LayerRetrievalService
from .opacity_module import apply_opacity

try:
    from ...animator import LayerAnimState, apply_mask_to_layer, generate_reveal_mask
except ImportError:
    pass


def composite_centered_layer(
    frame: Image.Image,
    layer: LayerEntity,
    state: "LayerAnimState",
    scale: float,
    y_offset: float,
    layer_service: LayerRetrievalService,
) -> Image.Image:
    """Composite a single layer with PSD-to-viewport centering."""
    layer_img = layer_service.get_layer_image(layer)
    if layer_img is None:
        return frame

    # 1. Apply Reveal Mask (on original resolution)
    if 0 < state.reveal_progress < 1.0 and state.path:
        mask = generate_reveal_mask(
            layer_size=layer_img.size,
            path=state.path,
            progress=state.reveal_progress,
            brush_size=state.brush_size,
            layer_origin=Vector2(layer.bounds.x, layer.bounds.y),
        )
        layer_img = apply_mask_to_layer(layer_img, mask)

    # 2. Scale
    new_w = max(1, int(layer_img.width * scale))
    new_h = max(1, int(layer_img.height * scale))

    if new_w > 0 and new_h > 0:
        try:
            layer_img = layer_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        except Exception:
            pass

    # Calculate position with centering offset
    pos_x = int(layer.bounds.x * scale)
    pos_y = int(layer.bounds.y * scale + y_offset)

    # 3. Opacity
    if state.opacity < 1.0:
        layer_img = apply_opacity(layer_img, state.opacity)

    # Composite
    try:
        if layer_img.mode == "RGBA":
            frame.paste(layer_img, (pos_x, pos_y), layer_img)
        else:
            frame.paste(layer_img, (pos_x, pos_y))
    except Exception:
        pass

    return frame


def compose_centered_frame(
    world: WorldEntity,
    viewport: ViewportEntity,
    layer_states: dict[str, "LayerAnimState"],
    find_layer_func: Callable[[str], LayerEntity | None],
    layer_service: LayerRetrievalService,
) -> Image.Image:
    """
    Compose frame with PSD centered in viewport.
    Centers PSD document within viewport by calculating proper Y offset.
    """
    # Create blank frame with background color
    frame = Image.new(
        "RGBA", (viewport.output_width, viewport.output_height), viewport.background_color
    )

    # Calculate scale to fit PSD width to viewport width
    scale = viewport.output_width / world.width

    # Calculate Y offset to center PSD vertically in viewport
    scaled_psd_height = world.height * scale
    y_offset = (viewport.output_height - scaled_psd_height) / 2

    # Compose each layer
    for layer_id, state in layer_states.items():
        if not state.visible or state.opacity <= 0:
            continue

        layer = find_layer_func(layer_id)
        if not layer or layer.image_data is None:
            continue

        frame = composite_centered_layer(frame, layer, state, scale, y_offset, layer_service)

    return frame
