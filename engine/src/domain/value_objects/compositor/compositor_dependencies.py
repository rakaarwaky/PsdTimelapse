from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CompositorDependencies:
    """Dependencies injected into the compositor."""

    mask_generator_fn: Callable[..., Any] | None = None
    brush_tool_factory_fn: Callable[..., Any] | None = None
    path_generator_fn: Callable[..., Any] | None = None
    get_brush_cursor_pos_fn: Callable[..., Any] | None = None
    draw_brush_cursor_ui_fn: Callable[..., Any] | None = None
