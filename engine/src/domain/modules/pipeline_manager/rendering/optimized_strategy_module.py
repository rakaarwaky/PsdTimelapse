"""
Optimized Render Strategy: Multi-layer composition with static UI caching.
Migrated from render_manager to pipeline_manager.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ....entities.camera_entity import CameraEntity
from ....entities.layer_entity import LayerEntity
from ....entities.viewport_entity import ViewportEntity
from ....entities.world_entity import WorldEntity
from ....ports.media.video_port import VideoPort
from ....value_objects.configs import EngineState, RenderConfig
from ...animator import AnimationController
from ...compositor import FrameCompositor
from ...script_director import TimelineEntity

# Pipeline dependencies
from ..orchestrator.pipeline_manager_module import CompositeConfig, PipelineManager
from ..ui.cursor_overlay_module import CursorOverlay
from ..ui.ui_helper_module import build_ui_layer_list

if TYPE_CHECKING:
    from ....value_objects.resource.media_output_path_value import MediaOutputPath


class OptimizedRenderStrategy:
    def __init__(self, world: WorldEntity):
        self.world = world

    def execute(
        self,
        config: "RenderConfig",
        timeline: "TimelineEntity",
        video_port: "VideoPort",
        ui_renderer: Any,
        find_layer: Callable[[str], "LayerEntity | None"],
        progress_callback: Callable[["EngineState", int, int, str], None],
        camera: "CameraEntity",
        media_output: "MediaOutputPath | None" = None,  # New arg
    ) -> str:
        # 1. Setup Viewport & Video
        viewport = ViewportEntity(config.width, config.height, config.fps)

        # Determine output path
        output_path = str(media_output.final_video_path) if media_output else config.output_path

        video_port.start_recording(output_path, viewport)

        # 2. Setup Animator & Init Layers
        anim_controller = AnimationController(config.width, config.height)
        layer_ids = [layer.id for layer in self.world.scene.iterate_visible()]
        anim_controller.initialize_layers(layer_ids)

        # 3. Setup Compositor
        # Inject Dependencies (Orchestration Wiring)
        try:
            from ...animator.generators.mask_generator_module import (
                create_brush_tool_for_layer,
                generate_reveal_mask,
            )
            from ...animator.motion.path_generator_module import generate_brush_path
        except ImportError:
            create_brush_tool_for_layer = None  # type: ignore
            generate_reveal_mask = None  # type: ignore
            generate_brush_path = None  # type: ignore

        draw_brush_cursor_ui = None
        get_brush_cursor_position = None

        compositor = FrameCompositor(
            self.world,
            viewport,
            mask_generator_fn=generate_reveal_mask,
            brush_tool_factory_fn=create_brush_tool_for_layer,
            path_generator_fn=generate_brush_path,
            get_brush_cursor_pos_fn=get_brush_cursor_position,
            draw_brush_cursor_ui_fn=draw_brush_cursor_ui,
        )

        total_frames = int(timeline.total_duration * config.fps)

        # 4. Render Static UI (Optimization)
        progress_callback(EngineState.RENDERING, 0, total_frames, "Rendering static UI...")

        layer_list = build_ui_layer_list(self.world)
        static_ui = ui_renderer.render_static_ui(layer_list)

        # 5. Setup Pipeline Manager
        pipeline_cfg = CompositeConfig(width=config.width, height=config.height, fps=config.fps)
        pipeline = PipelineManager(pipeline_cfg)

        cursor_overlay = CursorOverlay(icon_size=32)

        # 6. Render Loop (Pipeline)
        def _emit_progress_adapter(current, total):
            progress_callback(EngineState.RENDERING, current, total, f"Frame {current}/{total}")

        for frame_num, frame in pipeline.iterate_frames(
            static_ui=static_ui,
            timeline=timeline,
            anim_controller=anim_controller,
            compositor=compositor,
            find_layer_fn=find_layer,
            progress_callback=_emit_progress_adapter,
            cursor_overlay=cursor_overlay,
        ):
            # Camera Update
            timestamp = frame_num / config.fps
            cam_action = timeline.get_camera_at(timestamp)
            if cam_action:
                t = (timestamp - cam_action.start_time) / cam_action.duration
                camera.lerp_to(cam_action.end_position, cam_action.end_zoom, t)

            video_port.add_frame(frame)

        # 7. Finalize
        progress_callback(EngineState.SAVING, total_frames, total_frames, "Saving video")
        output_path = video_port.save()

        progress_callback(EngineState.COMPLETE, total_frames, total_frames, "Complete!")
        return output_path
