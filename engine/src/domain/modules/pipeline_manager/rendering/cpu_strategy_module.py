from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ....entities.camera_entity import CameraEntity
from ....entities.layer_entity import LayerEntity
from ....entities.viewport_entity import ViewportEntity
from ....entities.world_entity import WorldEntity
from ....ports.media.video_port import VideoPort
from ....value_objects.configs import EngineState, RenderConfig
from ...script_director import TimelineEntity

# Factory type aliases (blind)
AnimControllerFactory = Callable[[int, int], Any]
CompositorFactory = Callable[[Any, Any], Any]

if TYPE_CHECKING:
    from ....entities.timeline_entity import TimelineEntity
    from ....value_objects.resource.media_output_path_value import MediaOutputPath


class CPURenderStrategy:
    def __init__(self, world: WorldEntity):
        self.world = world

    def execute(
        self,
        config: RenderConfig,
        timeline: TimelineEntity,
        video_port: VideoPort,
        ui_renderer: Any,
        find_layer_fn: Callable[[str], LayerEntity | None],
        progress_callback: Callable[[EngineState, int, int, str], None],
        camera: CameraEntity,
        media_output: MediaOutputPath | None = None,
        anim_controller_factory: AnimControllerFactory | None = None,
        compositor_factory: CompositorFactory | None = None,
    ) -> str:
        # 1. Setup Viewport & Video
        viewport = ViewportEntity(config.width, config.height, config.fps)

        # Determine output path
        output_path = str(media_output.final_video_path) if media_output else config.output_path

        video_port.start_recording(output_path, viewport)

        # 2. Setup Animator (New Stateless API)
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

            # Inject Dependencies (Orchestration Wiring)
            try:
                from ...animator.generators.mask_generator_module import (
                    create_brush_tool_for_layer,
                    generate_reveal_mask,
                )
                from ...animator.motion.path_generator_module import generate_brush_path
            except ImportError:
                # Should not happen in production, but graceful degradation for strict isolation testing
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
        progress_callback(EngineState.RENDERING, 0, total_frames, "Starting render")

        # 4. Prepare UI List
        # layer_list = build_ui_layer_list(self.world) # Removed unused
        if ui_renderer:  # Basic check to silence linter if needed
            pass

        # 5. Render Loop
        for frame_num, timestamp in timeline.iterate_frames(config.fps):
            # Update Camera
            cam_action = timeline.get_camera_at(timestamp)
            if cam_action:
                t = (timestamp - cam_action.start_time) / cam_action.duration
                camera.lerp_to(cam_action.end_position, cam_action.end_zoom, t)

            # Update Animation State
            current_actions = timeline.get_actions_at(timestamp)
            for action in current_actions:
                if action.duration > 0:
                    progress = (timestamp - action.start_time) / action.duration
                    progress = max(0.0, min(1.0, progress))
                else:
                    progress = 1.0
                anim_controller.update(action, progress)

            # Retrieve States
            layer_states = {}
            for lid in layer_ids:
                st = anim_controller.get_layer_state(lid)
                if st:
                    layer_states[lid] = st

            # Compose Frame
            frame_image = compositor.compose_psd_content(layer_states, find_layer_fn)

            video_port.add_frame(frame_image)

            if frame_num % 10 == 0:
                progress_callback(
                    EngineState.RENDERING,
                    frame_num,
                    total_frames,
                    f"Frame {frame_num}/{total_frames}",
                )

        # 6. Finalize
        progress_callback(EngineState.SAVING, total_frames, total_frames, "Saving video")
        output_path = video_port.save()

        progress_callback(EngineState.COMPLETE, total_frames, total_frames, "Complete!")
        return output_path
