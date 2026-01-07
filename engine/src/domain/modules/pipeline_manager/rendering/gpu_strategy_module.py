"""
GPURenderStrategy: Handles GPU-accelerated rendering pipeline.
Migrated from render_manager to pipeline_manager.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ....entities.camera_entity import CameraEntity
from ....entities.layer_entity import LayerEntity
from ....entities.viewport_entity import ViewportEntity
from ....entities.world_entity import WorldEntity
from ....ports.media.video_port import VideoPort
from ....ports.render.compositor_port import CompositorPort
from ....ports.render.gpu_renderer_port import GpuRendererPort
from ....value_objects.configs import EngineState, RenderConfig
from ...script_director import TimelineEntity
from ..orchestrator.pipeline_manager_module import CompositeConfig, PipelineManager
from ..ui.cursor_overlay_module import CursorOverlay
from ..ui.ui_helper_module import build_ui_layer_list

# Factory type aliases (blind)
AnimControllerFactory = Callable[[int, int], Any]
CompositorFactory = Callable[[Any, Any], Any]


class GPURenderStrategy:
    def __init__(self, world: WorldEntity):
        self.world = world
        self.gpu_port: GpuRendererPort | None = None
        self.ui_renderer_factory: Callable[[], Any] | None = None
        self.compositor_port: CompositorPort | None = None
        self.backend: Any = None

    def initialize(
        self,
        gpu_port: GpuRendererPort,
        ui_renderer_factory: Callable[[], Any],
        compositor: CompositorPort | None = None,
        backend: Any = None,
    ) -> None:
        self.gpu_port = gpu_port
        self.ui_renderer_factory = ui_renderer_factory
        self.compositor_port = compositor
        self.backend = backend

    def execute(
        self,
        config: RenderConfig,
        timeline: TimelineEntity,
        video_port: VideoPort,
        ui_renderer: Any,  # Passed from Engine
        find_layer_fn: Callable[[str], LayerEntity | None],
        progress_callback: Callable[[EngineState, int, int, str], None],
        camera: CameraEntity,
        anim_controller_factory: AnimControllerFactory | None = None,
        compositor_factory: CompositorFactory | None = None,
    ) -> str:
        if not self.gpu_port:
            raise RuntimeError("GPU Port not initialized on GPURenderStrategy")

        # 1. Setup Viewport & Video
        viewport = ViewportEntity(config.width, config.height, config.fps)
        video_port.start_recording(config.output_path, viewport)

        # 2. Setup Animator & Init Layers
        if anim_controller_factory:
            anim_controller = anim_controller_factory(config.width, config.height)
        else:
            from ...animator import AnimationController

            anim_controller = AnimationController(config.width, config.height)

        layer_ids = [layer.id for layer in self.world.scene.iterate_visible()]
        anim_controller.initialize_layers(layer_ids)

        # 3. Setup Compositor
        if compositor_factory:
            compositor = compositor_factory(self.world, viewport)
        else:
            from ...compositor import FrameCompositor

            compositor = FrameCompositor(self.world, viewport)

        total_frames = int(timeline.total_duration * config.fps)

        # 4. Render Static UI
        progress_callback(EngineState.RENDERING, 0, total_frames, "Rendering static UI (GPU)...")

        layer_list = build_ui_layer_list(self.world)
        static_ui = ui_renderer.render_static_ui(layer_list)

        # 5. Setup Pipeline Manager with GPU Backend
        backend = self.backend
        if not backend and self.compositor_port:
            pass  # Blind logic compliance

        if not backend:
            print("Warning: GPU Backend not injected, falling back to CPU logic in PipelineManager")

        pipeline_cfg = CompositeConfig(width=config.width, height=config.height, fps=config.fps)
        pipeline = PipelineManager(pipeline_cfg, backend=backend)

        cursor_overlay = CursorOverlay(icon_size=32)

        # 6. Render Loop
        def _emit_progress_adapter(current: int, total: int) -> None:
            progress_callback(EngineState.RENDERING, current, total, f"GPU Frame {current}/{total}")

        for frame_num, frame in pipeline.iterate_frames(
            static_ui=static_ui,
            timeline=timeline,
            anim_controller=anim_controller,
            compositor=compositor,
            find_layer_fn=find_layer_fn,
            progress_callback=_emit_progress_adapter,
            cursor_overlay=cursor_overlay,
        ):
            # Camera Update
            timestamp = frame_num / config.fps
            cam_action = timeline.get_camera_at(timestamp)
            if cam_action:
                t = (timestamp - cam_action.start_time) / cam_action.duration
                camera.lerp_to(cam_action.end_position, cam_action.end_zoom, t)

            # Add frame to video port
            if hasattr(frame, "get"):  # CuPy/NumPy
                frame = frame.get()  # To NumPy

            video_port.add_frame(frame)

        # 7. Finalize
        progress_callback(EngineState.SAVING, total_frames, total_frames, "Saving video...")
        output_path = video_port.save()

        progress_callback(EngineState.COMPLETE, total_frames, total_frames, "Complete!")
        return output_path
