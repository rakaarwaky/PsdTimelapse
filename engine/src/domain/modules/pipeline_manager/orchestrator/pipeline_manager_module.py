"""
PipelineManager - Unified Compositing for CPU/GPU

Single source of truth for frame compositing algorithm.
Ensures CPU and GPU pipelines produce identical output.
"""
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any


@dataclass
class CompositeConfig:
    """Configuration for frame compositing."""

    width: int = 1080
    height: int = 1920
    fps: int = 30
    # Canvas area constants (matching UI layout)
    header_height: int = 50
    left_toolbar_width: int = 50
    right_toolbar_width: int = 50
    layers_panel_height: int = 672
    # Scaling
    content_scale: float = 0.9  # 90% of canvas area

    @property
    def canvas_left(self) -> int:
        return self.left_toolbar_width

    @property
    def canvas_top(self) -> int:
        return self.header_height

    @property
    def canvas_right(self) -> int:
        return self.width - self.right_toolbar_width

    @property
    def canvas_bottom(self) -> int:
        return self.height - self.layers_panel_height

    @property
    def canvas_width(self) -> int:
        return self.canvas_right - self.canvas_left

    @property
    def canvas_height(self) -> int:
        return self.canvas_bottom - self.canvas_top



# ... imports ...


# Protocol for Compositing Backend
class CompositingBackend(ABC):
    @abstractmethod
    def copy(self, image: Any) -> Any:
        pass

    @abstractmethod
    def resize(self, image: Any, size: tuple[int, int]) -> Any:
        pass

    @abstractmethod
    def paste(self, target: Any, source: Any, pos: tuple[int, int]) -> None:
        """Paste source onto target at pos (in-place)."""
        pass

    @abstractmethod
    def get_size(self, image: Any) -> tuple[int, int]:
        """Return (width, height)."""
        pass

    @abstractmethod
    def is_rgba(self, image: Any) -> bool:
        pass

    @abstractmethod
    def to_device(self, image: Any) -> Any:
        """Convert image to backend-specific format/device."""
        pass


# PillowBackend removed - moved to adapters.driven.renderers.pillow_backend
# Domain must not depend on Infrastructure.


class PipelineManager:
    """
    Unified compositing manager with pluggable backend.
    """

    def __init__(
        self, config: CompositeConfig | None = None, backend: CompositingBackend | None = None
    ):
        self.config = config or CompositeConfig()
        if backend is None:
            raise ValueError(
                "CompositingBackend implementation must be provided via Dependency Injection."
            )
        self.backend = backend

    def compose_frame(
        self,
        static_ui: Any,
        psd_content: Any,
    ) -> Any:
        """
        Compose frame using configured backend.
        Math is shared -> 100% Logic Match.
        """
        cfg = self.config
        backend = self.backend

        # Start with copy of static UI
        frame = backend.copy(static_ui)

        # Calculate scaling (Shared Logic)
        cw, ch = backend.get_size(psd_content)
        scale = min(cfg.canvas_width / cw, cfg.canvas_height / ch) * cfg.content_scale
        nw, nh = int(cw * scale), int(ch * scale)

        # Resize Content
        resized = backend.resize(psd_content, (nw, nh))

        # Center in canvas (Shared Logic)
        ix = cfg.canvas_left + (cfg.canvas_width - nw) // 2
        iy = cfg.canvas_top + (cfg.canvas_height - nh) // 2

        # Paste
        backend.paste(frame, resized, (ix, iy))

        return frame

    def iterate_frames(
        self,
        static_ui: Any,
        timeline: Any,
        anim_controller: Any,
        compositor: Any,
        find_layer_fn: Callable[..., Any],
        progress_callback: Callable[[int, int], None] | None = None,
        cursor_overlay: Any | None = None,  # New: CursorOverlay instance
    ) -> Iterator[tuple[int, Any]]:
        """Yields composited frames (backend-specific type)."""
        total_frames = int(timeline.total_duration * self.config.fps)

        # 1. Convert Static UI to Backend Device (ONCE)
        static_ui = self.backend.to_device(static_ui)

        for frame_num, timestamp in timeline.iterate_frames(self.config.fps):
            # Update animation state for each action at current timestamp
            current_actions = timeline.get_actions_at(timestamp)
            for action in current_actions:
                if action.duration > 0:
                    progress = (timestamp - action.start_time) / action.duration
                    progress = max(0.0, min(1.0, progress))
                else:
                    progress = 1.0
                anim_controller.update(action, progress)

            layer_states = {
                action.layer_id: anim_controller.get_layer_state(action.layer_id)
                for action in timeline.actions
                if anim_controller.get_layer_state(action.layer_id)
            }

            # Compose PSD content
            psd_content = compositor.compose_psd_content(layer_states, find_layer_fn)

            # 2. Convert PSD Content to Backend Device (Per Frame)
            psd_content = self.backend.to_device(psd_content)

            # Compose final frame using shared algorithm
            frame = self.compose_frame(static_ui, psd_content)

            # 3. Apply Cursor Overlay (Post-Compositing)
            if cursor_overlay and hasattr(anim_controller, "cursor_position"):
                cursor_pos = anim_controller.cursor_position
                if cursor_pos is not None:
                    cursor_type = (
                        "brush"
                        if any(
                            getattr(s, "reveal_progress", 0) > 0
                            and getattr(s, "reveal_progress", 1) < 1.0
                            for s in layer_states.values()
                        )
                        else "hand"
                    )
                    frame = cursor_overlay.overlay_cursor(frame, cursor_pos, cursor_type, True)

            if progress_callback and frame_num % 30 == 0:
                progress_callback(frame_num, total_frames)

            yield frame_num, frame

    def get_scale_params(self, content_size: tuple[int, int]) -> tuple[int, int, int, int]:
        """
        Get scaling parameters for given content size.

        Returns:
            (new_width, new_height, x_offset, y_offset)
        """
        cfg = self.config
        cw, ch = content_size

        scale = min(cfg.canvas_width / cw, cfg.canvas_height / ch) * cfg.content_scale
        nw, nh = int(cw * scale), int(ch * scale)

        ix = cfg.canvas_left + (cfg.canvas_width - nw) // 2
        iy = cfg.canvas_top + (cfg.canvas_height - nh) // 2

        return nw, nh, ix, iy
