"""
DocumentEntity: White square canvas representing the PSD document background.
Auto-sizes to fit PSD content with locked 1:1 aspect ratio.
"""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


@dataclass
class DocumentEntity:
    """
    White square canvas entity.

    Automatically creates a 1:1 aspect ratio white background
    that fits the PSD document dimensions.

    Attributes:
        psd_width: Original PSD width
        psd_height: Original PSD height
        size: Final square size (max of width/height)
        background_color: Locked to white (255, 255, 255)
    """

    psd_width: int
    psd_height: int
    background_color: tuple[int, int, int] = field(default=(255, 255, 255), init=False)

    @property
    def size(self) -> int:
        """Square size = max(width, height) for 1:1 ratio."""
        return max(self.psd_width, self.psd_height)

    @property
    def width(self) -> int:
        return self.size

    @property
    def height(self) -> int:
        return self.size

    @property
    def offset_x(self) -> int:
        """X offset to center PSD content."""
        return (self.size - self.psd_width) // 2

    @property
    def offset_y(self) -> int:
        """Y offset to center PSD content."""
        return (self.size - self.psd_height) // 2

    def create_image(self) -> Image.Image:
        """Create the white square background as PIL Image."""
        if not HAS_PILLOW:
            raise ImportError("Pillow required for image generation")

        return Image.new("RGBA", (self.size, self.size), (*self.background_color, 255))

    @classmethod
    def from_psd_dimensions(cls, width: int, height: int) -> DocumentEntity:
        """Factory method to create DocumentEntity from PSD dimensions."""
        return cls(psd_width=width, psd_height=height)

    def __repr__(self) -> str:
        return f"Document({self.size}x{self.size}, psd={self.psd_width}x{self.psd_height})"
