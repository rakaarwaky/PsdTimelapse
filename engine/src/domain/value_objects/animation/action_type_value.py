from enum import Enum


class ActionType(Enum):
    """Types of animation actions the engine can perform."""

    DRAG = "drag"  # Element flies in and snaps to position
    BRUSH = "brush"  # Element revealed by cursor movement
    FADE = "fade"  # Simple opacity fade-in
    NONE = "none"  # No animation (instant appear)
