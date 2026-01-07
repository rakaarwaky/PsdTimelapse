"""
DirectorEngine: Central coordinator for the Timelapse Generation Engine.
Delegates heavy lifting to `strategies/` modules.
Migrated from render_manager to pipeline_manager.
"""

from __future__ import annotations

# New Service Imports
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ....entities.camera_entity import CameraEntity
from ....entities.layer_entity import LayerEntity
from ....entities.world_entity import WorldEntity
from ....ports.media.psd_port import PsdPort
from ....ports.media.video_port import VideoPort
from ....ports.render.compositor_port import CompositorPort
from ....ports.render.gpu_renderer_port import GpuRendererPort
from ....ports.render.renderer_port import RendererPort
from ....ports.store.file_system_port import FileSystemPort
from ....ports.system.logger_port import LoggerPort, NullLogger
from ....ports.system.notification_port import DomainEvent, NotificationPort, NullNotifier
from ....ports.system.random_port import RandomPort
from ....ports.system.time_port import TimePort
from ....value_objects.configs import EngineProgress, EngineState, RenderConfig
from ...script_director import SequencingStrategy, TimelineEntity, create_timeline
from ..rendering.cpu_strategy_module import CPURenderStrategy
from ..rendering.gpu_backend_module import GpuBackend
from ..rendering.gpu_strategy_module import GPURenderStrategy
from ..rendering.optimized_strategy_module import OptimizedRenderStrategy

if TYPE_CHECKING:
    from ....value_objects.resource.media_output_path_value import MediaOutputPath
    from ..rendering.media_output_service_module import MediaOutputService

# Legacy callback type (deprecated, use NotificationPort instead)
ProgressCallback = Callable[[EngineProgress], None]


