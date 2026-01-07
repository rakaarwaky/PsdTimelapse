"""
CursorState Value Object
========================

Immutable cursor state for cross-module sharing between animator and compositor.
Animator produces this (calculates position), Compositor consumes (renders PNG).
"""

from dataclasses import dataclass

from ..geometry import Vector2


@dataclass(frozen=True)
class CursorState:
    """
    Immutable cursor state for animation rendering.

    Attributes:
        position: Cursor position in world coordinates
        visible: Whether cursor should be rendered
        tool_type: Visual tool type ("pointer", "brush", "hand")
        scale: Cursor scale factor
    """

    position: Vector2
    visible: bool = True
    tool_type: str = "pointer"
    scale: float = 1.0
