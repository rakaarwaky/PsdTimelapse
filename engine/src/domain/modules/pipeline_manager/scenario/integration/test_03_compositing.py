
import sys
import os
import shutil
import unittest
from pathlib import Path

# Project Root Setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SRC_ROOT = os.path.join(PROJECT_ROOT, 'src')
if SRC_ROOT not in sys.path:
    sys.path.append(SRC_ROOT)

from domain.entities.world_entity import WorldEntity, SceneEntity
from domain.entities.layer_entity import LayerEntity
from domain.entities.viewport_entity import ViewportEntity
from domain.value_objects import Vector2, Rect
from domain.modules.script_director import TimelineEntity, Action, ActionType
from domain.modules.animator import AnimationController
from domain.modules.compositor import FrameCompositor

# Adapters
from adapters.driven.psd_modeler.psdtools_parser_adapter import PsdToolsAdapter
from adapters.driven.ui_modeler.pillow_modeler_adapter import UIRendererCore
from adapters.driven.ui_modeler.pillow_constants_adapter import VIDEO_WIDTH, VIDEO_HEIGHT

from domain.modules.pipeline_manager import PipelineManager, CompositeConfig
from domain.modules.pipeline_manager.scenario.fixtures.mock_renderer_factory import DynamicCursorRenderer
from domain.modules.pipeline_manager.scenario.fixtures.video_output_helper import VideoTestHelper

from PIL import Image, ImageDraw
import cv2
import numpy as np

# Use MediaOutputPath logic
from domain.value_objects.resource.media_output_path_value import MediaOutputPath


class TestCompositing(unittest.TestCase):
    """Integration Test: Final Compositing with Real PSD."""

    def setUp(self):
        self.project_id = "test_integration_compositing"
        self.media_path = MediaOutputPath(
            base_path=os.path.abspath(os.path.join(PROJECT_ROOT, "media")),
            project_id="test_project"
        )
        self.output_dir = str(self.media_path.integration_test_dir / "compositing")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Resolve PSD Path
        self.psd_path = os.path.join(SRC_ROOT, 'assets/Psd/test.psd')

    def test_final_render(self):
        print(f"\\n--- Starting Final Render Test (Real PSD Integration) ---")
        
        if not os.path.exists(self.psd_path):
            self.fail(f"Error: PSD not found at {self.psd_path}")

        print(f"Loading PSD: {self.psd_path}")
        psd_adapter = PsdToolsAdapter()
        world = psd_adapter.load(self.psd_path)
        
        all_layers_list = list(world.scene.iterate_all())
        if len(all_layers_list) < 4:
            self.fail("Error: Expected at least 4 layers in PSD.")

        layer_hoodie = all_layers_list[0]
        layer_arm_right = all_layers_list[1]
        layer_arm_left = all_layers_list[2]
        layer_logo = all_layers_list[3]
        
        print(f"Hoodie: {layer_hoodie.name}, Logo: {layer_logo.name}")

        # Timeline
        timeline = TimelineEntity()
        
        # 1. DRAG Hoodie
        start_pos = layer_hoodie.position
        target_pos = Vector2(start_pos.x + 100, start_pos.y)
        
        timeline.add_action(Action(layer_hoodie.id, ActionType.DRAG, 0.5, 2.0, target_pos))
        
        # 2. BRUSH Reveals
        for i, l in enumerate([layer_arm_right, layer_arm_left, layer_logo]):
            timeline.add_action(Action(l.id, ActionType.BRUSH, 3.0 + (i * 0.5), 2.0, Vector2(0,0)))
        
        # 3. Engines
        anim_controller = AnimationController(world.width, world.height)
        anim_controller.initialize_layers(list(world.scene.iterate_all()))
        
        viewport = ViewportEntity(world.width, world.height, 30)
        compositor = FrameCompositor(world, viewport)
        
        for l in world.scene.iterate_all():
            if l.image_data:
                compositor.layer_service._layer_cache[l.id] = l.image_data
            else:
                 w = int(l.bounds.width) if l.bounds.width > 0 else 1
                 h = int(l.bounds.height) if l.bounds.height > 0 else 1
                 compositor.layer_service._layer_cache[l.id] = Image.new('RGBA', (w, h), (0,0,0,0))

        dynamic_cursor_renderer = DynamicCursorRenderer()
        app_ui_renderer = UIRendererCore()
        
        fps = 30
        total_frames = int(7.0 * fps)
        
        helper = VideoTestHelper(
            output_dir=self.output_dir,
            filename_base='final_render_test',
            fps=fps,
            width=VIDEO_WIDTH,
            height=VIDEO_HEIGHT
        )
        
        print(f"Rendering {total_frames} frames...")
        
        # Helper for UI
        ui_layer_data = [
            {"name": l.name, "visible": l.visible, "locked": False, "id": l.id}
            for l in world.scene.iterate_all()
        ]

        # Static UI
        static_ui_frame = app_ui_renderer.render_frame(
            canvas_content=Image.new('RGBA', (world.width, world.height), (0,0,0,0)), 
            layers=ui_layer_data
        )

        pipeline_cfg = CompositeConfig(width=VIDEO_WIDTH, height=VIDEO_HEIGHT)
        # Inject Backend
        from adapters.driven.renderers.pillow_backend import PillowBackend
        canvas_backend = PillowBackend()
        pipeline_manager = PipelineManager(pipeline_cfg, backend=canvas_backend)

        # Render Loop
        for frame_num in range(total_frames):
            time = frame_num / fps
            
            # 1. Update Animation
            for action in timeline.actions:
                if time >= action.start_time:
                    if time <= (action.start_time + action.duration):
                        p = (time - action.start_time) / action.duration
                        anim_controller.update(action, p)
                    elif time > (action.start_time + action.duration):
                         anim_controller.update(action, 1.0)
                         
            # 2. Get States & Compose Content
            layer_states = {l.id: anim_controller.get_layer_state(l.id) for l in world.scene.iterate_all()}
            
            content_frame = compositor.compose_psd_content(
                layer_states=layer_states,
                find_layer_func=lambda lid: next((x for x in world.scene.iterate_all() if x.id == lid), None)
            )
            
            # 3. Dynamic Cursor
            if anim_controller.cursor_position:
                class SimpleCursorState:
                    def __init__(self, pos): self.position = pos
                st = SimpleCursorState(anim_controller.cursor_position)
                dynamic_cursor_renderer.render_cursor(ui_layer_data, st, content_frame)

            # 4. Final Composite
            final_frame = pipeline_manager.compose_frame(
                static_ui=static_ui_frame,
                psd_content=content_frame
            )
            
            helper.write_frame(final_frame, save_to_gif=False)
            # if frame_num % 30 == 0:
            #     print(f"Frame {frame_num}/{total_frames}")

        helper.finalize()
        print("Video saved.")
        self.assertTrue(os.path.exists(self.output_dir))


if __name__ == "__main__":
    unittest.main()
