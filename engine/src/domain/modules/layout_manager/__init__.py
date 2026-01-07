"""
Layout Manager Module
=====================

Scene blocking and coordinate transformations between World, Camera, and Viewport spaces.

Public API:
-----------
- LayoutConfig: Configuration for layout calculations
- create_coordinate_mapper(): Factory with camera/viewport injection
- CoordinateMapper: Direct access (backward compatible)

Usage:
------
    from domain.modules.layout_manager import create_coordinate_mapper

    mapper = create_coordinate_mapper(camera, viewport)
    screen_pos = mapper.world_to_viewport(world_pos)

Internal (DO NOT IMPORT DIRECTLY):
----------------------------------
- coordinate_mapper_module.py
"""

from __future__ import annotations

# ============================================================
# Core Exports (Extracted)
# ============================================================
from ...value_objects.configs import LayoutConfig

# ============================================================
# Backward Compatible Re-exports
# ============================================================
from .coordinate_mapper_module import CoordinateMapper
from .layout_orchestrator import create_coordinate_mapper

# ============================================================
# Public API
# ============================================================

__all__ = [
    # Configuration
    "LayoutConfig",
    # Factory
    "create_coordinate_mapper",
    # Core Class (backward compatible)
    "CoordinateMapper",
]
