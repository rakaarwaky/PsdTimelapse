"""
RenderPipeline: Optimized rendering pipeline with caching and memory management.
Dependencies: FrameCompositor, AnimationController, VideoPort
Migrated from render_manager to pipeline_manager.
"""

from __future__ import annotations

import gc
import importlib.util
import time

try:
    importlib.util.find_spec("PIL")
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from ....entities.camera_entity import CameraEntity
from ....entities.viewport_entity import ViewportEntity
from ....entities.world_entity import WorldEntity
from ....ports.media.video_port import VideoPort
from ....ports.system.logger_port import LoggerPort, NullLogger
from ....ports.system.notification_port import DomainEvent, NotificationPort, NullNotifier
from ....ports.system.time_port import TimePort
from ....value_objects.configs.render_pipeline_config import PipelineConfig

# Domain Value Objects
from ....value_objects.pipeline.pipeline_state import (
    PipelineProgress,
    PipelineState,
    ProgressCallback,
)
from ....value_objects.resource.media_output_path_value import MediaOutputPath
from ...animator import AnimationController
from ...compositor import FrameCompositor
from ...script_director import TimelineEntity


class RenderPipeline:
    """Optimized rendering pipeline with memory management."""

    def __init__(  # noqa: PLR0913
        self,
        world: WorldEntity,
        timeline: TimelineEntity,
        video_port: VideoPort,
        config: PipelineConfig,
        logger: LoggerPort | None = None,
        notifier: NotificationPort | None = None,
        time_port: TimePort | None = None,
        media_output: MediaOutputPath | None = None,  # New injection
    ):
        self.world = world
        self.timeline = timeline
        self.video_port = video_port
        self.config = config

        self.logger = logger or NullLogger()
        self.notifier = notifier or NullNotifier()
        self.time_port = time_port
        self.media_output = media_output

        self.viewport = ViewportEntity(config.width, config.height, config.fps)
        self.camera = CameraEntity(  # type: ignore[call-arg]
            center_x=config.width / 2,
            center_y=config.height / 2,
            width=config.width,
            height=config.height,
        )

        self._state = PipelineState.IDLE
        self._cancelled = False
        self._progress_callback: ProgressCallback | None = None

    def set_progress_callback(self, callback: ProgressCallback) -> None:
        self._progress_callback = callback

    def cancel(self) -> None:
        self._cancelled = True
        if self._state == PipelineState.RENDERING:
            self.video_port.cancel()

    def run(self) -> str:
        """Execute the full render pipeline."""
        start_time = self._get_time()

        try:
            # Phase 1: Prepare
            self._start_pipeline(start_time)

            controller = AnimationController(
                self.timeline,  # type: ignore[arg-type]
                self.viewport.output_width,
                self.viewport.output_height,  # type: ignore[arg-type]
            )
            compositor = FrameCompositor(self.world, self.viewport)
            total_frames = int(self.timeline.total_duration * self.config.fps)

            # Phase 2: Render loop
            self._render_loop(controller, compositor, total_frames, start_time)

            if self._cancelled:
                return ""

            # Phase 3: Encode and finalize
            output_path = self._finalize_pipeline(compositor, total_frames, start_time)
            return output_path

        except Exception as e:
            self._handle_error(e)
            raise

    def get_estimated_duration(self) -> float:
        """Estimate total render time based on complexity."""
        frame_count = int(self.timeline.total_duration * self.config.fps)
        return frame_count * 0.1

    @property
    def state(self) -> PipelineState:
        return self._state

    # --- Private Helpers ---

    def _get_time(self) -> float:
        return self.time_port.now() if self.time_port else time.time()

    def _get_elapsed(self, start_time: float) -> float:
        if self.time_port:
            return self.time_port.elapsed_since(start_time)
        return time.time() - start_time

    def _start_pipeline(self, start_time: float) -> None:
        self.logger.info("Starting render pipeline")

        # Determine output path (MediaOutput or Config)
        output_path = (
            str(self.media_output.final_video_path)
            if self.media_output
            else self.config.output_path
        )

        self.notifier.publish(
            DomainEvent.RENDER_STARTED,
            {
                "output_path": output_path,
                "fps": self.config.fps,
                "resolution": f"{self.config.width}x{self.config.height}",
            },
        )
        self._emit_progress(PipelineState.PREPARING, 0, 1, "Initializing")

        self.video_port.start_recording(output_path, self.viewport, self.config.codec)
        self._state = PipelineState.RENDERING

    def _render_loop(
        self,
        controller: AnimationController,
        compositor: FrameCompositor,
        total_frames: int,
        start_time: float,
    ) -> None:
        for frame_num, timestamp in self.timeline.iterate_frames(self.config.fps):
            if self._cancelled:
                self.video_port.cancel()
                self._state = PipelineState.CANCELLED
                return

            # Reset frame state (velocity, etc)
            controller.reset_frame_state()

            # Update Layers
            active_actions = self.timeline.get_actions_at(timestamp)
            for action in active_actions:
                duration = action.end_time - action.start_time
                progress = (timestamp - action.start_time) / duration if duration > 0 else 1.0
                progress = max(0.0, min(1.0, progress))
                controller.update(action, progress)

            # Update Camera
            camera_action = self.timeline.get_camera_at(timestamp)
            if camera_action and hasattr(camera_action, "target"):
                self.camera.pan_to(camera_action.target)
            if camera_action and hasattr(camera_action, "zoom"):
                self.camera.zoom = camera_action.zoom

            frame = compositor.compose_frame(self.camera, controller)  # type: ignore[attr-defined]
            self.video_port.add_frame(frame)

            elapsed = self._get_elapsed(start_time)
            remaining = (elapsed / max(frame_num, 1)) * (total_frames - frame_num)

            self._emit_progress(
                PipelineState.RENDERING,
                frame_num,
                total_frames,
                f"Frame {frame_num}/{total_frames}",
                elapsed,
                remaining,
            )

            if frame_num > 0 and frame_num % self.config.batch_size == 0:
                gc.collect()

    def _finalize_pipeline(
        self, compositor: FrameCompositor, total_frames: int, start_time: float
    ) -> str:
        self._emit_progress(PipelineState.ENCODING, total_frames, total_frames, "Encoding video")
        output_path = self.video_port.save()

        compositor.clear_cache()  # type: ignore[attr-defined]
        gc.collect()

        elapsed = self._get_elapsed(start_time)
        self._state = PipelineState.COMPLETE

        self._emit_progress(
            PipelineState.COMPLETE,
            total_frames,
            total_frames,
            f"Complete in {elapsed:.1f}s",
            elapsed,
            0,
        )

        self.logger.info(f"Render complete: {output_path}")
        self.notifier.publish(
            DomainEvent.RENDER_COMPLETED,
            {"output_path": output_path, "total_frames": total_frames, "elapsed_seconds": elapsed},
        )
        return output_path

    def _handle_error(self, e: Exception) -> None:
        self._state = PipelineState.ERROR
        self.logger.error(f"Render failed: {e!s}", exception=e)
        self.notifier.publish(
            DomainEvent.ERROR_OCCURRED, {"error": str(e), "phase": self._state.value}
        )
        self._emit_progress(PipelineState.ERROR, 0, 0, str(e))

    def _emit_progress(  # noqa: PLR0913
        self,
        state: PipelineState,
        current: int,
        total: int,
        message: str,
        elapsed: float = 0,
        remaining: float = 0,
    ) -> None:
        self._state = state

        progress_data = {
            "state": state.value,
            "current_frame": current,
            "total_frames": total,
            "message": message,
            "elapsed_seconds": elapsed,
            "estimated_remaining": remaining,
            "percent": (current / total * 100) if total > 0 else 0,
        }
        self.notifier.publish(DomainEvent.RENDER_PROGRESS, progress_data)

        if self._progress_callback:
            self._progress_callback(
                PipelineProgress(
                    state=state,
                    current_frame=current,
                    total_frames=total,
                    current_phase=state.value,
                    message=message,
                    elapsed_seconds=elapsed,
                    estimated_remaining=remaining,
                )
            )
