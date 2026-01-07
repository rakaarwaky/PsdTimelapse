"""
Domain Layer - Core Business Logic (7-Role Hexagonal Architecture)

This is the central entry point for the Domain Layer.
It exports all Entities, Value Objects, Ports, and Core Engine logic,
serving as a "complete library" for the application.

Usage:
    from engine.src.domain import SceneEntity, PsdPort, ProducerEngine
"""

# ============================================================
# ENTITIES (Mutable domain objects with identity)
# ============================================================
# ============================================================
# CORE ENGINE (Orchestration)
# ============================================================
from .core.engine import ProducerEngine
from .entities.action_entity import Action, CameraAction
from .entities.asset_entity import AssetEntity, AssetMetadata, AssetType
from .entities.camera_entity import CameraEntity
from .entities.document_entity import DocumentEntity
from .entities.layer_entity import ActionHint, BlendMode, LayerEntity
from .entities.scene_entity import SceneEntity
from .entities.smart_action_entity import SmartAction
from .entities.timeline_entity import TimelineEntity
from .entities.viewport_entity import OutputPreset, ViewportEntity
from .entities.world_entity import WorldEntity
from .modules.animator import (
    AnimationController,
    AnimationPath,
    CursorState,
    LayerAnimState,
    cubic_bezier,
    ease_in_out,
    ease_out_back,
    generate_brush_path,
    generate_drag_path,
)
from .modules.compositor import CursorStyle, FrameCompositor, LayerCache, MultiLayerCompositor
from .modules.layout_manager import CoordinateMapper

# ============================================================
# 7-ROLE MODULES (Sub-system Facades)
# ============================================================
from .modules.pipeline_manager import (
    DirectorEngine,
    EngineProgress,
    EngineState,
    PipelineProgress,
    PipelineState,
    RenderConfig,
    RenderPipeline,
)
from .modules.script_director import (
    ActionType,
    SequencingStrategy,
    estimate_duration,
    plan_smart_timeline,
)

# ============================================================
# PORTS (Hexagonal Architecture Interfaces)
# ============================================================
from .ports import (
    AssetProviderPort,
    CachePort,
    CompositorPort,
    CursorType,
    DeterministicRandom,
    DomainEvent,
    EventPayload,
    ExrExportPort,
    FileSystemPort,
    GpuRendererPort,
    ImageProcessingPort,
    InMemoryEventBus,
    LoggerPort,
    MockTime,
    NotificationPort,
    NullAssetProvider,
    NullLogger,
    NullNotifier,
    NullOverlay,
    OverlayPort,
    PsdPort,
    RandomPort,
    RendererPort,
    TimePort,
    VideoPort,
)

# ============================================================
# VALUE OBJECTS (Immutable primitives)
# ============================================================
from .value_objects import (
    BLACK,
    BLUE,
    DOWN,
    GREEN,
    LEFT,
    ONE,
    RED,
    RIGHT,
    TRANSPARENT,
    UP,
    WHITE,
    ZERO,
    BatchSize,
    BlendModeType,
    BrushTool,
    Color,
    Dimensions,
    DirectorProfile,
    Duration,
    EasingCurve,
    EasingType,
    FilePath,
    FrameRate,
    LayerClassification,
    MemoryLimit,
    MemoryUnit,
    Opacity,
    Progress,
    Rect,
    RenderState,
    Resolution,
    RhythmPace,
    Scale,
    TimeRange,
    Transform2D,
    Vector2,
    WorkerCount,
    rect,
    vec2,
)
from .value_objects.configs import ProducerConfig

__all__ = [
    "BLACK",
    "BLUE",
    "DOWN",
    "GREEN",
    "LEFT",
    "ONE",
    "RED",
    "RIGHT",
    "TRANSPARENT",
    "UP",
    "WHITE",
    "ZERO",
    "Action",
    "ActionHint",
    "ActionType",
    "AnimationController",
    "AnimationPath",
    "AssetEntity",
    "AssetMetadata",
    "AssetProviderPort",
    "AssetType",
    "BatchSize",
    "BlendMode",
    "BlendModeType",
    "BlendModeVO",
    "BrushTool",
    "CachePort",
    "CameraAction",
    "CameraEntity",
    "Color",
    "CompositorPort",
    "CoordinateMapper",
    "CursorState",
    "CursorStyle",
    "CursorType",
    "DeterministicRandom",
    "Dimensions",
    "DirectorEngine",
    "DirectorProfile",
    "DocumentEntity",
    "DomainEvent",
    "Duration",
    "EasingCurve",
    "EasingType",
    "EngineProgress",
    "EngineState",
    "EventPayload",
    "ExrExportPort",
    "FilePath",
    "FileSystemPort",
    "FrameCompositor",
    "FrameRate",
    "GpuRendererPort",
    "ImageProcessingPort",
    "InMemoryEventBus",
    "LayerAnimState",
    "LayerCache",
    "LayerClassification",
    "LayerEntity",
    "LoggerPort",
    "MemoryLimit",
    "MemoryUnit",
    "MockTime",
    "MultiLayerCompositor",
    "NotificationPort",
    "NullAssetProvider",
    "NullLogger",
    "NullNotifier",
    "NullOverlay",
    "Opacity",
    "OutputPreset",
    "OverlayPort",
    "PipelineConfig",
    "PipelineProgress",
    "PipelineState",
    "ProducerConfig",
    "ProducerEngine",
    "Progress",
    "PsdPort",
    "RandomPort",
    "Rect",
    "RenderConfig",
    "RenderPipeline",
    "RenderState",
    "RendererPort",
    "Resolution",
    "RhythmPace",
    "Scale",
    "SceneEntity",
    "SequencingStrategy",
    "SmartAction",
    "TimeLimit",
    "TimePort",
    "TimeRange",
    "TimelineEntity",
    "Transform2D",
    "Vector2",
    "VideoPort",
    "ViewportEntity",
    "WorkerCount",
    "WorldEntity",
    "cubic_bezier",
    "ease_in_out",
    "ease_out_back",
    "estimate_duration",
    "generate_brush_path",
    "generate_drag_path",
    "plan_smart_timeline",
    "rect",
    "vec2",
]
