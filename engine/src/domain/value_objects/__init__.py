"""
Value Objects
==============

Immutable domain value objects organized by function.

Subpackages:
- geometry: Coordinates, shapes, transformations
- visual: Color, opacity, blend modes, output config
- animation: Easing, brush tools, render state
- timing: Duration, time range, frame rate
- resource: File path, memory, batch, workers
- analysis: Classification, layer analysis
- manifest: Compositor and layer manifests

Usage:
    from engine.src.domain.value_objects import Vector2, Color, EasingCurve
    from engine.src.domain.value_objects.geometry import Rect
"""

# Geometry - Coordinates & Shapes
# Analysis - Classification & Insights
from .analysis import (
    ClassificationResult,
    LayerAnalysis,
)

# Animation - Easing & Brush
from .animation import (
    ActionType,
    BrushPathType,
    BrushTool,
    DirectorProfile,
    EasingCurve,
    EasingType,
    LayerClassification,
    PathDirection,
    RecommendedAction,
    RenderState,
    RhythmPace,
    SequencingStrategy,
)

# Compositor - Rendering & Layers
from .compositor import (
    CachedLayer,
    CompositeFrame,
    CursorState,
    CursorStyle,
    LayerType,
    RenderLayer,
)

# Configs - Immutable Configuration Value Objects
from .configs import (
    AnimatorConfig,
    CompositorConfig,
    EngineProgress,
    EngineState,
    LayerRenderConfig,
    LayoutConfig,
    PipelineConfig,
    ProducerConfig,
    RenderConfig,
    RenderMode,
    ScriptDirectorConfig,
)
from .geometry import (
    DOWN,
    LEFT,
    ONE,
    RIGHT,
    UP,
    ZERO,
    Dimensions,
    Rect,
    Scale,
    Transform2D,
    Vector2,
    rect,
    vec2,
)

# Manifest - Output Description
from .manifest import (
    CompositorManifest,
    LayerManifest,
)

# Resource - Files & Processing
from .resource import (
    IMAGE_EXTENSIONS,
    PSD_EXTENSIONS,
    VIDEO_EXTENSIONS,
    BatchSize,
    FilePath,
    MemoryLimit,
    MemoryUnit,
    WorkerCount,
)

# Timing - Duration & Frames
from .timing import (
    COMMON_FRAME_RATES,
    Duration,
    FrameRate,
    Progress,
    TimeRange,
)

# Visual - Color & Appearance
from .visual import (
    BG_COLOR,
    BLACK,
    BLUE,
    CANVAS_MARGIN,
    CANVAS_RENDER_AREA,
    GREEN,
    LAYER_PANEL_HEIGHT,
    RED,
    RESOLUTION_PRESETS,
    TRANSPARENT,
    UI_CANVAS,
    UI_LAYERS_PANEL,
    UI_MENUBAR,
    UI_TOOLBAR,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
    WHITE,
    BlendMode,
    BlendModeType,
    Border,
    BorderAlignment,
    BorderStyle,
    Color,
    Opacity,
    Orientation,
    Resolution,
    calculate_psd_offset,
)

__all__ = [
    # Geometry
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
    "Dimensions",
    "Scale",
    "Transform2D",
    # Visual
    "Color",
    "WHITE",
    "BLACK",
    "RED",
    "GREEN",
    "BLUE",
    "TRANSPARENT",
    "Opacity",
    "BlendMode",
    "BlendModeType",
    "Border",
    "BorderAlignment",
    "BorderStyle",
    "Orientation",
    "Resolution",
    "RESOLUTION_PRESETS",
    "VIDEO_WIDTH",
    "VIDEO_HEIGHT",
    "BG_COLOR",
    "LAYER_PANEL_HEIGHT",
    "UI_MENUBAR",
    "UI_LAYERS_PANEL",
    "UI_TOOLBAR",
    "UI_CANVAS",
    "CANVAS_MARGIN",
    "CANVAS_RENDER_AREA",
    "calculate_psd_offset",
    # Animation
    "EasingCurve",
    "EasingType",
    "BrushTool",
    "BrushPathType",
    "RenderState",
    "LayerClassification",
    "RecommendedAction",
    "DirectorProfile",
    "RhythmPace",
    "ActionType",
    "PathDirection",
    "SequencingStrategy",
    # Timing
    "Duration",
    "TimeRange",
    "FrameRate",
    "COMMON_FRAME_RATES",
    "Progress",
    # Resource
    "FilePath",
    "VIDEO_EXTENSIONS",
    "IMAGE_EXTENSIONS",
    "PSD_EXTENSIONS",
    "MemoryLimit",
    "MemoryUnit",
    "BatchSize",
    "WorkerCount",
    # Compositor
    "CursorStyle",
    "CursorState",
    "LayerType",
    "RenderLayer",
    "CompositeFrame",
    "CachedLayer",
    # Analysis
    "ClassificationResult",
    "LayerAnalysis",
    # Manifest
    "CompositorManifest",
    "LayerManifest",
    # Configs
    "ProducerConfig",
    "AnimatorConfig",
    "CompositorConfig",
    "LayoutConfig",
    "ScriptDirectorConfig",
    "LayerRenderConfig",
    "EngineState",
    "RenderMode",
    "RenderConfig",
    "PipelineConfig",
    "EngineProgress",
]
