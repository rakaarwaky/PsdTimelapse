"""
Pytest Configuration and Fixtures
==================================

Shared fixtures for all scenario tests.
"""
import pytest
import sys
import os
from pathlib import Path

# Ensure src path
SCENARIO_DIR = Path(__file__).parent
SRC_DIR = SCENARIO_DIR.parent.parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def psd_path():
    """Path to test.psd."""
    from .base_test_setup import PSD_PATH
    return PSD_PATH


@pytest.fixture(scope="function")
def psd_world(psd_path):
    """Loaded WorldEntity from test.psd."""
    from adapters.driven.psd_modeler.psdtools_parser_adapter import PsdToolsAdapter
    adapter = PsdToolsAdapter()
    return adapter.load(str(psd_path))


@pytest.fixture(scope="function")
def timeline(psd_world):
    """Planned timeline from test.psd."""
    from domain.modules.script_director import plan_smart_timeline
    
    layers = list(psd_world.scene.iterate_all())
    return plan_smart_timeline(
        layers=layers,
        canvas_width=psd_world.width,
        canvas_height=psd_world.height,
        exclude_bottom_layer=True
    )


@pytest.fixture(scope="function")
def media_output(tmp_path):
    """MediaOutputService with temporary directory."""
    from domain.modules.pipeline_manager.rendering.media_output_service_module import MediaOutputService
    from domain.value_objects.configs import MediaOutputConfig
    
    config = MediaOutputConfig(base_path=str(tmp_path))
    service = MediaOutputService(config)
    output_path = service.create_project("pytest_test")
    
    yield output_path, service
    
    # Cleanup after test
    service.cleanup_project(output_path)


@pytest.fixture(scope="session")
def engine_media_output():
    """MediaOutputService pointing to engine/media for persistent tests."""
    from .base_test_setup import MEDIA_OUTPUT_DIR
    from domain.modules.pipeline_manager.rendering.media_output_service_module import MediaOutputService
    from domain.value_objects.configs import MediaOutputConfig
    
    config = MediaOutputConfig(base_path=str(MEDIA_OUTPUT_DIR))
    service = MediaOutputService(config)
    
    return service
