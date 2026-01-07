"""
Per-Layer Animation Render Test (Dumb Script)
=============================================
Delegates all logic to Engine modules:
1. ScriptDirector -> Plans Timeline
2. Animator (LayerAnimationService) -> Generates Pure State
3. PipelineManager (LayerRenderPipeline) -> Orchestrates I/O
"""
import sys
import os
import shutil
import json
import unittest
import dataclasses
from typing import Any

# PYTHONPATH handled by .env

# DEPS
# If test_02 doesn't import Timeline explicitly, maybe no need.
# But checking imports...
from domain.modules.script_director import plan_smart_timeline
# It doesn't import Timeline explicitly in the provided snippet earlier.
# If it fails, I'll see why.
# Wait, I didn't see explicit Timeline import in test_02 snippet earlier.
# I'll enable this tool call only if needed.
# Converting usage if any.
# Actually, test_01 failed explicitly. test_02 failed discovery. Likely related.
# I'll check test_02 imports first.
from domain.modules.animator import (
    create_animator,
    AnimatorConfig
)
from domain.value_objects.configs import LayerRenderConfig
from domain.modules.pipeline_manager.orchestrator.layer_render_pipeline_module import LayerRenderPipeline
from domain.entities.layer_entity import LayerEntity
from domain.value_objects.geometry import Vector2, Rect, rect
try:
    from PIL import Image
except ImportError:
    Image = None

class TestPerLayerRender(unittest.TestCase):
    def setUp(self):
        # Setup Paths
        # Setup Paths
        from domain.value_objects.resource.media_output_path_value import MediaOutputPath
        from pathlib import Path
        
        # Resolve 'engine' root
        # Resolve 'engine' root
        # Start: src/domain/modules/pipeline_manager/scenario/integration (test file)
        # Goal: engine (6 levels up)
        engine_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../'))
        media_base = Path(engine_root) / "media"
        
        self.output_path = MediaOutputPath(
            base_path=media_base,
            project_id="test_project"
        )
        self.output_dir = str(self.output_path.tests_dir / "integration" / "per_layer_render")
        
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    def test_smart_render_execution(self):
        print("\n=== Smart Render Integration Test ===")
        
        # 1. Mock Data (No PsdTools dependency)
        WIDTH = 1080
        HEIGHT = 1920
        
        bg_layer = LayerEntity(
            id="root_0",
            name="Background",
            z_index=0,
            bounds=rect(0, 0, WIDTH, HEIGHT),
            visible=True
        )
        
        active_layer = LayerEntity(
            id="layer_1",
            name="[D] Hero",
            z_index=1,
            bounds=rect(100, 100, 200, 200),
            visible=True
        )
        
        all_layers = [bg_layer, active_layer]
        print(f"Mocked {len(all_layers)} layers")
        
        # Mock Image Provider
        def mock_get_image(layer):
            if Image:
                return Image.new('RGBA', (int(layer.bounds.width), int(layer.bounds.height)), (255, 0, 0, 255))
            return None

        # 2. Plan Timeline (Script Director)
        print("Planning Smart Timeline...")
        timeline = plan_smart_timeline(
            layers=all_layers,
            canvas_width=WIDTH,
            canvas_height=HEIGHT,
            exclude_bottom_layer=True
        )
        print(f"Timeline Duration: {timeline.total_duration}s")
        
        # 3. Configure Renderer (Animator + Pipeline)
        anim_config = AnimatorConfig(
            viewport_width=WIDTH,
            viewport_height=HEIGHT
        )
        
        # New: Instantiate pure service
        animation_service = create_animator(width=WIDTH, height=HEIGHT, config=anim_config)
        
        # New: Instantiate Pipeline Orchestrator with Ports
        # Use Mock Adapter for testing logic without OpenEXR
        class MockExrAdapter:
            def __init__(self, *args): pass
            def write_frame(self, frame, path): 
                # Simulate file creation for verification
                with open(path, 'w') as f: f.write("mock_exr_data")
                
        exr_adapter = MockExrAdapter()

        pipeline = LayerRenderPipeline(
            config=LayerRenderConfig(
                output_dir=self.output_dir,
                fps=24,
                canvas_width=WIDTH,
                canvas_height=HEIGHT,
                enable_video=True
            ),
            animation_service=animation_service,
            exr_port=exr_adapter,
            video_port=None,
            media_output=self.output_path
        )
        
        # 4. Execute Render
        total_frames = int(timeline.total_duration * 24)
        print(f"Total Frames: {total_frames}")
        
        manifests = []
        
        for layer in all_layers:
            # Find time range for this layer
            layer_actions = [a for a in timeline.actions if a.layer_id == layer.id]
            is_bottom = layer.z_index == min(l.z_index for l in all_layers)
            
            if layer_actions:
                action = layer_actions[0]
                start_frame = int(action.start_time * 24)
                end_frame = int((action.start_time + action.duration) * 24)
            else:
                action = None
                start_frame = 0
                end_frame = total_frames
                
            print(f"Rendering {layer.id}... ({start_frame}-{end_frame})")
            
            # DELEGATE TO PIPELINE
            manifest = pipeline.execute(
                layer=layer,
                get_layer_image=mock_get_image,
                timeline_info={
                    'start_frame': start_frame,
                    'end_frame': end_frame,
                    'total_frames': total_frames,
                    'action': action,
                    'layer': layer
                }
            )
            manifests.append(manifest)
            
        # 5. Validation
        print(f"Generated {len(manifests)} manifests")
        
        # Write generic manifest just for debug
        manifest_path = os.path.join(self.output_dir, "manifest_dump.json")
        with open(manifest_path, 'w') as f:
            json.dump([dataclasses.asdict(m) for m in manifests], f, indent=2)
            
        # 6. Verify File Optimization
        print("Verifying outputs...")
        for lm in manifests:
            start_frame = lm.visible_range[0]
            folder = lm.sequence_folder
            
            # Only check if folder exists (it should)
            self.assertTrue(os.path.exists(folder))

            # If we don't have exr_adapter or Image, we can't check files
            if exr_adapter and Image:
                # Check blank frames (should NOT exist)
                for f in range(start_frame):
                    f_path = os.path.join(folder, f"frame_{f:05d}.exr")
                    self.assertFalse(os.path.exists(f_path), f"Blank frame {f} should not exist for {lm.id}")
                    
                # Check visible frames (should exist)
                # visible_range is (start, end)
                end_frame = lm.visible_range[1]
                if start_frame < end_frame:
                    first_vis = os.path.join(folder, f"frame_{start_frame:05d}.exr")
                    self.assertTrue(os.path.exists(first_vis), f"First visible frame {start_frame} missing for {lm.id}")
            else:
                print(f"Skipping file check for {lm.id} (No EXR Adapter or Pillow)")

if __name__ == "__main__":
    unittest.main()
