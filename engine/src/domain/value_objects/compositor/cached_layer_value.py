from dataclasses import dataclass

try:
    from PIL import Image
except ImportError:
    pass


@dataclass
class CachedLayer:
    """A cached static layer."""

    name: str
    image: "Image.Image"
    width: int
    height: int
    hash: str
