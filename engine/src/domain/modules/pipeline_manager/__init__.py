"""
Pipeline Manager Module
=======================

Central rendering pipeline coordination with strict type enforcement and validation.
"""

from typing import TYPE_CHECKING

from ...value_objects.configs import (  # type: ignore[unused-ignore]
    CompositorConfig,
    EngineProgress,
    EngineState,
    RenderConfig,
)

if TYPE_CHECKING:
    pass

# ============================================================
# Core Exports (Extracted)
# ============================================================
# Legacy / Internal Imports (for compatibility)
# ============================================================
from ...value_objects.pipeline.pipeline_state import PipelineProgress, PipelineState
from .orchestrator.director_engine_module import DirectorEngine
from .orchestrator.pipeline_manager_module import PipelineManager
from .orchestrator.render_pipeline_module import RenderPipeline
from .pipeline_orchestrator import PipelineOrchestrator, create_pipeline

# Re-export configuration for public access
__all__ = [
    "CompositorConfig",
    "DirectorEngine",
    "EngineProgress",
    "EngineState",
    "PipelineManager",
    "PipelineOrchestrator",
    "PipelineProgress",
    "PipelineState",
    "RenderConfig",
    "RenderPipeline",
    "create_pipeline",
]
