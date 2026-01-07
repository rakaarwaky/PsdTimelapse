import math

import cv2  # type: ignore[import-not-found]
import numpy as np
from PIL import Image

from domain.value_objects.geometry import Vector2  # type: ignore[import-not-found]

# Constants
EPSILON = 1e-6
DEFAULT_BLUR_THRESHOLD = 1e-6
RGB_CHANNELS = 3


def apply_motion_blur(img: Image.Image, velocity: Vector2) -> tuple[Image.Image, tuple[int, int]]:
    """Apply motion blur approximation using OpenCV.
    Returns (Blurred Image, (offset_x, offset_y)).
    """
    if not velocity or (abs(velocity.x) < EPSILON and abs(velocity.y) < EPSILON):
        return img, (0, 0)

    speed = (velocity.x**2 + velocity.y**2) ** 0.5
    # Threshold: Only blur if moving fast enough
    if speed < DEFAULT_BLUR_THRESHOLD:
        return img, (0, 0)

    # Convert PIL -> OpenCV (RGB)

    open_cv_image = np.array(img)

    # Kernel Size based on speed strength
    k_size = int(min(50, speed * 0.5))
    if k_size < 1:
        return img, (0, 0)

    # Create the kernel
    kernel = np.zeros((k_size, k_size), dtype=np.float32)
    # Fill middle row with ones (horizontal line)
    kernel[int((k_size - 1) / 2), :] = np.ones(k_size, dtype=np.float32)
    # Normalize
    kernel /= k_size

    # Calculate Angle

    angle = math.degrees(math.atan2(velocity.y, velocity.x))

    # Rotate Kernel
    rotation_matrix = cv2.getRotationMatrix2D((k_size / 2 - 0.5, k_size / 2 - 0.5), angle, 1.0)
    kernel_rotated = cv2.warpAffine(kernel, rotation_matrix, (k_size, k_size))

    # ADD PADDING to prevent clipping
    # We need enough padding for the kernel radius
    pad = k_size // 2 + 2
    padded_image = cv2.copyMakeBorder(
        open_cv_image, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0)
    )

    # Apply Filter to PADDED image
    blurred = cv2.filter2D(padded_image, -1, kernel_rotated)

    # Return padded image and negative offset
    return Image.fromarray(blurred), (-pad, -pad)
