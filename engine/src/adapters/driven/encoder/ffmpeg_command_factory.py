"""
FFmpeg Command Factory: Build FFmpeg encoding commands.
"""

from __future__ import annotations

import os


def build_nvenc_command_from_images(input_pattern: str, output_path: str, fps: int) -> list[str]:
    """Build NVENC encoding command for image sequence input."""
    return [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        input_pattern,
        "-c:v",
        "h264_nvenc",
        "-preset",
        "p4",  # Balanced preset
        "-tune",
        "hq",  # High quality
        "-rc",
        "vbr",  # Variable bitrate
        "-cq",
        "23",  # Quality level (lower = better)
        "-b:v",
        "0",  # Let CQ control bitrate
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]


def build_libx264_command_from_images(input_pattern: str, output_path: str, fps: int) -> list[str]:
    """Build libx264 (CPU) encoding command for image sequence input."""
    return [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        input_pattern,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]


def build_nvenc_command_from_pipe(width: int, height: int, fps: int, output_path: str) -> list[str]:
    """Build NVENC encoding command for raw pipe input."""
    return [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        f"{width}x{height}",
        "-pix_fmt",
        "rgb24",
        "-r",
        str(fps),
        "-i",
        "-",  # Read from stdin
        "-c:v",
        "h264_nvenc",
        "-preset",
        "p4",
        "-tune",
        "hq",
        "-rc",
        "vbr",
        "-cq",
        "23",
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]


def build_libx264_command_from_pipe(
    width: int, height: int, fps: int, output_path: str
) -> list[str]:
    """Build libx264 (CPU) encoding command for raw pipe input."""
    return [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        f"{width}x{height}",
        "-pix_fmt",
        "rgb24",
        "-r",
        str(fps),
        "-i",
        "-",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]


def ensure_output_dir(output_path: str) -> None:
    """Ensure output directory exists."""
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
