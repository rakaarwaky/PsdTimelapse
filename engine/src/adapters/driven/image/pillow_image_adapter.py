"""
PillowImageAdapter: PIL-based implementation of ImageProcessingPort.
Dependencies: Pillow (PIL)
"""

from typing import Any

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False

from domain.ports.media.image_processing_port import ImageProcessingPort


class PillowImageAdapter(ImageProcessingPort):
    """
    PIL/Pillow-based implementation of ImageProcessingPort.

    This is the default CPU-based image processing backend.
    For GPU acceleration, use CupyImageAdapter instead.
    """

    def __init__(self) -> None:
        if not HAS_PILLOW:
            raise ImportError("Pillow is required: pip install Pillow")

    def create_canvas(
        self, width: int, height: int, color: tuple[int, int, int, int] = (0, 0, 0, 0)
    ) -> Image.Image:
        """Create a blank RGBA canvas."""
        return Image.new("RGBA", (width, height), color)

    def resize(
        self, image: Image.Image, size: tuple[int, int], resample: str = "lanczos"
    ) -> Image.Image:
        """Resize image using specified resampling method."""
        resample_map = {
            "lanczos": Image.Resampling.LANCZOS,
            "bilinear": Image.Resampling.BILINEAR,
            "bicubic": Image.Resampling.BICUBIC,
            "nearest": Image.Resampling.NEAREST,
        }
        method = resample_map.get(resample.lower(), Image.Resampling.LANCZOS)
        return image.resize(size, method)

    def paste(
        self,
        target: Image.Image,
        source: Image.Image,
        position: tuple[int, int],
        mask: Image.Image | None = None,
    ) -> Image.Image:
        """Paste source onto target at position."""
        result = target.copy()
        if source.mode == "RGBA":
            result.paste(source, position, mask or source)
        else:
            result.paste(source, position, mask)
        return result

    def apply_mask(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """Apply alpha mask to image."""
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Split channels
        r, g, b, a = image.split()

        # Combine original alpha with mask
        mask_l = mask.convert("L")
        new_alpha = ImageChops.multiply(a, mask_l)

        # Merge back
        return Image.merge("RGBA", (r, g, b, new_alpha))

    def gaussian_blur(self, image: Image.Image, radius: float) -> Image.Image:
        """Apply Gaussian blur to image."""
        return image.filter(ImageFilter.GaussianBlur(radius=radius))

    def draw_ellipse(
        self, image: Image.Image, bbox: tuple[float, float, float, float], fill: tuple[int, ...]
    ) -> Image.Image:
        """Draw filled ellipse on image."""
        result = image.copy()
        draw = ImageDraw.Draw(result)
        draw.ellipse(bbox, fill=fill)
        return result

    def get_size(self, image: Image.Image) -> tuple[int, int]:
        """Get image dimensions (width, height)."""
        return image.size

    def copy(self, image: Image.Image) -> Image.Image:
        """Create a copy of the image."""
        return image.copy()

    def to_numpy(self, image: Image.Image) -> Any:
        """Convert PIL Image to numpy array."""
        if not HAS_NUMPY:
            raise ImportError("NumPy is required for to_numpy: pip install numpy")
        return np.array(image)

    def from_numpy(self, array: Any) -> Image.Image:
        """Create PIL Image from numpy array."""
        return Image.fromarray(array)

    def split_channels(self, image: Image.Image) -> tuple[Image.Image, ...]:
        """Split image into individual channels."""
        return image.split()

    def merge_channels(self, channels: tuple[Image.Image, ...], mode: str = "RGBA") -> Image.Image:
        """Merge channels back into image."""
        return Image.merge(mode, channels)

    # === Additional Convenience Methods ===

    def composite(self, background: Image.Image, foreground: Image.Image) -> Image.Image:
        """Alpha composite foreground over background."""
        if background.mode != "RGBA":
            background = background.convert("RGBA")
        if foreground.mode != "RGBA":
            foreground = foreground.convert("RGBA")
        return Image.alpha_composite(background, foreground)

    def crop(self, image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
        """Crop image to specified box (left, top, right, bottom)."""
        return image.crop(box)

    def rotate(self, image: Image.Image, angle: float, expand: bool = False) -> Image.Image:
        """Rotate image by angle (degrees)."""
        return image.rotate(angle, expand=expand, resample=Image.Resampling.BILINEAR)

    def flip_horizontal(self, image: Image.Image) -> Image.Image:
        """Flip image horizontally."""
        return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    def flip_vertical(self, image: Image.Image) -> Image.Image:
        """Flip image vertically."""
        return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    def adjust_opacity(self, image: Image.Image, opacity: float) -> Image.Image:
        """Adjust image opacity (0.0 to 1.0)."""
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        r, g, b, a = image.split()
        # Multiply alpha by opacity
        a = a.point(lambda x: int(x * opacity))
        return Image.merge("RGBA", (r, g, b, a))
