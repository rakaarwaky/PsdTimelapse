"""
Pipeline Manager Module
=======================

Central rendering pipeline coordination with strict type enforcement and validation.
"""

from typing import TYPE_CHECKING

from ...value_objects.configs import (
    CompositeConfig,
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
from .orchestrator.director_engine_module import DirectorEngine
from .orchestrator.pipeline_manager_module import PipelineManager
from .orchestrator.render_pipeline_module import PipelineProgress, PipelineState, RenderPipeline
from .pipeline_orchestrator import PipelineOrchestrator, create_pipeline

# Re-export configuration for public access
__all__ = [
    "CompositeConfig",
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
