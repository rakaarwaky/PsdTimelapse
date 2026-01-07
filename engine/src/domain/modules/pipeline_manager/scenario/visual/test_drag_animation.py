
import sys
import os
import unittest
from pathlib import Path

# Project root setup
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
from domain.modules.compositor import LayerRetrievalService

# Shared Fixtures
from domain.modules.pipeline_manager.scenario.fixtures.mock_layer_factory import MockGrid
from domain.modules.pipeline_manager.scenario.fixtures.mock_renderer_factory import MockRenderer
from domain.modules.pipeline_manager.scenario.fixtures.video_output_helper import VideoTestHelper
from domain.value_objects.resource.media_output_path_value import MediaOutputPath

import cv2
import numpy as np
from PIL import Image


class TestDragAnimation(unittest.TestCase):
    """Drag and Drop Animation Test."""

    def setUp(self):
        self.project_id = "test_project"
        self.media_path = MediaOutputPath(
            base_path=os.path.abspath(os.path.join(PROJECT_ROOT, "media")),
            project_id=self.project_id
        )
        self.output_dir = str(self.media_path.visual_test_dir / "drag_and_drop")
        os.makedirs(self.output_dir, exist_ok=True)

    def test_drag_sequence(self):
        print(f"\\n--- Starting Drag and Drop Test ---")
        
        # 1. World & Layers
        l1 = MockGrid("GreenRect", (100, 255, 100, 255), 100, 100, 300, 400, 0)
        l2 = MockGrid("YellowBox", (255, 255, 100, 255), 450, 100, 200, 200, 1)
        l3 = MockGrid("MagentaBox", (255, 100, 255, 255), 450, 350, 200, 150, 2)
        
        layers = [l1, l2, l3]
        scene = SceneEntity()
        for l in layers:
            scene.add_layer(l)
        world = WorldEntity(800, 600, scene)
        
        svc = LayerRetrievalService()
        svc.clear_cache()
        for l in layers:
            svc._layer_cache[l.id] = l._create_mock_image()
            
        # 2. Timeline
        timeline = TimelineEntity()
        timeline.add_action(Action(l1.id, ActionType.DRAG, 0.0, 3.0, Vector2(500, 300)))
        timeline.add_action(Action(l2.id, ActionType.DRAG, 3.5, 3.0, Vector2(550, 500)))
        timeline.add_action(Action(l3.id, ActionType.DRAG, 7.0, 3.0, Vector2(100, 100)))
    
        # 3. Engines
        anim_controller = AnimationController(800, 600)
        anim_controller.initialize_layers([l.id for l in layers])
        
        # Init states
        for i, (lid, pos) in enumerate([(l1.id, Vector2(250, 300)), 
                                      (l2.id, Vector2(550, 200)), 
                                      (l3.id, Vector2(550, 425))]):
            s = anim_controller.get_layer_state(lid)
            s.position = pos
            s.reveal_progress = 1.0
            s.visible = False
        
        viewport = ViewportEntity(800, 600, 30)
        compositor = FrameCompositor(world, viewport)
        
        compositor.layer_service.clear_cache()
        for l in layers:
            compositor.layer_service._layer_cache[l.id] = l._create_mock_image()
            
        mock_renderer = MockRenderer(os.path.dirname(__file__))
        
        fps = 30
        total_frames = int(11.0 * fps)
        
        # 4. Output Helper
        helper = VideoTestHelper(
            output_dir=self.output_dir,
            filename_base='drag_and_drop_test',
            fps=fps
        )
        
        print(f"Rendering {total_frames} frames...")
        
        for f in range(total_frames):
            time = f / fps
            # if f % 30 == 0: print(f"Frame {f}/{total_frames}")
            
            # A. Update Actions & Visibility
            for action in timeline.actions:
                if time >= action.start_time:
                     anim_controller.get_layer_state(action.layer_id).visible = True
                
                if time >= action.start_time and time <= (action.start_time + action.duration):
                    p = (time - action.start_time) / action.duration
                    anim_controller.update(action, p)
                elif time > (action.start_time + action.duration):
                     anim_controller.update(action, 1.0)
                     
            # B. Compose
            layer_states = {l.id: anim_controller.get_layer_state(l.id) for l in layers}
            
            img = compositor.compose_psd_content(
                layer_states,
                lambda lid: next((x for x in layers if x.id == lid), None)
            )
            
            # Render Cursor
            if anim_controller.cursor_position:
                class SimpleCursorState:
                    def __init__(self, pos): self.position = pos
                st = SimpleCursorState(anim_controller.cursor_position)
                mock_renderer.render_cursor([], st, img)
            
            # C. Save
            helper.write_frame(img, save_to_gif=(f % 2 == 0))
            
        helper.finalize()
        self.assertTrue(os.path.exists(self.output_dir))


if __name__ == "__main__":
    unittest.main()
