from dataclasses import dataclass

try:
    from PIL import Image
except ImportError:
    pass


@dataclass
class CompositeFrame:
    """A single composed frame with all layers merged."""

    frame_number: int
    image: "Image.Image"
