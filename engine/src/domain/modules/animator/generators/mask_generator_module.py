"""
MaskGenerator: Generate reveal masks for brush animation.
Separated from compositor for proper separation of concerns.

NOTE: ImageProcessingPort MUST be injected (Hexagonal Architecture).
      No default adapter fallback.
"""

from __future__ import annotations

from typing import Any

from ....value_objects.animation import BrushTool

# REMOVED: ImageProcessingPort (Submodules must be pure)
from ....value_objects.animation.animation_path import AnimationPath
from ....value_objects.geometry import Rect, Vector2


def generate_reveal_mask(  # noqa: PLR0913
    layer_size: tuple[int, int],
    path: AnimationPath,
    progress: float,
    brush_size: float,
    blur_radius: float = 15.0,
    layer_origin: Vector2 | None = None,
    image_processor: Any = None,
) -> Any:
    """
    Facade for mask generation.
    """
    if layer_origin is None:
        layer_origin = Vector2(0, 0)

    """
    Generate organic brush reveal mask.

    Args:
        layer_size: (width, height) of the layer image
        path: Animation path containing brush stroke points (World Space)
        progress: Current reveal progress (0.0 to 1.0)
        brush_size: Diameter of brush stroke
        blur_radius: Edge blur for organic feel
        layer_origin: Top-left World position of the layer
        image_processor: REQUIRED ImageProcessingPort implementation.

    Returns:
        Grayscale mask image (L mode). White = visible, Black = hidden.

    Raises:
        ValueError: If image_processor is not provided.
    """
    if image_processor is None:
        raise ValueError("image_processor (ImageProcessingPort) must be provided.")

    processor = image_processor
    width, height = layer_size

    # Create black mask (invisible start)
    mask = processor.create_canvas(width, height, (0, 0, 0, 255))

    if not path or not path.points:
        # No path = full reveal at progress 1.0
        if progress >= 1.0:
            return processor.create_canvas(width, height, (255, 255, 255, 255))
        return mask

    # Calculate brush radius
    brush_radius = brush_size / 2

    # Calculate how many points to draw based on progress
    total_points = len(path.points)
    current_idx = int(progress * (total_points - 1))
    current_idx = max(0, min(current_idx, total_points - 1))

    # Draw cumulative path strokes
    for i in range(current_idx + 1):
        pt = path.points[i]

        # Transform World Space -> Layer Local Space
        lx = pt.x - layer_origin.x
        ly = pt.y - layer_origin.y

        # Draw circle at each point
        bbox = (lx - brush_radius, ly - brush_radius, lx + brush_radius, ly + brush_radius)
        mask = processor.draw_ellipse(mask, bbox, fill=(255, 255, 255, 255))

    # Apply gaussian blur for smooth organic edge
    if blur_radius > 0:
        mask = processor.gaussian_blur(mask, blur_radius)

    return mask


def apply_mask_to_layer(layer_image: Any, mask: Any, image_processor: Any) -> Any:
    """
    Apply reveal mask to layer image.

    Args:
        layer_image: Original layer image (RGBA)
        mask: Reveal mask (grayscale)
        image_processor: REQUIRED ImageProcessingPort implementation.

    Returns:
        Masked layer image with updated alpha channel

    Raises:
        ValueError: If image_processor is not provided.
    """
    if image_processor is None:
        raise ValueError("image_processor (ImageProcessingPort) must be provided.")
    return image_processor.apply_mask(layer_image, mask)


def calculate_brush_size_for_layer(layer_bounds: Rect) -> float:
    """
    Calculate optimal brush size (legacy, returns float).

    Formula: BrushSize = max(width, height) * 1.1
    """
    return max(layer_bounds.width, layer_bounds.height) * 1.1


def create_brush_tool_for_layer(layer_bounds: Rect, hardness: float = 0.3) -> BrushTool:
    """
    Create a properly configured BrushTool for a given layer.

    Args:
        layer_bounds: The layer's bounding rectangle.
        hardness: Edge hardness (0.0 = soft/blurry, 1.0 = sharp).

    Returns:
        A BrushTool configured for organic reveal animation.
    """
    size = max(layer_bounds.width, layer_bounds.height) * 1.1
    return BrushTool(size_px=size, hardness=hardness)


def generate_reveal_mask_v2(  # noqa: PLR0913
    layer_size: tuple[int, int],
    path: AnimationPath,
    progress: float,
    tool: BrushTool,
    layer_origin: Vector2 | None = None,
    image_processor: Any = None,
) -> Any:
    """
    Generate the mask for a brush stroke.
    """
    if layer_origin is None:
        layer_origin = Vector2(0, 0)

    """
    Generate organic brush reveal mask using BrushTool configuration.

    Args:
        layer_size: (width, height) of the layer image.
        path: Animation path containing brush stroke points (World Space).
        progress: Current reveal progress (0.0 to 1.0).
        tool: BrushTool configuration object.
        layer_origin: Top-left World position of the layer.
        image_processor: REQUIRED ImageProcessingPort implementation.

    Returns:
        Grayscale mask image (L mode). White = visible, Black = hidden.
    """
    # Delegate to original function using BrushTool properties
    return generate_reveal_mask(
        layer_size=layer_size,
        path=path,
        progress=progress,
        brush_size=tool.size_px,
        blur_radius=tool.blur_radius,
        layer_origin=layer_origin,
        image_processor=image_processor,
    )
