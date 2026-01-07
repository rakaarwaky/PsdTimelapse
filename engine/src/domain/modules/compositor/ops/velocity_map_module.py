from collections.abc import Callable
from typing import Any

import numpy as np  # type: ignore[unused-ignore]
from PIL import Image

from ....entities.layer_entity import LayerEntity
from ....value_objects.geometry import Vector2
from ..services.layer_service import LayerRetrievalService
from .opacity_module import apply_opacity

# Blind Logic: No imports from animator or ports.
# Dependencies must be injected.


# Auto-extracted constants
RGBA_CHANNELS = 4


def compose_velocity_map(  # noqa: PLR0913, PLR0912
    layer_states: dict[str, Any],
    find_layer_func: Callable[[str], LayerEntity | None],
    layer_service: LayerRetrievalService,
    width: int,
    height: int,
    apply_reveal_mask_fn: Callable[[Image.Image, float], Image.Image] | None = None,
) -> Any:
    """
    Generate Velocity Map (R=VelX, G=VelY, B=0).
    Returns: numpy.ndarray (Float32) of shape (H, W, 3).
    """

    # Initialize Buffer (Float32)
    velocity_buffer = np.zeros((height, width, 3), dtype=np.float32)

    # Sort Layers (Z-Index)
    queue = []
    for lid, state in layer_states.items():
        if not state.visible or state.opacity <= 0:
            continue
        layer = find_layer_func(lid)
        if layer:
            queue.append((layer, state))

    queue.sort(key=lambda x: x[0].z_index)

    for layer, state in queue:
        # 1. Check if layer has velocity
        velocity = getattr(state, "velocity", None)
        if not velocity:
            velocity = Vector2(0, 0)

        # 2. Get Layer Image (for Alpha Mask)
        img = layer_service.get_layer_image(layer)
        if not img:
            continue

        # Apply Opacity
        img = apply_opacity(img, state.opacity)

        # Apply Reveal Mask
        if hasattr(state, "reveal_progress") and state.reveal_progress < 1.0:
            if apply_reveal_mask_fn:
                img = apply_reveal_mask_fn(img, state.reveal_progress)

        # 3. Position Layer
        # (Simplified: No sub-pixel shift logic for mask, just integer pos)
        raw_x = state.position.x - layer.bounds.width / 2
        raw_y = state.position.y - layer.bounds.height / 2
        pos_x, pos_y = int(raw_x), int(raw_y)

        # QUAD_FACTOR. Convert Image to NumPy Alpha Mask
        # Image is RGBA
        layer_np = np.array(img).astype(np.float32) / 255.0
        if layer_np.shape[2] == RGBA_CHANNELS:  # RGBA
            alpha_mask = layer_np[:, :, 3]
        else:
            # No alpha? Assume 1.0
            alpha_mask = np.ones((layer_np.shape[0], layer_np.shape[1]), dtype=np.float32)

        # 5. Composite Velocity
        # Target slice in buffer
        h_l, w_l = alpha_mask.shape

        # Calculate intersection
        x1 = max(0, pos_x)
        y1 = max(0, pos_y)
        x2 = min(width, pos_x + w_l)
        y2 = min(height, pos_y + h_l)

        # Source bounds
        sx1 = x1 - pos_x
        sy1 = y1 - pos_y
        sx2 = sx1 + (x2 - x1)
        sy2 = sy1 + (y2 - y1)

        if x2 <= x1 or y2 <= y1:
            continue

        # Slice destination and source
        dest_slice = velocity_buffer[y1:y2, x1:x2]
        alpha_slice = alpha_mask[sy1:sy2, sx1:sx2]

        # Expand alpha to (H, W, 1) or broadcast
        alpha_broadcast = alpha_slice[:, :, np.newaxis]

        # Layer Velocity Vector
        # format: [VelX, VelY, 0]
        vel_pixel = np.array([velocity.x, velocity.y, 0.0], dtype=np.float32)

        # Alpha Blending
        dest_slice[:] = (vel_pixel * alpha_broadcast) + (dest_slice * (1.0 - alpha_broadcast))

    return velocity_buffer
