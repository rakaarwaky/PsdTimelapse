from PIL import Image


def apply_opacity(img: Image.Image, opacity: float) -> Image.Image:
    """
    Apply opacity to image alpha channel.
    Target Size: < 20 lines.
    """
    if opacity >= 1.0:
        return img

    if img.mode != "RGBA":
        img = img.convert("RGBA")

    r, g, b, a = img.split()
    a = a.point(lambda x: int(x * opacity))
    return Image.merge("RGBA", (r, g, b, a))
