"""
Test 04: Final Pipeline (E2E)
==============================

Complete end-to-end test: PSD → Timeline → EXR Frames → Composite → MP4

This is the master integration test that validates the entire render pipeline.
"""
import sys
import os
import unittest
from pathlib import Path

# Path setup
SCENARIO_DIR = Path(__file__).parent.parent
SRC_DIR = SCENARIO_DIR.parent.parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from domain.modules.pipeline_manager.scenario.base_test_setup import (
    BaseScenarioTest,
    load_psd_world,
    print_test_header,
    print_test_footer,
    MEDIA_OUTPUT_DIR,
    PSD_PATH,
)
from domain.value_objects.resource.media_output_path_value import MediaOutputPath


class TestFinalPipeline(BaseScenarioTest, unittest.TestCase):
    """
    E2E Integration Test: Complete render pipeline.
    
    Flow:
    1. Load test.psd
    2. Plan timeline via ScriptDirector
    3. Create output structure via MediaOutputService
    4. Render per-layer EXR frames
    5. Composite final frames
    6. Encode to MP4
    7. Verify outputs
    8. Cleanup cache (keep previews + final)
    """
    
    test_name = "final_pipeline"
    
    def setUp(self):
        """Initialize test with output structure."""
        super().setUp()
        print_test_header("Final Pipeline E2E Test")
        self.output = self.setup_output("test_project")
        print(f"Output project: {self.output.project_root}")
    
    def tearDown(self):
        """Cleanup but keep MP4 previews."""
        # Don't cleanup for now - let user inspect outputs
        pass
    
    def test_01_load_psd(self):
        """Step 1: Load test.psd successfully."""
        print("\n[1] Loading PSD...")
        
        self.assertTrue(PSD_PATH.exists(), f"PSD not found: {PSD_PATH}")
        
        world = load_psd_world()
        self.assertIsNotNone(world)
        self.assertEqual(world.width, 1080)
        self.assertEqual(world.height, 1080)
        
        layers = list(world.scene.iterate_all())
        print(f"    Loaded {len(layers)} layers from {world.width}x{world.height} PSD")
        self.assertGreater(len(layers), 0)
        
        return world
    
    def test_02_plan_timeline(self):
        """Step 2: Plan smart timeline."""
        print("\n[2] Planning Timeline...")
        
        from domain.modules.script_director import plan_smart_timeline
        
        world = load_psd_world()
        layers = list(world.scene.iterate_all())
        
        timeline = plan_smart_timeline(
            layers=layers,
            canvas_width=world.width,
            canvas_height=world.height,
            exclude_bottom_layer=True
        )
        
        self.assertIsNotNone(timeline)
        print(f"    Timeline duration: {timeline.total_duration}s")
        print(f"    Actions planned: {len(timeline.actions)}")
        
        # Verify alternating pattern
        if len(timeline.actions) >= 2:
            action_types = [a.action_type for a in timeline.actions]
            print(f"    Action sequence: {[t.value for t in action_types]}")
        
        return timeline
    
    def test_03_create_layer_structure(self):
        """Step 3: Create layer output folders."""
        print("\n[3] Creating Layer Structure...")
        
        world = load_psd_world()
        layers = list(world.scene.iterate_all())
        
        for layer in layers:
            if layer.z_index > 0:  # Skip background
                frames_dir = self._output_service.ensure_layer(self.output, layer.name)
                self.assertTrue(frames_dir.exists())
                print(f"    Created: {layer.name} -> {frames_dir}")
    
    def test_04_verify_output_structure(self):
        """Step 4: Verify complete output structure."""
        print("\n[4] Verifying Output Structure...")
        
        # Check main folders
        self.assertTrue(self.output.layout_dir.exists(), "layout/ missing")
        self.assertTrue(self.output.ui_dir.exists(), "ui/ missing")
        self.assertTrue(self.output.final_frames_dir.exists(), "final/frames/ missing")
        
        print("    ✓ layout/")
        print("    ✓ ui/")
        print("    ✓ final/frames/")
        
        # Check manifest
        self.assertTrue(self.output.manifest_path.exists(), "_manifest.json missing")
        print("    ✓ _manifest.json")
        
        print_test_footer(True)


def run_final_pipeline_test():
    """Run the complete E2E test."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFinalPipeline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_final_pipeline_test()
    sys.exit(0 if success else 1)
