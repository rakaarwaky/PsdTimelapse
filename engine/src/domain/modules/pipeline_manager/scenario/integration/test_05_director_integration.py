"""
Director Integration Test
=========================
Verifies that the DirectorEngine orchestrator correctly integrates with:
1. MediaOutputService (for path generation)
2. Rendering Strategies
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
    print_test_header,
    print_test_footer,
    PSD_PATH,
)

# Domain Imports
from domain.modules.pipeline_manager.orchestrator.director_engine_module import DirectorEngine
from domain.value_objects.configs.pipeline_config_value import RenderConfig
from domain.entities.world_entity import WorldEntity
from domain.entities.timeline_entity import TimelineEntity
from domain.entities.action_entity import Action
from domain.value_objects.animation.action_type_value import ActionType

# Port Mocks/Adapters
# We will use simple mocks where possible to keep it lightweight, 
# or reuse what's available if it's integrated.

class MockUiRenderer:
    def render_static_ui(self, layers):
        from PIL import Image
        return Image.new('RGBA', (100, 100), (0,0,0,0))

class MockVideoPort:
    def __init__(self):
        self.recorded_path = None
        
    def start_recording(self, path, viewport, codec=None):
        self.recorded_path = path
        # Create dummy file to simulate success
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write("mock_video_data")
            
    def write_frame(self, frame):
        pass
        
    def stop_recording(self):
        pass

class TestDirectorIntegration(BaseScenarioTest, unittest.TestCase):
    test_name = "director_integration"
    
    def setUp(self):
        # Base setup creates self._output_service and self._output_path
        self.setup_output("test_project")
        print_test_header("DirectorEngine Integration")
        
    def test_director_media_path_integration(self):
        """Test that DirectorEngine uses MediaOutputService to set output paths."""
        
        # 1. Setup Director
        video_port = MockVideoPort()
        
        # We need a DirectorEngine that we can inspect
        # Since DirectorEngine doesn't fully support injection of everything in __init__ 
        # (some are internal state), we might need to partially construct or mock its internals
        # for a pure unit/integration test, OR run it fully.
        
        director = DirectorEngine()
        
        # Inject our MediaOutputService
        director.media_output_service = self.output_service
        
        # Inject standard ports
        director.video_port = video_port
        director.ui_renderer_factory = lambda: MockUiRenderer()
        
        # Load World (Manual injection for speed, or bypass load_project)
        # Director.load_project(psd_path) does real PSD loading.
        # Let's try to mock the world to avoid dependency on heavy PSD parsing if possible,
        # but for Integration, maybe we SHOULD use real PSD.
        
        # Let's rely on Director's manual setup if possible, or just mock the state.
        # Director.world is set by load_project.
        
        # Mock World
        mock_world = WorldEntity(1080, 1080)
        mock_world.source_path = Path("test_project.psd") # Fake source
        director.world = mock_world
        
        # Mock Timeline
        director.timeline = TimelineEntity()
        # Add dummy action to set duration (total_duration is property)
        director.timeline.add_action(Action(
            layer_id="dummy_layer",
            action_type=ActionType.NONE,
            start_time=0.0,
            duration=1.0
        ))
        
        # 2. Configure Render
        config = RenderConfig(
            output_path="SHOULD_BE_IGNORED_IF_SERVICE_PRESENT",
            width=100,
            height=100,
            fps=10
        )
        
        # 3. Run Director (Partially)
        # Calling `run` calls `_ensure_media_path` then `_execute_strategy`
        # We want to verify `_ensure_media_path` worked and passed correct path to strategy.
        
        # We can spy on _execute_strategy or check media_path state after execution.
        
        # Warning: DirectorEngine.run() calls CPURenderStrategy() which creates REAL components.
        # To avoid heavy computation, we might want to mock the Strategy creation.
        # But Director implementation hardcodes `strategy = CPURenderStrategy(self.world)`.
        # This makes it hard to mock without patching.
        
        # Let's use `unittest.mock.patch`
        from unittest.mock import patch, MagicMock
        
        with patch('domain.modules.pipeline_manager.orchestrator.director_engine_module.CPURenderStrategy') as MockStrategyClass:
            mock_strategy_instance = MockStrategyClass.return_value
            mock_strategy_instance.execute.return_value = "/final/path/video.mp4"
            
            result_path = director.run(config)
            
            # Verify _ensure_media_path logic
            self.assertIsNotNone(director.media_path)
            self.assertEqual(director.media_path.project_id, "test_project")
            print(f"✓ Director created media path: {director.media_path.project_root}")
            
            # Verify it passed media_output to strategy
            mock_strategy_instance.execute.assert_called_once()
            call_args = mock_strategy_instance.execute.call_args
            self.assertIn('media_output', call_args.kwargs)
            self.assertEqual(call_args.kwargs['media_output'], director.media_path)
            print("✓ Director passed media_output to strategy")

if __name__ == "__main__":
    unittest.main()
