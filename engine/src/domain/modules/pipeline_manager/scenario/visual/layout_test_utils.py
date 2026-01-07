"""
Layout Test Utilities
=====================
Helper functions for layout and viewport testing.
"""
import os
import shutil
from typing import Tuple  # noqa: PLR0913, PLR0912

try:
    from PIL import ImageDraw
except ImportError:
    ImageDraw = None

# Domain Imports
from domain.entities.camera_entity import CameraEntity
from domain.entities.viewport_entity import ViewportEntity
from domain.value_objects.geometry.vector_value import Vector2


def setup_output_dir(output_dir: str):
    """Clear and recreate output directory."""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)


def create_centered_viewport(
    psd_width: int,
    psd_height: int,
    viewport_size: int = 1080
) -> Tuple[ViewportEntity, CameraEntity]:  # noqa: PLR0913, PLR0912
    """
    Create 1:1 viewport with camera centered on PSD content.

    Args:
        psd_width: Original PSD width
        psd_height: Original PSD height
        viewport_size: Size of the square viewport

    Returns:
        Tuple of (ViewportEntity, CameraEntity) configured for centered layout
    """
    viewport = ViewportEntity(
        output_width=viewport_size,
        output_height=viewport_size,
        fps=30,
        background_color=(255, 255, 255, 255)
    )

    # Camera centers on PSD center
    camera = CameraEntity(
        position=Vector2(psd_width / 2, psd_height / 2),
        zoom=1.0
    )

    # Calculate zoom to fit PSD into 1:1 viewport
    max_dim = max(psd_width, psd_height)
    fit_zoom = viewport_size / max_dim
    camera.zoom_to(fit_zoom)

    return viewport, camera


def draw_coordinate_info(
    draw: 'ImageDraw.Draw',
    label: str,
    world_pos: Vector2,
    viewport_pos: Vector2,
    color: tuple
):
    """Draw debug info about a coordinate transformation."""
    try:
        x, y = int(viewport_pos.x), int(viewport_pos.y)

        # Draw point
        r = 8
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

        # Draw label
        info = f"{label}\nWorld: ({int(world_pos.x)}, {int(world_pos.y)})\nViewport: ({x}, {y})"
        draw.text((x + 12, y - 20), info, fill=color)

    except Exception as e:
        print(f"Warning: Could not draw {label}: {e}")
