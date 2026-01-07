"""
Domain Core Package - Gateway for Hexagonal Architecture

This is the central Gateway layer that:
1. Exports all Entities, Value Objects, and Ports (shared types)
2. Coordinates all Domain modules

Usage (preferred for modules):
    from domain.core import LayerEntity, Vector2, ImageProcessingPort

Usage (full engine):
    from domain.core import ProducerEngine, ProducerConfig
"""

# ============================================================
# ENTITIES (Mutable domain objects with identity)
# ============================================================
from ..entities.asset_entity import AssetEntity, AssetMetadata, AssetType
from ..entities.camera_entity import CameraEntity
from ..entities.document_entity import DocumentEntity
from ..entities.layer_entity import ActionHint, BlendMode, LayerEntity
from ..entities.scene_entity import SceneEntity
from ..entities.timeline_entity import TimelineEntity
from ..entities.viewport_entity import OutputPreset, ViewportEntity
from ..entities.world_entity import WorldEntity

# Animator exports
from ..modules.animator import (
    AnimationController,
    AnimationPath,
    LayerAnimState,
    cubic_bezier,
    ease_in_out,
    ease_out_back,
    generate_brush_path,
    generate_drag_path,
)

# Compositor exports
from ..modules.compositor import (
    CursorStyle,
    FrameCompositor,
    LayerCache,
    MultiLayerCompositor,
)

# Layout Manager exports
from ..modules.layout_manager import CoordinateMapper

# ============================================================
# MODULE EXPORTS (for backwards compatibility)
# ============================================================
# Engine exports (Unified in pipeline_manager)
from ..modules.pipeline_manager import (
    DirectorEngine,
    EngineProgress,
    EngineState,
    PipelineProgress,
    PipelineState,
    RenderConfig,
    RenderPipeline,
)

# Script Director exports
from ..modules.script_director import (
    Action,
    ActionType,
    CameraAction,
    SequencingStrategy,
    estimate_duration,
)

# ============================================================
# PORTS (Hexagonal Architecture Interfaces)
# ============================================================
from ..ports import (
    AssetProviderPort,
    CachePort,
    CompositorPort,
    CursorType,
    DeterministicRandom,
    DomainEvent,
    EventPayload,
    # Infrastructure
    FileSystemPort,
    GpuRendererPort,
    # Image Processing
    ImageProcessingPort,
    InMemoryEventBus,
    # Observability
    LoggerPort,
    MockTime,
    NotificationPort,
    NullAssetProvider,
    NullLogger,
    NullNotifier,
    NullOverlay,
    # UI/Visual
    OverlayPort,
    # Core I/O
    PsdPort,
    RandomPort,
    RendererPort,
    TimePort,
    VideoPort,
)

# ============================================================
# VALUE OBJECTS (Immutable primitives)
# ============================================================
from ..value_objects import (
    BatchSize,
    BlendModeType,
    BrushTool,
    Color,
    # dimensions / sizing
    Dimensions,
    # director
    DirectorProfile,
    # time-related
    Duration,
    EasingCurve,
    EasingType,
    # config
    FilePath,
    FrameRate,
    LayerClassification,
    MemoryLimit,
    MemoryUnit,
    # visual
    Opacity,
    Progress,
    Rect,
    # state
    RenderState,
    Resolution,
    RhythmPace,
    Scale,
    TimeRange,
    Transform2D,
    # Core geometry
    Vector2,
    WorkerCount,
)
from ..value_objects import (
    BlendMode as BlendModeVO,
)

# ============================================================
# MAIN ENGINE
# ============================================================
from .engine import ProducerConfig, ProducerEngine

__all__ = [
    # === ENTITIES ===
    "LayerEntity",
    "BlendMode",
    "ActionHint",
    "SceneEntity",
    "WorldEntity",
    "CameraEntity",
    "ViewportEntity",
    "OutputPreset",
    "AssetEntity",
    "AssetType",
    "AssetMetadata",
    "DocumentEntity",
    "TimelineEntity",
    "DirectorProfile",
    "RhythmPace",
    # === VALUE OBJECTS ===
    "Vector2",
    "Rect",
    "Color",
    "Dimensions",
    "Resolution",
    "Scale",
    "Duration",
    "FrameRate",
    "TimeRange",
    "Progress",
    "Opacity",
    "BlendModeVO",
    "BlendModeType",
    "BrushTool",
    "EasingCurve",
    "EasingType",
    "FilePath",
    "Transform2D",
    "MemoryLimit",
    "MemoryUnit",
    "BatchSize",
    "WorkerCount",
    "RenderState",
    "LayerClassification",
    # === PORTS ===
    "PsdPort",
    "RendererPort",
    "VideoPort",
    "GpuRendererPort",
    "CompositorPort",
    "LoggerPort",
    "NullLogger",
    "NotificationPort",
    "InMemoryEventBus",
    "NullNotifier",
    "DomainEvent",
    "EventPayload",
    "ImageProcessingPort",
    "CachePort",
    "OverlayPort",
    "NullOverlay",
    "CursorType",
    "AssetProviderPort",
    "NullAssetProvider",
    "FileSystemPort",
    "RandomPort",
    "DeterministicRandom",
    "TimePort",
    "MockTime",
    # === Main Engine ===
    "ProducerEngine",
    "DirectorEngine",
    "EngineState",
    "RenderConfig",
    "EngineProgress",
    "RenderPipeline",
    "PipelineConfig",
    "PipelineState",
    "PipelineProgress",
    # === Script Director ===
    "ActionType",
    "Timeline",
    "Action",
    "CameraAction",
    "SequencingStrategy",
    "estimate_duration",
    # === Layout Manager ===
    "CoordinateMapper",
    # === Animator ===
    "AnimationController",
    "LayerAnimState",
    "AnimationPath",
    "generate_drag_path",
    "generate_brush_path",
    "ease_in_out",
    "ease_out_back",
    "cubic_bezier",
    # === Compositor ===
    "FrameCompositor",
    "CursorStyle",
    "MultiLayerCompositor",
    "LayerCache",
]
