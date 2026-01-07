"""
MoviePyAdapter: Concrete implementation of VideoPort using MoviePy library.
Dependencies: moviepy, Domain.Ports.VideoPort
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np  # type: ignore[unused-ignore]

try:
    from moviepy import ImageSequenceClip  # type: ignore[import-untyped]

    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from domain.entities.viewport_entity import ViewportEntity  # type: ignore[import-not-found]
from domain.ports.media.video_port import VideoPort  # type: ignore[import-not-found]

from .layer_compositor_service import composite_frame_naive, prepare_layer_compositing
from .nvenc_detector import check_nvenc_available


class MoviePyAdapter(VideoPort):  # type: ignore[misc]
    """
    Adapter for video encoding using MoviePy library.
    Accumulates frames and exports to MP4 format.
    """

    def __init__(self, prefer_nvenc: bool = True):
        if not HAS_MOVIEPY:
            raise ImportError("moviepy not installed.")
        if not HAS_PILLOW:
            raise ImportError("Pillow not installed.")

        self._frames: list[np.ndarray] = []
        self._output_path: str | None = None
        self._viewport: ViewportEntity | None = None
        self._is_recording: bool = False

        # Auto-detect NVENC
        self._use_nvenc = prefer_nvenc and check_nvenc_available()
        self._codec = "h264_nvenc" if self._use_nvenc else "libx264"

        print(f"MoviePy using encoder: {self._codec}")

    def start_recording(
        self, output_path: str, viewport: ViewportEntity, codec: str = "libx264"
    ) -> None:
        """Initialize video recording session."""
        self._frames = []
        self._output_path = output_path
        self._viewport = viewport
        self._codec = codec
        self._is_recording = True

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def add_frame(self, image: Any) -> None:
        """Add a frame to the video stream."""
        if not self._is_recording:
            raise RuntimeError("Recording not started")

        if hasattr(image, "convert"):  # PIL Image
            frame_array = np.array(image.convert("RGB"))
        elif isinstance(image, np.ndarray):
            frame_array = image
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")

        self._frames.append(frame_array)

    def add_frames(self, images: list[Any]) -> None:
        """Add multiple frames at once."""
        for img in images:
            self.add_frame(img)

    def save(self) -> str:
        """Finalize and save the video file."""
        if not self._is_recording or not self._frames:
            raise RuntimeError("Cannot save: Recording not started or empty")

        fps = self._viewport.fps if self._viewport else 30
        clip = ImageSequenceClip(self._frames, fps=fps)

        clip.write_videofile(self._output_path, codec=self._codec, audio=False)
        clip.close()
        self._is_recording = False
        return self._output_path  # type: ignore[return-value]

    def cancel(self) -> None:
        """Cancel recording and clean up resources."""
        self._frames = []
        self._is_recording = False
        self._output_path = None

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    @property
    def duration(self) -> float:
        if not self._viewport:
            return 0.0
        return self.frame_count / self._viewport.fps if self._viewport.fps > 0 else 0.0

    def get_progress(self) -> dict[str, Any]:
        estimated_size = 0
        if self._frames:
            frame_bytes = self._frames[0].nbytes
            estimated_size = (frame_bytes * len(self._frames) * 0.1) / (1024 * 1024)  # type: ignore[assignment]

        return {
            "frame_count": self.frame_count,
            "duration": self.duration,
            "estimated_size_mb": round(estimated_size, 2),
            "is_recording": self._is_recording,
        }

    def save_with_layers(
        self, static_layer: Image.Image, dynamic_frames: list[Any], output_path: str, fps: int = 30
    ) -> str:
        """Save video using multi-layer compositing."""
        if not dynamic_frames:
            raise ValueError("No dynamic frames provided")

        layout = prepare_layer_compositing(static_layer)
        composited_frames = [
            composite_frame_naive(static_layer, frame, layout) for frame in dynamic_frames
        ]

        clip = ImageSequenceClip(composited_frames, fps=fps)
        clip.write_videofile(output_path, codec=self._codec, audio=False)
        clip.close()
        return output_path
