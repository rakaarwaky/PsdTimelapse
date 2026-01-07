from dataclasses import dataclass

from ..value_objects.analysis.layer_analysis_value import LayerAnalysis
from ..value_objects.animation.brush_path_type_value import BrushPathType
from ..value_objects.animation.path_direction_value import PathDirection
from .action_entity import Action

# Assuming BrushPathType is in existing location, based on imports in original code:
# from ..animator import BrushPathType
# But code showed it was imported from `.animator` in `smart_timeline_planner_module.py`.
# I should double check where BrushPathType is.
# The user's metadata mentioned `domain/value_objects/brush_tool.py`, but `BrushPathType` was referred in `Integrate Value Objects` conversation.
# Safe bet is to try to import it from `domain.modules.animator` as per original code OR `domain.value_objects.brush_tool` if it was moved.
# Wait, I'll temporarily import from `..modules.animator` if I can't confirm.
# Actually, looking at the previous conversation summary "Integrate Value Objects", it mentioned "consolidating it".
# Let's try `domain.value_objects.brush_strategy` or similar.
# The original code imported from `..animator`.
# I'll stick to `from ..modules.animator import BrushPathType` for now to avoid specific breakage,
# BUT `domain/entities` importing from `domain/modules` violates architecture rules (Dependency Rule: Entities should not depend on Modules).
# So `BrushPathType` MUST be a Value Object.
# If it's not well placed, I should move it or find where it is.
# I will check `engine/src/domain/value_objects/animation/brush_path_type.py` availability or create it if missing,
# but per "extreme modularity" approval I can create it.
# Let's check `engine/src/domain/value_objects/brush_tool.py`.


@dataclass
class SmartAction(Action):
    """Extended action with smart planning metadata."""

    path_direction: PathDirection = PathDirection.HORIZONTAL
    analysis: LayerAnalysis | None = None
    # Defaulting to STRAIGHT if import fails is risky, but I'll use a string or Any temporarily if I can't locate it,
    # but better to assume it's a VO.
    # I will assume `BrushPathType` is available or needs to be moved.
    # The original import was `from ..animator import BrushPathType`.
    brush_path_type: "BrushPathType" = (
        None  # Type hint generic to avoid runtime error if possible, but dataclass needs value.
    )


# Correct strategy: I will check for BrushPathType location in next step. For now I will write this file without the specific enum import
# if I can avoid it, or better yet, I'll `run_command` to find it first.
