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
    PipelineConfig,
    PipelineProgress,
    PipelineState,
    RenderConfig,
    RenderPipeline,
)
from .modules.script_director import (
    ActionType,
    SequencingStrategy,
    TimelineEntity,
    estimate_duration,
    plan_timeline,
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
    "CameraAction",
    "AssetEntity",
    "AssetType",
    "AssetMetadata",
    "CameraEntity",
    "DocumentEntity",
    "LayerEntity",
    "BlendMode",
    "ActionHint",
    "SceneEntity",
    "SmartAction",
    "TimelineEntity",
    "ViewportEntity",
    "OutputPreset",
    "WorldEntity",
    # === Value Objects ===
    "Vector2",
    "vec2",
    "ZERO",
    "ONE",
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    "Rect",
    "rect",
    "Color",
    "WHITE",
    "BLACK",
    "RED",
    "GREEN",
    "BLUE",
    "TRANSPARENT",
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
    "DirectorProfile",
    "RhythmPace",
    # === Ports ===
    "AssetProviderPort",
    "NullAssetProvider",
    "CachePort",
    "CompositorPort",
    "ExrExportPort",
    "FileSystemPort",
    "GpuRendererPort",
    "ImageProcessingPort",
    "LoggerPort",
    "NullLogger",
    "NotificationPort",
    "InMemoryEventBus",
    "NullNotifier",
    "DomainEvent",
    "EventPayload",
    "OverlayPort",
    "NullOverlay",
    "CursorType",
    "PsdPort",
    "RandomPort",
    "DeterministicRandom",
    "RendererPort",
    "TimePort",
    "MockTime",
    "VideoPort",
    # === Core Engine ===
    "ProducerEngine",
    "ProducerConfig",
    # === Modules ===
    # Pipeline
    "DirectorEngine",
    "RenderConfig",
    "EngineState",
    "EngineProgress",
    "RenderPipeline",
    "PipelineConfig",
    "PipelineState",
    "PipelineProgress",
    # Script Director
    "ActionType",
    "TimelineEntity",
    "SequencingStrategy",
    "estimate_duration",
    # Layout Manager
    "CoordinateMapper",
    # Animator
    "AnimationController",
    "LayerAnimState",
    "CursorState",
    "AnimationPath",
    "generate_drag_path",
    "generate_brush_path",
    "ease_in_out",
    "ease_out_back",
    "cubic_bezier",
    # Compositor
    "FrameCompositor",
    "CursorStyle",
    "MultiLayerCompositor",
    "LayerCache",
]
