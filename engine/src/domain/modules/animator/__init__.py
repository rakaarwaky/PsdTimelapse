"""
Animator Module
===============

Orchestrates animation, path generation, and frame rendering.

Submodules:
-----------
- core: Central control and state (AnimationController)
- strategies: Interactivity logic (Drag, Brush)
- motion: Kinematics and Path generation (Bezier)
- rendering: Layer composition and rendering services
- generators: Procedural state and mask generation
- io: caching and persistence
"""

from ...value_objects.animation.layer_anim_state import LayerAnimState
from ...value_objects.compositor import CursorState
from ...value_objects.configs import AnimatorConfig

# ============================================================
# IO / Manifest Exports
# ============================================================
from ...value_objects.io.render_manifest import LayerManifest
from .animator_orchestrator import create_animation_path, create_animator

# ============================================================
# Core Exports (re-exported from submodules)
# ============================================================
from .core.animator_controller_module import AnimationController
from .motion.bezier_solver_module import cubic_bezier, ease_in_out, ease_out_back
from .motion.path_generator_module import AnimationPath, generate_brush_path, generate_drag_path

# ============================================================
# Public API
# ============================================================
__all__ = [
    # Factory & Config
    "create_animator",
    "create_animation_path",
    "AnimatorConfig",
    # Core Services
    "AnimationController",
    "LayerAnimState",
    "CursorState",
    # Motion
    "AnimationPath",
    # Strategies
    "generate_drag_path",
    "generate_brush_path",
    # IO
    "LayerManifest",
    "ease_in_out",
    "ease_out_back",
    "cubic_bezier",
]
