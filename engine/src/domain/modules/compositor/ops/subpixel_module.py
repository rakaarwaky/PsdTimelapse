import numpy as np
from PIL import Image

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def apply_subpixel_shift(
    img: Image.Image, shift_x: float, shift_y: float, padding: int = 2
) -> tuple[Image.Image, tuple[int, int]]:
    """
    Apply sub-pixel shift using OpenCV warpAffine with padding to prevent clipping.
    Falls back to no-op if cv2 is not installed.

    Args:
        img: Source PIL Image.
        shift_x: Horizontal shift (0.0 - 1.0).
        shift_y: Vertical shift (0.0 - 1.0).
        padding: Pixels to pad around the image to capture shifted edges.

    Returns:
        (Shifted PIL Image, (offset_x_correction, offset_y_correction))
    """
    # Precision threshold or cv2 not available -> no-op
    if not CV2_AVAILABLE or (abs(shift_x) < 0.01 and abs(shift_y) < 0.01):
        return img, (0, 0)

    # Convert to OpenCV (numpy)
    img_np = np.array(img)

    # Add Padding (Transparent)
    # This prevents the border from being clipped when shifting
    if padding > 0:
        img_np = cv2.copyMakeBorder(
            img_np, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0)
        )

    height, width = img_np.shape[:2]

    # Transformation Matrix [ [1, 0, shift_x], [0, 1, shift_y] ]
    # Note: We are shifting the PADDED image.
    matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])

    # Apply Warp with Lanczos4 Interpolation (High Quality)
    warped = cv2.warpAffine(
        img_np,
        matrix,
        (width, height),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )

    # Return image and the offset correction (negative padding)
    # The compositor needs to paste this image at (pos_x - padding, pos_y - padding)
    return Image.fromarray(warped), (-padding, -padding)
