"""
VideoPort: Interface for video encoding operations.
Dependencies: ViewportEntity
"""

from abc import ABC, abstractmethod
from typing import Any

from ...entities.viewport_entity import ViewportEntity


class VideoPort(ABC):
    """
    Port interface for video encoding.

    Adapters implementing this port:
    - moviepy_adapter.py (uses MoviePy library)
    """

    @abstractmethod
    def start_recording(
        self, output_path: str, viewport: ViewportEntity, codec: str = "libx264"
    ) -> None:
        """
        Initialize video recording session.

        Args:
            output_path: Destination file path (.mp4).
            viewport: Resolution and FPS settings.
            codec: Video codec to use.
        """
        pass

    @abstractmethod
    def add_frame(self, image: Any) -> None:
        """
        Add a frame to the video stream.

        Args:
            image: PIL.Image or numpy array to add.
        """
        pass

    @abstractmethod
    def add_frames(self, images: list[Any]) -> None:
        """
        Add multiple frames at once.

        Args:
            images: List of images to add in sequence.
        """
        pass

    @abstractmethod
    def save(self) -> str:
        """
        Finalize and save the video file.

        Returns:
            Path to the saved video file.
        """
        pass

    @abstractmethod
    def cancel(self) -> None:
        """Cancel recording and clean up resources."""
        pass

    @property
    @abstractmethod
    def frame_count(self) -> int:
        """Get current number of frames recorded."""
        pass

    @property
    @abstractmethod
    def duration(self) -> float:
        """Get current video duration in seconds."""
        pass

    @abstractmethod
    def get_progress(self) -> dict[str, Any]:
        """
        Get recording progress info.

        Returns:
            Dict with: frame_count, duration, estimated_size_mb
        """
        pass

    @abstractmethod
    def save_with_layers(
        self, static_layer: Any, dynamic_frames: list[Any], output_path: str, fps: int = 30
    ) -> str:
        """
        Save video using multi-layer compositing.

        Composites a static background layer with dynamic frame sequence.
        Used for optimized rendering where static UI is rendered once.

        Args:
            static_layer: Static UI layer (rendered once)
            dynamic_frames: List of dynamic frame images
            output_path: Output video file path
            fps: Frames per second

        Returns:
            Path to saved video file
        """
        pass
