"""
NvencEncoderAdapter: GPU-accelerated video encoding using NVIDIA NVENC.
Uses FFmpeg with h264_nvenc for hardware-accelerated encoding.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Any

try:
    import numpy as np  # type: ignore[unused-ignore]
    from PIL import Image

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

from domain.entities.viewport_entity import ViewportEntity  # type: ignore[import-not-found]
from domain.ports.media.video_port import VideoPort  # type: ignore[import-not-found]

from .alpha_composite_module import alpha_composite, convert_to_numpy_rgb, convert_to_numpy_rgba
from .ffmpeg_command_factory import (
    build_libx264_command_from_images,
    build_libx264_command_from_pipe,
    build_nvenc_command_from_images,
    build_nvenc_command_from_pipe,
    ensure_output_dir,
)

# Import extracted modules
from .nvenc_capability_module import detect_encoder


class NvencEncoderAdapter(VideoPort):  # type: ignore[misc]
    """
    Video encoder using NVIDIA NVENC hardware acceleration.

    Requires:
    - NVIDIA GPU with NVENC support (GTX 600+, RTX series)
    - FFmpeg compiled with NVENC support
    - nvidia-drivers installed
    """

    def __init__(self, fallback_to_cpu: bool = True):
        """Initialize NVENC encoder."""
        if not HAS_DEPS:
            raise ImportError("Pillow and numpy required")

        self._frames: list[np.ndarray] = []
        self._output_path: str | None = None
        self._viewport: ViewportEntity | None = None
        self._is_recording: bool = False

        self._use_nvenc, self._encoder_name = detect_encoder(fallback_to_cpu)

    def start_recording(
        self, output_path: str, viewport: ViewportEntity, codec: str = "h264_nvenc"
    ) -> None:
        """Initialize video recording session."""
        self._frames = []
        self._output_path = output_path
        self._viewport = viewport
        self._is_recording = True
        ensure_output_dir(output_path)

    def add_frame(self, image: Any) -> None:
        """Add a frame to the video stream."""
        if not self._is_recording:
            raise RuntimeError("Recording not started")
        self._frames.append(convert_to_numpy_rgb(image))

    def add_frames(self, images: list[Any]) -> None:
        """Add multiple frames at once."""
        for img in images:
            self.add_frame(img)

    def save(self) -> str:
        """Finalize and save the video file using NVENC."""
        if not self._is_recording:
            raise RuntimeError("Recording not started")
        if not self._frames:
            raise RuntimeError("No frames to save")

        fps = self._viewport.fps if self._viewport else 30
        temp_dir = tempfile.mkdtemp(prefix="nvenc_")

        try:
            # Save frames as images
            for i, frame in enumerate(self._frames):
                img = Image.fromarray(frame)
                img.save(os.path.join(temp_dir, f"frame_{i:06d}.png"))

            # Build command using factory
            input_pattern = os.path.join(temp_dir, "frame_%06d.png")
            if self._use_nvenc:
                cmd = build_nvenc_command_from_images(input_pattern, self._output_path, fps)  # type: ignore[arg-type]
            else:
                cmd = build_libx264_command_from_images(input_pattern, self._output_path, fps)  # type: ignore[arg-type]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        self._is_recording = False
        return self._output_path  # type: ignore[return-value]

    def save_with_layers(
        self, static_layer: Any, dynamic_frames: list[Any], output_path: str, fps: int = 30
    ) -> str:
        """Save video using multi-layer compositing with NVENC."""
        if not dynamic_frames:
            raise ValueError("No dynamic frames provided")

        static_np = convert_to_numpy_rgba(static_layer)
        height, width = static_np.shape[:2]
        ensure_output_dir(output_path)

        # Build command using factory
        if self._use_nvenc:
            cmd = build_nvenc_command_from_pipe(width, height, fps, output_path)
        else:
            cmd = build_libx264_command_from_pipe(width, height, fps, output_path)

        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        try:
            for dyn_frame in dynamic_frames:
                dyn_np = convert_to_numpy_rgba(dyn_frame)
                composite = alpha_composite(static_np, dyn_np)
                process.stdin.write(composite.tobytes())  # type: ignore[union-attr]

            process.stdin.close()  # type: ignore[union-attr]
            returncode = process.wait()

            if returncode != 0:
                stderr = process.stderr.read().decode() if process.stderr else ""
                raise RuntimeError(f"FFmpeg failed (code {returncode}): {stderr}")

        except Exception as e:
            process.kill()
            process.wait()
            raise e
        finally:
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

        return output_path

    def cancel(self) -> None:
        """Cancel recording and clean up resources."""
        self._frames = []
        self._is_recording = False
        self._output_path = None

    @property
    def frame_count(self) -> int:
        """Get current number of frames recorded."""
        return len(self._frames)

    @property
    def duration(self) -> float:
        """Get current video duration in seconds."""
        if not self._viewport:
            return 0.0
        fps = self._viewport.fps
        return self.frame_count / fps if fps > 0 else 0.0

    def get_progress(self) -> dict[str, Any]:
        """Get recording progress info."""
        estimated_size = 0
        if self._frames:
            frame_bytes = self._frames[0].nbytes
            estimated_size = (frame_bytes * len(self._frames) * 0.1) / (1024 * 1024)  # type: ignore[assignment]

        return {
            "frame_count": self.frame_count,
            "duration": self.duration,
            "estimated_size_mb": round(estimated_size, 2),
            "is_recording": self._is_recording,
            "encoder": "NVENC" if self._use_nvenc else "libx264",
        }
