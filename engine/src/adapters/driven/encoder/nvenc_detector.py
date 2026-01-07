import subprocess


def check_nvenc_available() -> bool:
    """Check if NVENC is available via FFmpeg."""
    try:
        result = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True, timeout=5)
        return "h264_nvenc" in result.stdout
    except Exception:
        return False
