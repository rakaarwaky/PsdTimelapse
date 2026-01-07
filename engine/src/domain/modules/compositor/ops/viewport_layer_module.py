from PIL import Image

from ....entities.layer_entity import LayerEntity
from ....value_objects.geometry import Vector2
from ...layout_manager.coordinate_mapper_module import CoordinateMapper
from ..services.layer_service import LayerRetrievalService
from .opacity_module import apply_opacity

try:
    from ...animator import (  # type: ignore[attr-defined]
        LayerAnimState,
        apply_mask_to_layer,
        generate_reveal_mask,
    )
except ImportError:
    # Placeholder types/funcs if circular import issues arise,
    # but in atomic op we expect them to be available or passed in.
    pass


def composite_viewport_layer(
    base: Image.Image,
    layer: LayerEntity,
    state: "LayerAnimState",
    mapper: CoordinateMapper,
    layer_service: LayerRetrievalService,
) -> Image.Image:
    """Composite a single layer with animation state and camera transform."""
    if layer.image_data is None:
        return base

    # Get or create layer image using service
    layer_img = layer_service.get_layer_image(layer)
    if layer_img is None:
        return base

    # Calculate position based on animation state
    if state.position.x != 0 or state.position.y != 0:
        # Use animated position
        viewport_pos = mapper.world_to_viewport(state.position)
    else:
        # Use original layer position
        viewport_pos = mapper.world_to_viewport(Vector2(layer.bounds.x, layer.bounds.y))

    # Scale based on camera zoom
    new_width = int(layer.bounds.width * mapper.camera.zoom)
    new_height = int(layer.bounds.height * mapper.camera.zoom)

    if new_width <= 0 or new_height <= 0:
        return base

    # 1. Apply Mask to Original (if needed)
    img_to_composite = layer_img
    if 0 < state.reveal_progress < 1.0 and state.path:
        mask = generate_reveal_mask(
            layer_size=layer_img.size,
            path=state.path,
            progress=state.reveal_progress,
            brush_size=state.brush_size,
            layer_origin=Vector2(layer.bounds.x, layer.bounds.y),
        )
        img_to_composite = apply_mask_to_layer(layer_img, mask)

    # 2. Scale
    try:
        scaled = img_to_composite.resize((new_width, new_height), Image.Resampling.LANCZOS)
    except Exception:
        return base

    # 3. Opacity
    if state.opacity < 1.0:
        scaled = apply_opacity(scaled, state.opacity)

    # Paste onto base
    paste_x = int(viewport_pos.x)
    paste_y = int(viewport_pos.y)

    try:
        if scaled.mode == "RGBA":
            base.paste(scaled, (paste_x, paste_y), scaled)
        else:
            base.paste(scaled, (paste_x, paste_y))
    except Exception:
        pass

    return base
