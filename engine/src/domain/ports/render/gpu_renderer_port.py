"""
GPU Renderer Port Interface.
Separates Domain (DirectorEngine) from GPU Implementation (CuPy/FFmpeg).
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class GpuRendererPort(ABC):
    @abstractmethod
    def render(
        self,
        composited_frames: list[Any],  # Pre-composited PIL frames from Domain
        config: Any,  # RenderConfig
        progress_callback: Callable[[int, int], None] = None,
    ) -> str:
        """
        Encode pre-composited frames to video using GPU.

        GPU adapter only does encoding - all compositing is done in Domain.

        Args:
            composited_frames: List of pre-composited PIL Image frames.
            config: Render configuration (width, height, fps, output_path).
            progress_callback: Callback (frame, total).

        Returns:
            Path to output video.
        """
        pass
