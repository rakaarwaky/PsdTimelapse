"""
ProducerEngine - Central coordinator for Timelapse Generation.

This is the high-level API that coordinates all domain modules:
- Script Director: Pre-production planning
- Layout Manager: Scene blocking & coordinates
- Animator: Motion & timing
- Compositor: Layer merging
- Pipeline Manager: Pipeline control

Usage:
    from domain.core import ProducerEngine
    engine = ProducerEngine()
    engine.load_psd("design.psd")
    engine.generate_video("output.mp4")
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

# Import entities
from ..entities.world_entity import WorldEntity
from ..modules.animator import AnimationController
from ..modules.compositor import FrameCompositor, LayerCache
from ..modules.layout_manager import CoordinateMapper

# Import from role modules
from ..modules.pipeline_manager import (
    DirectorEngine,
    EngineProgress,
    EngineState,
    RenderConfig,
)
from ..modules.script_director import (
    ActionType,
    SequencingStrategy,
    TimelineEntity,
)

# Import ports
from ..ports.media.psd_port import PsdPort
from ..ports.media.video_port import VideoPort
from ..ports.render.compositor_port import CompositorPort
from ..ports.render.gpu_renderer_port import GpuRendererPort
from ..ports.render.renderer_port import RendererPort
from ..value_objects.configs import ProducerConfig


class ProducerEngine:
    """
    Central orchestrator that coordinates all 5-role modules.

    Provides a high-level API for the timelapse generation workflow.
    """

    def __init__(  # noqa: PLR0913
        self,
        psd_port: PsdPort | None = None,
        renderer_port: RendererPort | None = None,
        video_port: VideoPort | None = None,
        # Factory Injection
        ui_renderer_factory: Callable[[], Any] | None = None,
        gpu_renderer_port: GpuRendererPort | None = None,
        compositor_port: CompositorPort | None = None,
    ):
        """
        Initialize orchestrator with optional port implementations.

        Args:
            psd_port: PSD parser implementation
            renderer_port: Frame renderer implementation
            video_port: Video encoder implementation
            ui_renderer_factory: Factory for creating UI Renderer
            gpu_renderer_port: Port for GPU Rendering Adapter
            compositor_port: Port for GPU blend operations (Hexagonal DI)
        """
        self._engine = DirectorEngine(
            psd_port=psd_port,
            renderer_port=renderer_port,
            video_port=video_port,
            ui_renderer_factory=ui_renderer_factory,
            gpu_renderer_port=gpu_renderer_port,
            compositor_port=compositor_port,
        )

    def load_psd(self, psd_path: str) -> WorldEntity:
        """Load a PSD file and return the world entity."""
        return self._engine.load_project(psd_path)

    # Alias for adapter compatibility
    def load_project(self, psd_path: str) -> WorldEntity:
        return self.load_psd(psd_path)

    def generate_timeline(
        self, strategy: SequencingStrategy = SequencingStrategy.STAGGERED
    ) -> TimelineEntity:
        """Generate animation timeline."""
        return self._engine.generate_timeline(strategy)

    def set_progress_callback(self, callback: Callable[[EngineProgress], None]) -> None:
        """Set callback for progress updates."""
        self._engine.set_progress_callback(callback)

    def run(self, config: RenderConfig) -> str:
        """
        Execute render with directory RenderConfig (Adapter compatibility).
        """
        # Auto-select strategy based on internal logic or config hooks if needed
        # For now, default to optimized CPU unless GPU is explicitly requested in some way
        if config.use_gpu:
            return self._engine.run_gpu(config)
        return self._engine.run_optimized(config)

    def run_optimized(self, config: RenderConfig) -> str:
        """Delegate to director engine (CPU)."""
        return self._engine.run_optimized(config)

    def run_gpu(self, config: RenderConfig) -> str:
        """Delegate to director engine (GPU)."""
        return self._engine.run_gpu(config)

    def render(self, config: ProducerConfig) -> str:
        """
        Execute full render pipeline.

        Args:
            config: ProducerConfig configuration

        Returns:
            Path to output video file
        """
        render_config = RenderConfig(
            output_path=config.output_path,
            width=config.width,
            height=config.height,
            fps=config.fps,
            strategy=config.strategy,
            # use_gpu is used for dispatch here, not in RenderConfig
        )
        if config.use_gpu:
            return self._engine.run_gpu(render_config)
        return self._engine.run_optimized(render_config)

    def generate_video(  # noqa: PLR0913
        self,
        psd_path: str,
        output_path: str = "./output.mp4",
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        strategy: SequencingStrategy = SequencingStrategy.STAGGERED,
        use_gpu: bool = False,  # Added use_gpu
        progress_callback: Callable[[EngineProgress], None] | None = None,
    ) -> str:
        """
        High-level API: Generate video from PSD in one call.

        Args:
            psd_path: Path to PSD file
            output_path: Output video path
            width: Video width
            height: Video height
            fps: Frames per second
            strategy: Animation sequencing strategy
            use_gpu: Whether to use GPU acceleration
            progress_callback: Optional progress callback

        Returns:
            Path to output video file
        """
        # Load PSD
        self.load_psd(psd_path)

        # Generate timeline
        self.generate_timeline(strategy)

        # Set callback if provided
        if progress_callback:
            self.set_progress_callback(progress_callback)

        # Render
        config = ProducerConfig(
            output_path=output_path,
            width=width,
            height=height,
            fps=fps,
            strategy=strategy,
            use_gpu=use_gpu,
        )
        return self.render(config)

    @property
    def state(self) -> EngineState:
        """Get current engine state."""
        return self._engine.state

    @property
    def world(self) -> WorldEntity | None:
        """Get loaded world entity."""
        return self._engine.world


# Convenience exports
__all__ = [
    "ActionType",
    "AnimationController",
    "CoordinateMapper",
    "DirectorEngine",
    "EngineProgress",
    "EngineState",
    "FrameCompositor",
    "LayerCache",
    "ProducerConfig",
    "ProducerEngine",
    "RenderConfig",
    "SequencingStrategy",
    "TimelineEntity",
]
