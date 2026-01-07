
import sys
import os
import shutil
import unittest
from pathlib import Path

# Project root setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SRC_ROOT = os.path.join(PROJECT_ROOT, 'src')
if SRC_ROOT not in sys.path:
    sys.path.append(SRC_ROOT)

from domain.entities.world_entity import WorldEntity, SceneEntity  # noqa: E402
from domain.entities.layer_entity import LayerEntity  # noqa: E402
from domain.entities.viewport_entity import ViewportEntity  # noqa: E402
from domain.value_objects.geometry.vector_value import Vector2  # noqa: E402
from domain.value_objects.geometry.rect_value import Rect  # noqa: E402
from domain.modules.script_director import TimelineEntity as Timeline, Action, ActionType  # noqa: E402
from domain.modules.animator import AnimationController  # noqa: E402

from domain.modules.compositor import FrameCompositor  # noqa: E402
from domain.modules.compositor import LayerRetrievalService  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402
import cv2  # noqa: E402
import numpy as np  # noqa: E402

# Shared Fixtures
from domain.modules.pipeline_manager.scenario.fixtures.mock_layer_factory import MockGrid  # noqa: E402
from domain.modules.pipeline_manager.scenario.fixtures.mock_renderer_factory import MockRenderer  # noqa: E402
from domain.modules.pipeline_manager.scenario.fixtures.video_output_helper import VideoTestHelper  # noqa: E402
from domain.value_objects.resource.media_output_path_value import MediaOutputPath  # noqa: E402


class TestBrushMultiObject(unittest.TestCase):
    """Brush Reveal Test: Multi-Object."""

    def setUp(self):
        self.project_id = "test_project"
        self.media_path = MediaOutputPath(
            base_path=os.path.abspath(os.path.join(PROJECT_ROOT, "media")),
            project_id=self.project_id
        )
        self.output_dir = str(self.media_path.visual_test_dir / "brush_multi")
        os.makedirs(self.output_dir, exist_ok=True)

    def test_multi_object_brush(self):
        print("--- Starting Brush Reveal Test: Multi-Object ---")
        
        # 1. World & Layers
        l1 = MockGrid("GreenRect", (100, 255, 100, 255), 100, 100, 300, 400, 0)
        l2 = MockGrid("YellowBox", (255, 255, 100, 255), 450, 100, 200, 200, 1)
        l3 = MockGrid("MagentaBox", (255, 100, 255, 255), 450, 350, 200, 150, 2)
        
        layers = [l1, l2, l3]
        scene = SceneEntity()
        for l in layers:
            scene.add_layer(l)
        world = WorldEntity(800, 600, scene)
        
        # 2. Timeline
        timeline = Timeline()
        
        # Brush Action 1: Green Rect (0s -> 3s)
        a1 = Action(l1.id, ActionType.BRUSH, 0.0, 3.0, Vector2(0,0))
        timeline.add_action(a1)
        
        # Brush Action 2: Yellow Box (3s -> 5s)
        a2 = Action(l2.id, ActionType.BRUSH, 3.0, 2.0, Vector2(0,0))
        timeline.add_action(a2)
        
        # Brush Action 3: Magenta Box (5s -> 7s)
        a3 = Action(l3.id, ActionType.BRUSH, 5.0, 2.0, Vector2(0,0))
        timeline.add_action(a3)
    
        print("Timeline Planned.")
        
        # 3. Engines (Refactored)
        anim_controller = AnimationController(800, 600)
        anim_controller.initialize_layers([l.id for l in layers])
        
        # Manually set positions
        anim_controller.get_layer_state(l1.id).position = Vector2(250, 300)
        anim_controller.get_layer_state(l2.id).position = Vector2(550, 200)
        anim_controller.get_layer_state(l3.id).position = Vector2(550, 425)
        
        viewport = ViewportEntity(800, 600, 30)
        compositor = FrameCompositor(world, viewport)
        
        # Mock Image Cache population
        compositor.layer_service.clear_cache()
        for l in layers:
            compositor.layer_service._layer_cache[l.id] = l._create_mock_image()
            
        mock_renderer = MockRenderer()
        
        # 4. Render Loop
        fps = 30
        total_frames = int(7.0 * fps) # Approx
        
        helper = VideoTestHelper(
            output_dir=self.output_dir,
            filename_base='brush_reveal_test_001',
            fps=fps
        )
        
        print(f"Rendering {total_frames} frames...")
        
        for f in range(total_frames):
            time = f / fps
            # if f % 30 == 0: print(f"Frame {f}/{total_frames}")
            
            # A. Get Actions (mock loop)
            active_actions = []
            for action in [a1, a2, a3]:
                if time >= action.start_time and time <= (action.start_time + action.duration):
                    p = (time - action.start_time) / action.duration
                    active_actions.append((action, p))
                elif time > (action.start_time + action.duration):
                    active_actions.append((action, 1.0))

            for act, prog in active_actions:
                anim_controller.update(act, prog)
                
            # C. Get States
            layer_states = {
                l.id: anim_controller.get_layer_state(l.id)
                for l in layers
            }
            
            # D. Compose
            img = compositor.compose_psd_content(
                layer_states,
                lambda lid: next((x for x in layers if x.id == lid), None)
            )
            
            helper.write_frame(img, save_to_gif=(f % 2 == 0))
            
        helper.finalize()
        self.assertTrue(os.path.exists(self.output_dir))


if __name__ == "__main__":
    unittest.main()
