"""
Compositor Module
=================

Layer merging, effects, and frame composition.

Public API:
-----------
- CompositorConfig: Configuration for composition behavior
- CompositorOrchestrator: High-level compositor with all components
- create_compositor(): Factory with sensible defaults
- FrameCompositor: Direct access (backward compatible)

Usage:
------
    from domain.modules.compositor import create_compositor

    compositor = create_compositor(world, viewport)
    frame = compositor.compose_frame(layer_states, find_layer_fn)

Internal (DO NOT IMPORT DIRECTLY):
----------------------------------
- compositor_module.py
- layer_compositor_module.py
- layer_cache_module.py
- viewport_compositor_module.py
- layer_service.py
- blur_op.py, opacity_op.py, composite_op.py, subpixel_op.py
"""

from __future__ import annotations

# ============================================================
# Backward Compatible Re-exports
# ============================================================
from ...value_objects.compositor import (
    CachedLayer,
    CompositeFrame,
    CompositeLayer,
    CursorStyle,
)

# ============================================================
# Core Exports (Extracted)
# ============================================================
from ...value_objects.configs import CompositorConfig
from .compositor_orchestrator import (
    CompositorOrchestrator,
    create_compositor,
    create_frame_compositor,
)
from .ops.blur_module import apply_motion_blur
from .ops.composite_module import safe_paste
from .ops.opacity_module import apply_opacity
from .orchestrators.compositor_module import FrameCompositor
from .orchestrators.layer_compositor_module import MultiLayerCompositor
from .services.cursor_render_service import CursorRenderService
from .services.layer_cache_module import LayerCache
from .services.layer_service import LayerRetrievalService

# Alias following naming convention
CompositorModule = FrameCompositor
LayerCompositorModule = MultiLayerCompositor


# ============================================================
# Public API
# ============================================================

__all__ = [
    "CachedLayer",
    "CompositeFrame",
    "CompositeLayer",
    "CompositorConfig",
    "CompositorModule",
    "CompositorOrchestrator",
    "CursorRenderService",
    "CursorStyle",
    "FrameCompositor",
    "LayerCache",
    "LayerCompositorModule",
    "LayerRetrievalService",
    "MultiLayerCompositor",
    "apply_motion_blur",
    "apply_opacity",
    "create_compositor",
    "create_frame_compositor",
    "safe_paste",
]
