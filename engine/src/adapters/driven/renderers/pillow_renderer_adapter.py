"""
PillowRenderer: Concrete implementation of RendererPort using Pillow library.
Dependencies: Pillow, Domain.Ports.RendererPort
"""

from __future__ import annotations

from typing import Any

from domain.entities.camera_entity import CameraEntity
from domain.entities.layer_entity import LayerEntity
from domain.entities.viewport_entity import ViewportEntity
from domain.entities.world_entity import WorldEntity
from domain.modules.layout_manager import CoordinateMapper
from domain.ports.render.renderer_port import RendererPort
from domain.value_objects.geometry.vector_value import Vector2

try:
    from PIL import Image, ImageDraw

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    Image = None


class PillowRenderer(RendererPort):
    """
    Adapter for rendering frames using Pillow (PIL) library.

    Composites visible layers based on camera position and zoom.
    """

    def __init__(self):
        if not HAS_PILLOW:
            raise ImportError("Pillow not installed. Run: pip install Pillow")

    def render_frame(
        self, world: WorldEntity, camera: CameraEntity, viewport: ViewportEntity
    ) -> Image.Image:
        """Render a complete frame."""
        frame = self.create_blank_frame(viewport)
        mapper = CoordinateMapper(camera, viewport)

        # Render visible layers in order
        for layer in world.scene.iterate_visible():
            if mapper.is_visible(layer.bounds):
                frame = self.composite_layer(frame, layer, camera, viewport)

        return frame

    def composite_layer(
        self,
        base_image: Image.Image,
        layer: LayerEntity,
        camera: CameraEntity,
        viewport: ViewportEntity,
        opacity_override: float | None = None,
    ) -> Image.Image:
        """Composite a single layer onto base image."""
        if layer.image_data is None:
            return base_image

        mapper = CoordinateMapper(camera, viewport)

        # Get layer image
        layer_img = layer.image_data
        if not isinstance(layer_img, Image.Image):
            # Handle raw bytes or other formats
            return base_image

        # Transform position to viewport space
        viewport_rect = mapper.world_rect_to_viewport(layer.bounds)

        # Scale layer image based on zoom
        new_width = int(viewport_rect.width)
        new_height = int(viewport_rect.height)

        if new_width <= 0 or new_height <= 0:
            return base_image

        # Resize layer image
        try:
            scaled_layer = layer_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        except Exception:
            return base_image

        # Apply opacity
        opacity = opacity_override if opacity_override is not None else layer.opacity
        if opacity < 1.0:
            scaled_layer = self._apply_opacity(scaled_layer, opacity)

        # Composite onto base
        paste_x = int(viewport_rect.x)
        paste_y = int(viewport_rect.y)

        try:
            if scaled_layer.mode == "RGBA":
                base_image.paste(scaled_layer, (paste_x, paste_y), scaled_layer)
            else:
                base_image.paste(scaled_layer, (paste_x, paste_y))
        except Exception:
            pass

        return base_image

    def _apply_opacity(self, img: Image.Image, opacity: float) -> Image.Image:
        """Apply opacity to an image."""
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Multiply alpha channel by opacity
        r, g, b, a = img.split()
        a = a.point(lambda x: int(x * opacity))
        return Image.merge("RGBA", (r, g, b, a))

    def create_blank_frame(self, viewport: ViewportEntity) -> Image.Image:
        """Create a blank frame with background color."""
        color = viewport.background_color
        return Image.new("RGBA", (viewport.output_width, viewport.output_height), color)

    def save_frame(self, image: Image.Image, file_path: str, format: str = "PNG") -> None:
        """Save image to file."""
        image.save(file_path, format=format)

    def draw_cursor(
        self,
        frame: Image.Image,
        position: Vector2,
        size: int = 20,
        color: tuple[Any, ...] = (0, 0, 0, 200),
    ) -> Image.Image:
        """Draw a cursor indicator on the frame."""
        draw = ImageDraw.Draw(frame)

        # Draw a simple arrow cursor
        x, y = int(position.x), int(position.y)
        points = [
            (x, y),
            (x, y + size),
            (x + size * 0.3, y + size * 0.7),
            (x + size * 0.5, y + size * 0.7),
            (x + size * 0.7, y + size),
            (x + size * 0.5, y + size * 0.5),
            (x + size, y + size * 0.5),
        ]
        draw.polygon(points, fill=color)

        return frame
