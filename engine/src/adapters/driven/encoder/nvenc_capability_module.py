"""
NVENC Capability Module: Detect NVIDIA NVENC hardware encoder availability.
"""

from __future__ import annotations

import subprocess


def check_nvenc_available() -> bool:
    """
    Check if NVENC is available via FFmpeg.

    Returns:
        True if h264_nvenc encoder is available.
    """
    try:
        result = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True, timeout=5)
        return "h264_nvenc" in result.stdout
    except Exception:
        return False


def detect_encoder(fallback_to_cpu: bool = True) -> tuple[bool, str]:
    """
    Detect which encoder to use.

    Args:
        fallback_to_cpu: Allow CPU fallback if NVENC unavailable.

    Returns:
        Tuple of (use_nvenc: bool, encoder_name: str)

    Raises:
        RuntimeError: If NVENC unavailable and fallback disabled.
    """
    use_nvenc = check_nvenc_available()

    if use_nvenc:
        print("✓ NVENC hardware encoder detected")
        return True, "h264_nvenc"
    elif fallback_to_cpu:
        print("⚠ NVENC not available, using CPU encoding")
        return False, "libx264"
    else:
        raise RuntimeError("NVENC not available and fallback disabled")
