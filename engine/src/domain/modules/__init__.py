"""
Domain Modules Package - 7-Role Architecture
============================================

Root of the Domain Service Layer.
Responsibility: Enforce strict usage of Entities and Value Objects across module boundaries.

Exports are categorized by their Domain Role:
1. Entities (Mutable, Identity-based)
2. Value Objects (Immutable, Attribute-based)
3. Services (Stateless Logic)
4. Configs (Data Transfer Objects)
"""

# ============================================================
# 1. Pipeline & Orchestration (The "Manager")
# ============================================================
# ============================================================
# 4. Animator (The "Mover")
# ============================================================
from .animator import (
    AnimationController,  # Service
    AnimationPath,  # Value Object
    AnimatorConfig,  # Config
    LayerAnimState,  # Value Object
    create_animator,  # Factory
    generate_brush_path,  # Service
    generate_drag_path,  # Service
)

# ============================================================
# 5. Compositor (The "Builder")
# ============================================================
from .compositor import (
    CompositorConfig,  # Config
    CursorStyle,  # Value Object (Enum)
    FrameCompositor,  # Service
    LayerCache,  # Service (Infrastructure wrapper)
    create_compositor,  # Factory
)

# ============================================================
# 3. Layout Manager (The "Mapper")
# ============================================================
from .layout_manager import (
    CoordinateMapper,  # Service
    LayoutConfig,  # Config
    create_coordinate_mapper,  # Factory
)

# ============================================================
# Legacy / Backward Compatibility
# ============================================================
from .pipeline_manager import (
    DirectorEngine,
    EngineProgress,
    EngineState,
    PipelineManager,
    PipelineOrchestrator,
    PipelineProgress,
    PipelineState,
    RenderConfig,
    RenderPipeline,
    create_pipeline,
)

# ============================================================
# 2. Script Director (The "Planner")
# ============================================================
from .script_director import (
    Action,  # Entity
    ActionType,  # Value Object (Enum)
    CameraAction,  # Entity
    ScriptDirectorConfig,  # Config
    SequencingStrategy,  # Value Object (Enum)
    SmartAction,  # Entity
    TimelineEntity,  # Entity (Aggregate)
    create_timeline,  # Factory
    estimate_duration,  # Service
    plan_production,  # Facade
)

__all__ = [
    "Action",
    "ActionType",
    "AnimationController",
    "AnimationPath",
    "AnimatorConfig",
    "CameraAction",
    "CompositorConfig",
    "CoordinateMapper",
    "CursorStyle",
    "DirectorEngine",
    "EngineProgress",
    "EngineState",
    "FrameCompositor",
    "LayerAnimState",
    "LayerCache",
    "LayoutConfig",
    "PipelineConfig",
    "PipelineManager",
    "PipelineOrchestrator",
    "PipelineProgress",
    "PipelineState",
    "RenderConfig",
    "RenderMode",
    "RenderPipeline",
    "ScriptDirectorConfig",
    "SequencingStrategy",
    "SmartAction",
    "TimelineEntity",
    "create_animator",
    "create_compositor",
    "create_coordinate_mapper",
    "create_pipeline",
    "create_timeline",
    "estimate_duration",
    "generate_brush_path",
    "generate_drag_path",
    "plan_production",
]
