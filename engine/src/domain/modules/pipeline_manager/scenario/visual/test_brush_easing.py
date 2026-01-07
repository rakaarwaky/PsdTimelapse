
import sys
import os
import unittest
from pathlib import Path

# Project root setup (handled by PYTHONPATH in VS Code, but good for standalone)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SRC_ROOT = os.path.join(PROJECT_ROOT, 'src')
if SRC_ROOT not in sys.path:
    sys.path.append(SRC_ROOT)

from domain.entities.world_entity import WorldEntity, SceneEntity
from domain.entities.layer_entity import LayerEntity
from domain.entities.viewport_entity import ViewportEntity
from domain.value_objects import Vector2, Rect, EasingCurve, EasingType
from domain.modules.script_director import TimelineEntity, Action, ActionType
from domain.modules.animator import AnimationController
from domain.modules.compositor import FrameCompositor

from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

# Shared Fixtures
from domain.modules.pipeline_manager.scenario.fixtures.mock_layer_factory import MockGrid
from domain.modules.pipeline_manager.scenario.fixtures.mock_renderer_factory import MockRenderer
from domain.modules.pipeline_manager.scenario.fixtures.video_output_helper import VideoTestHelper

# Local Config
from domain.modules.pipeline_manager.scenario.visual.brush_scenes_config import SCENES, POSITIONS, SCENE_DURATION, TRANSITION_GAP
from domain.value_objects.resource.media_output_path_value import MediaOutputPath


class TestBrushEasing(unittest.TestCase):
    """Brush Reveal Test 002: Extended Easing Showcase."""

    def setUp(self):
        self.project_id = "test_project"
        self.media_path = MediaOutputPath(
            base_path=os.path.abspath(os.path.join(PROJECT_ROOT, "media")),
            project_id=self.project_id
        )
        self.output_dir = str(self.media_path.visual_test_dir / "brush_easing")
        os.makedirs(self.output_dir, exist_ok=True)

    def test_extended_easing(self):
        print(f"\\n--- Brush Reveal Test 002: Extended Easing Showcase ---")
        print(f"Scenes: {len(SCENES)}, Total Easings: {len(SCENES) * 3}")
        
        total_duration = len(SCENES) * (SCENE_DURATION + TRANSITION_GAP)
        fps = 30
        total_frames = int(total_duration * fps)
        
        print(f"Output Directory: {self.output_dir}")
        
        helper = VideoTestHelper(
            output_dir=self.output_dir,
            filename_base='brush_reveal_test_002',
            fps=fps
        )
        
        print(f"Rendering {total_frames} frames ({total_duration}s)...")
        
        for scene_idx, scene in enumerate(SCENES):
            scene_start = scene_idx * (SCENE_DURATION + TRANSITION_GAP)
            print(f"\\n{scene['name']} @ {scene_start}s")
            
            # Create layers
            layers = []
            eased_actions = []
            
            for i, item in enumerate(scene["items"]):
                x, y, w, h = POSITIONS[i]
                layer_id = f"scene{scene_idx}_layer{i}"
                
                layer = MockGrid(layer_id, item["color"], x, y, w, h, i, item["label"])
                layers.append(layer)
                
                overshoot = item.get("overshoot", 0.0)
                easing = EasingCurve(item["easing"], overshoot)
                
                action = Action(layer_id, ActionType.BRUSH, scene_start, 3.0, Vector2(0,0))
                eased_actions.append((action, easing, layer))
            
            # Setup World
            scene_entity = SceneEntity()
            for l in layers:
                scene_entity.add_layer(l)
            world = WorldEntity(800, 600, scene_entity)
            
            anim_controller = AnimationController(800, 600)
            anim_controller.initialize_layers([l.id for l in layers])
            
            for l in layers:
                state = anim_controller.get_layer_state(l.id)
                state.position = Vector2(l.bounds.x + l.w/2, l.bounds.y + l.h/2)
            
            viewport = ViewportEntity(800, 600, 30)
            from adapters.driven.image.pillow_image_adapter import PillowImageAdapter
            image_processor = PillowImageAdapter()
            compositor = FrameCompositor(world, viewport, image_processor=image_processor)
            compositor.layer_service.clear_cache()
            for l in layers:
                compositor.layer_service._layer_cache[l.id] = l._create_mock_image()
            
            mock_renderer = MockRenderer()
            
            # Render Scene Frames
            scene_frame_start = int(scene_start * fps)
            scene_frame_end = int((scene_start + SCENE_DURATION) * fps)
            
            for f in range(scene_frame_start, min(scene_frame_end, total_frames)):
                time = f / fps
                # if f % 60 == 0: print(f"Frame {f}/{total_frames}")
                
                # Update
                for action, easing, layer in eased_actions:
                    if time >= action.start_time and time <= (action.start_time + action.duration):
                        raw_p = (time - action.start_time) / action.duration
                        eased_p = easing.apply(raw_p)
                        anim_controller.update(action, eased_p)
                    elif time > (action.start_time + action.duration):
                        anim_controller.update(action, 1.0)
                
                # Compose
                layer_states = {l.id: anim_controller.get_layer_state(l.id) for l in layers}
                img = compositor.compose_psd_content(
                    layer_states,
                    lambda lid, ls=layers: next((x for x in ls if x.id == lid), None)
                )
                
                # Draw Labels (UI Overlay)
                d = ImageDraw.Draw(img)
                d.rectangle([0, 0, 800, 50], fill=(30, 30, 30, 255))
                d.text((20, 15), scene["name"], fill=(255, 255, 255, 255))
                
                for i, item in enumerate(scene["items"]):
                    x, y, w, h = POSITIONS[i]
                    d.text((x + 10, y + h + 10), item["label"], fill=(50, 50, 50, 255))
                
                # Save
                helper.write_frame(img, save_to_gif=(f % 3 == 0))
        
        helper.finalize()
        print("\\n--- Complete ---")
        self.assertTrue(os.path.exists(self.output_dir))


if __name__ == "__main__":
    unittest.main()
