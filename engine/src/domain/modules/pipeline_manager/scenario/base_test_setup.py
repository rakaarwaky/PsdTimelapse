"""
Base Test Setup
================

Common utilities, paths, and fixtures for all render scenario tests.
Provides standardized output paths using MediaOutputService.
"""
import sys
import os
import shutil
from pathlib import Path
from typing import Optional, Callable, Any
from dataclasses import dataclass

# ============================================================
# Path Setup
# ============================================================

# Scenario directory (this file's location)
SCENARIO_DIR = Path(__file__).parent.absolute()

# Project roots
PIPELINE_MANAGER_DIR = SCENARIO_DIR.parent
MODULES_DIR = PIPELINE_MANAGER_DIR.parent
DOMAIN_DIR = MODULES_DIR.parent
SRC_DIR = DOMAIN_DIR.parent
ENGINE_DIR = SRC_DIR.parent

# Ensure src is in path
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ============================================================
# Asset Paths
# ============================================================

PSD_PATH = SRC_DIR / "assets" / "Psd" / "test.psd"
MEDIA_OUTPUT_DIR = ENGINE_DIR / "media"

# ============================================================
# Constants (from test.psd: 1080x1080 RGBA)
# ============================================================

PSD_WIDTH = 1080
PSD_HEIGHT = 1080
DEFAULT_FPS = 30
DEFAULT_VIEWPORT = (1080, 1080)  # 1:1 ratio

# Final render resolution (locked)
FINAL_WIDTH = 1080
FINAL_HEIGHT = 1920


# ============================================================
# Domain Imports
# ============================================================

def get_domain_imports():
    """Lazy import domain modules to avoid circular imports."""
    from domain.modules.pipeline_manager.rendering.media_output_service_module import (
        MediaOutputService,
        ProjectManifest
    )
    from domain.value_objects.configs import MediaOutputConfig
    from domain.value_objects.resource import MediaOutputPath
    return {
        'MediaOutputService': MediaOutputService,
        'MediaOutputConfig': MediaOutputConfig,
        'MediaOutputPath': MediaOutputPath,
        'ProjectManifest': ProjectManifest,
    }


# ============================================================
# Base Test Class
# ============================================================

class BaseScenarioTest:
    """
    Base class for all scenario tests.
    Provides common setup/teardown and output management.
    """
    
    # Override in subclass
    test_name: str = "base_test"
    
    # Instance state (set in setup_output)
    _output_service = None
    _output_path = None
    
    @classmethod
    def get_psd_path(cls) -> Path:
        """Get absolute path to test.psd."""
        if not PSD_PATH.exists():
            raise FileNotFoundError(f"Test PSD not found: {PSD_PATH}")
        return PSD_PATH
    
    def setup_output(self, project_id: Optional[str] = None) -> "MediaOutputPath":
        """
        Initialize output using MediaOutputService.
        
        Args:
            project_id: Optional custom ID, auto-generates if None
            
        Returns:
            MediaOutputPath for the test project
        """
        imports = get_domain_imports()
        
        config = imports['MediaOutputConfig'](
            base_path=str(MEDIA_OUTPUT_DIR)
        )
        
        self._output_service = imports['MediaOutputService'](config)
        self._output_path = self._output_service.create_project(
            project_id or f"test_{self.test_name}"
        )
        
        return self._output_path
    
    def cleanup_output(self, keep_final: bool = True):
        """
        Cleanup test output.
        
        Args:
            keep_final: If True, runs cache cleanup (keeps MP4). 
                       If False, deletes entire project.
        """
        if self._output_service and self._output_path:
            if keep_final:
                self._output_service.cleanup_cache(self._output_path)
            else:
                self._output_service.cleanup_project(self._output_path)
    
    @property
    def output_path(self) -> Optional["MediaOutputPath"]:
        return self._output_path
    
    @property
    def output_service(self) -> Optional["MediaOutputService"]:
        return self._output_service


# ============================================================
# Mock Layer Factory
# ============================================================

@dataclass
class MockLayerData:
    """Data for creating mock layers."""
    id: str
    name: str
    x: int
    y: int
    width: int
    height: int
    z_index: int = 0
    visible: bool = True
    color: tuple = (255, 0, 0, 255)  # RGBA


def create_mock_layer(data: MockLayerData) -> "LayerEntity":
    """Create a mock LayerEntity from data."""
    from domain.entities.layer_entity import LayerEntity
    from domain.value_objects.geometry import Rect
    
    return LayerEntity(
        id=data.id,
        name=data.name,
        z_index=data.z_index,
        bounds=Rect(data.x, data.y, data.width, data.height),
        visible=data.visible
    )


def create_mock_image(width: int, height: int, color: tuple = (255, 0, 0, 255)):
    """Create a mock RGBA image."""
    try:
        from PIL import Image
        return Image.new('RGBA', (width, height), color)
    except ImportError:
        return None


# ============================================================
# Test Runner Utilities
# ============================================================

def load_psd_world():
    """Load test.psd and return WorldEntity."""
    from adapters.driven.psd_modeler.psdtools_parser_adapter import PsdToolsAdapter
    
    psd_path = str(PSD_PATH.absolute())
    adapter = PsdToolsAdapter()
    return adapter.load(psd_path)


def print_test_header(test_name: str):
    """Print formatted test header."""
    print("\n" + "=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)


def print_test_footer(success: bool = True):
    """Print formatted test footer."""
    status = "✅ PASSED" if success else "❌ FAILED"
    print("\n" + "-" * 60)
    print(f"RESULT: {status}")
    print("-" * 60 + "\n")
