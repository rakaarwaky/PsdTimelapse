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
plan_smart_timeline
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
    # Dimensions / Sizing
    Dimensions,
    # Director
    DirectorProfile,
    # Time
    Duration,
    EasingCurve,
    EasingType,
    # Config
    FilePath,
    FrameRate,
    LayerClassification,
    MemoryLimit,
    MemoryUnit,
    # Visual
    Opacity,
    Progress,
    Rect,
    # State
    RenderState,
    Resolution,
    RhythmPace,
    Scale,
    TimeRange,
    Transform2D,
    # Core geometry
    Vector2,
    WorkerCount,
    rect,
    vec2,
)
from .value_objects import (
    BlendMode as BlendModeVO,
)
from .value_objects.configs import ProducerConfig

__all__ = [
    # === Entities ===
    "Action",
    "ActionHint",
    "AssetEntity",
    "AssetMetadata",
    "AssetType",
    "BlendMode",
    "CameraAction",
    "CameraEntity",
    "DocumentEntity",
    "LayerEntity",
    "OutputPreset",
    "SceneEntity",
    "SmartAction",
    "TimelineEntity",
    "ViewportEntity",
    "WorldEntity",
    # === Value Objects ===
    "BatchSize",
    "BLACK",
    "BlendModeType",
    "BlendModeVO",
    "BLUE",
    "BrushTool",
    "Color",
    "Dimensions",
    "DirectorProfile",
    "DOWN",
    "Duration",
    "EasingCurve",
    "EasingType",
    "FilePath",
    "FrameRate",
    "GREEN",
    "LayerClassification",
    "LEFT",
    "MemoryLimit",
    "MemoryUnit",
    "ONE",
    "Opacity",
    "Progress",
    "Rect",
    "rect",
    "RED",
    "RenderState",
    "Resolution",
    "RhythmPace",
    "RIGHT",
    "Scale",
    "TimeRange",
    "Transform2D",
    "TRANSPARENT",
    "UP",
    "vec2",
    "Vector2",
    "WHITE",
    "WorkerCount",
    "ZERO",
    # === Ports ===
    "AssetProviderPort",
    "CachePort",
    "CompositorPort",
    "CursorType",
    "DeterministicRandom",
    "DomainEvent",
    "EventPayload",
    "ExrExportPort",
    "FileSystemPort",
    "GpuRendererPort",
    "ImageProcessingPort",
    "InMemoryEventBus",
    "LoggerPort",
    "MockTime",
    "NotificationPort",
    "NullAssetProvider",
    "NullLogger",
    "NullNotifier",
    "NullOverlay",
    "OverlayPort",
    "PsdPort",
    "RandomPort",
    "RendererPort",
    "TimePort",
    "VideoPort",
    # === Core Engine ===
    "ProducerConfig",
    "ProducerEngine",
    # === Modules ===
    "ActionType",
    "AnimationController",
    "AnimationPath",
    "CoordinateMapper",
    "cubic_bezier",
    "CursorState",
    "CursorStyle",
    "DirectorEngine",
    "ease_in_out",
    "ease_out_back",
    "EngineProgress",
    "EngineState",
    "estimate_duration",
    "FrameCompositor",
    "generate_brush_path",
    "generate_drag_path",
    "LayerAnimState",
    "LayerCache",
    "MultiLayerCompositor",
    "PipelineConfig",
    "PipelineProgress",
    "PipelineState",
    "RenderConfig",
    "RenderPipeline",
    "SequencingStrategy",
]