@dataclass
class DirectorEngine:
    # === Required Ports ===
    psd_port: PsdPort | None = None
    renderer_port: RendererPort | None = None
    video_port: VideoPort | None = None
    gpu_renderer_port: GpuRendererPort | None = None
    ui_renderer_factory: Callable[[], Any] | None = None
    compositor_port: CompositorPort | None = None

    # === New Hexagonal Ports ===
    logger: LoggerPort = field(default_factory=NullLogger)
    notifier: NotificationPort = field(default_factory=NullNotifier)
    time_port: TimePort | None = None
    random_port: RandomPort | None = None
    file_system_port: FileSystemPort | None = None

    # === Services ===
    media_output_service: MediaOutputService | None = None

    # === Internal State ===
    state: EngineState = field(default=EngineState.IDLE, init=False)
    world: WorldEntity | None = field(default=None, init=False)
    camera: CameraEntity = field(default_factory=CameraEntity, init=False)
    timeline: TimelineEntity | None = field(default=None, init=False)
    media_path: MediaOutputPath | None = field(default=None, init=False)
    _progress_callback: ProgressCallback | None = field(default=None, init=False)

    def set_progress_callback(self, callback: ProgressCallback) -> None:
        """Legacy method. Prefer using NotificationPort.subscribe() instead."""
        self._progress_callback = callback

    def _emit(self, state: EngineState, frame: int, total: int, msg: str) -> None:
        """Emit progress via both NotificationPort and legacy callback."""
        self.state = state

        # New: Publish via NotificationPort
        self.notifier.publish(
            DomainEvent.RENDER_PROGRESS,
            {"state": state.value, "frame": frame, "total": total, "message": msg},
        )

        # Legacy: Call callback if set
        if self._progress_callback:
            self._progress_callback(EngineProgress(state, frame, total, msg))

    def load_project(self, psd_path: str) -> WorldEntity:
        if not self.psd_port:
            raise RuntimeError("PSD port missing")

        self.logger.info(f"Loading project: {psd_path}")
        self._emit(EngineState.LOADING, 0, 1, f"Loading {psd_path}")
        self.notifier.publish(DomainEvent.PROJECT_LOADED, {"path": psd_path})

        self.world = self.psd_port.load(psd_path)
        self.camera.pan_to(self.world.center)

        # Clear previous session media path
        self.media_path = None

        self.logger.info(f"Project loaded: {len(list(self.world.scene.iterate_visible()))} layers")
        self._emit(EngineState.IDLE, 1, 1, "Project loaded")
        return self.world

    def generate_timeline(
        self, strategy: SequencingStrategy = SequencingStrategy.STAGGERED
    ) -> TimelineEntity:
        if not self.world:
            raise RuntimeError("No world loaded")

        self.logger.info(f"Generating timeline with strategy: {strategy.value}")
        self._emit(EngineState.PLANNING, 0, 1, "Planning timeline")

        layers = list(self.world.scene.iterate_visible())
        # create_timeline returns TimelineEntity (not None)
        self.timeline = create_timeline(layers, strategy)

        self.logger.info(f"Timeline generated: {len(self.timeline.actions)} actions")
        self.notifier.publish(
            DomainEvent.TIMELINE_GENERATED,
            {"action_count": len(self.timeline.actions), "duration": self.timeline.total_duration},
        )
        self._emit(EngineState.IDLE, 1, 1, f"Timeline ready: {len(self.timeline.actions)}")
        return self.timeline

    def run(self, config: RenderConfig) -> str:
        self._ensure_media_path()
        if not self.world:
            raise RuntimeError("No world loaded")
        strategy = CPURenderStrategy(self.world)
        return self._execute_strategy(strategy, config)

    def run_optimized(self, config: RenderConfig) -> str:
        self._ensure_media_path()
        if not self.world:
            raise RuntimeError("No world loaded")
        strategy = OptimizedRenderStrategy(self.world)
        return self._execute_strategy(strategy, config)

    def run_gpu(self, config: RenderConfig) -> str:
        if not self.gpu_renderer_port:
            raise RuntimeError("GPU Port missing")
        if not self.world:
            raise RuntimeError("No world loaded")

        # Need UI Renderer
        if not self.ui_renderer_factory:
            raise RuntimeError("UI Factory missing")
        _ = self.ui_renderer_factory()

        strategy = GPURenderStrategy(self.world)
        if hasattr(strategy, "initialize"):
            # Create backend via factory or injection (Level 2 Orchestration responsibility)
            # Lazy import backend here (Orchestrator knows about backend implementation)
            backend = None
            if self.compositor_port:
                try:  # type: ignore[unused-ignore]
                    backend = GpuBackend(self.compositor_port)
                except ImportError:
                    self.logger.warning("GpuBackend not found")

            strategy.initialize(
                self.gpu_renderer_port,
                self.ui_renderer_factory,
                self.compositor_port,
                backend=backend,
            )

        self._ensure_media_path()
        return self._execute_strategy(strategy, config)

    def _ensure_media_path(self) -> None:
        """Initialize MediaOutputPath if service is available."""
        if self.media_output_service and not self.media_path:
            # Use PSD stem as project_id
            if self.world and hasattr(self.world, "source_path"):  # type: ignore[unused-ignore]
                project_id = os.path.splitext(os.path.basename(str(self.world.source_path)))[0]  # type: ignore[unused-ignore]
            else:
                project_id = "render_project"

            self.media_path = self.media_output_service.create_project(project_id)
            self.logger.info(f"Created media project: {self.media_path.project_root}")

    def _execute_strategy(self, strategy: Any, config: RenderConfig) -> str:
        if not all([self.timeline, self.video_port, self.ui_renderer_factory]):
            raise RuntimeError("Components missing")

        # Validate that ui_renderer_factory is callable
        if self.ui_renderer_factory is None:
            raise RuntimeError("UI Renderer Factory is missing")

        return strategy.execute(  # type: ignore[no-any-return]
            config,
            self.timeline,
            self.video_port,
            self.ui_renderer_factory(),
            self._find_layer,
            self._emit,
            self.camera,
            media_output=self.media_path,  # Pass new arg
        )

    def _find_layer(self, layer_id: str) -> LayerEntity | None:
        if not self.world:
            return None
        for layer in self.world.scene.iterate_visible():
            if layer.id == layer_id:
                return layer
        return None

    def get_coordinator(self) -> None:  # Helper
        return None  # Simplified

    def reset(self) -> None:
        self.state = EngineState.IDLE
        self.world = None
        self.camera = CameraEntity()
        self.timeline = None
