from typing import Any, Protocol

# NOTE: Strategy imports removed - injected via constructor (Blind Logic)
# from ..strategies.drag_strategy_module import animate_drag
# from ..strategies.brush_strategy_module import animate_brush
from ....value_objects.animation import BrushTool, EasingCurve, EasingType
from ....value_objects.animation.layer_anim_state import LayerAnimState
from ....value_objects.geometry import Vector2
from ...script_director import Action, ActionType


# Protocol definitions for DI (Blind Logic)
class DragAnimator(Protocol):
    def __call__(
        self,
        state: LayerAnimState,
        target_pos: Vector2,
        eased_progress: float,
        raw_progress: float,
        viewport_width: int,
        viewport_height: int,
        direction: str = "auto",
    ) -> None: ...


class BrushAnimator(Protocol):
    def __call__(
        self, state: LayerAnimState, progress: float, brush_tool: BrushTool | None = None
    ) -> None: ...


class PathGenerator(Protocol):
    """Protocol for path generation (DI)."""

    def __call__(
        self,
        target_position: Vector2,
        viewport_width: int,
        viewport_height: int,
        direction: str = "auto",
        **kwargs,
    ) -> Any: ...


class AnimationController:
    """
    Animation Controller (Level 1 Staff).

    REQUIRES: animate_drag and animate_brush to be injected by Orchestrator.
    This class is "Blind" - it doesn't know about strategy implementations.
    """

    def __init__(
        self,
        viewport_width: int,
        viewport_height: int,
        animate_drag: DragAnimator | None = None,
        animate_brush: BrushAnimator | None = None,
        generate_drag_path: PathGenerator | None = None,
    ):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.layer_states: dict[str, LayerAnimState] = {}
        self.cursor_position: Vector2 | None = None

        # Injected strategies (Blind Logic)
        self._animate_drag = animate_drag
        self._animate_brush = animate_brush
        self._generate_drag_path = generate_drag_path

    def initialize_layers(self, layers: list[Any]) -> None:
        """
        Initialize animation state for layers.
        Args:
            layers: List of LayerEntity objects OR layer ID strings.
        """
        for layer in layers:
            # Support both LayerEntity objects and raw string IDs
            lid = layer if isinstance(layer, str) else layer.id
            if lid not in self.layer_states:
                if isinstance(layer, str):
                    # String ID mode: initialize with default values
                    self.layer_states[lid] = LayerAnimState(
                        position=Vector2(0, 0), opacity=1.0, visible=True
                    )
                else:
                    # LayerEntity mode: use actual layer properties
                    self.layer_states[lid] = LayerAnimState(
                        position=layer.position,
                        opacity=layer.opacity.value,
                        visible=layer.visible,
                        bounds=layer.bounds,
                    )

    def reset_frame_state(self) -> None:
        """
        Reset transient per-frame state (like velocity).
        Should be called once at the start of each frame.
        """
        for state in self.layer_states.values():
            state.velocity = Vector2(0, 0)

    def get_layer_state(self, layer_id: str) -> LayerAnimState | None:
        return self.layer_states.get(layer_id)

    def update(self, action: Action | None, progress: float) -> None:
        if not action:
            return

        # Calculate Progress
        # Calculate Progress using EasingCurve
        # TODO: Get EasingType from Action (Task for user to add Easing to Action?)
        # For now, default to EASE_OUT
        easing = EasingCurve(EasingType.EASE_OUT)
        eased = easing.apply(progress)

        target_layer = str(action.layer_id)
        if target_layer not in self.layer_states:
            return

        state = self.layer_states[target_layer]
        if hasattr(action, "brush_path_type"):
            # Ensure we are using the VO enum
            # If action has string, we might need mapping,
            # but let's assume it passes VO or compatible
            state.brush_path_type = action.brush_path_type

        if action.action_type == ActionType.DRAG:
            # Validate strategy is injected
            if self._animate_drag is None:
                raise ValueError("animate_drag strategy must be injected via constructor")

            # Determine direction from SmartAction
            direction = "auto"
            if hasattr(action, "path_direction"):
                # Map PathDirection to concrete entry side
                # Vertical Path -> Enter from Top (Slide Down)
                # Horizontal Path -> Enter from Left (Slide Right)
                p_dir = str(action.path_direction)
                if "vertical" in p_dir.lower():
                    direction = "top"
                elif "horizontal" in p_dir.lower():
                    direction = "left"

            # Generate path if not already set (Orchestration: inject tools)
            if not state.path and self._generate_drag_path:
                state.path = self._generate_drag_path(
                    action.target_position,
                    self.viewport_width,
                    self.viewport_height,
                    direction=direction,
                )

            self._animate_drag(
                state,
                action.target_position,
                eased,
                progress,
                self.viewport_width,
                self.viewport_height,
                direction=direction,
            )
            # Update Cursor to match dragged item
            self.cursor_position = state.position

        elif action.action_type == ActionType.BRUSH:
            # Validate strategy is injected
            if self._animate_brush is None:
                raise ValueError("animate_brush strategy must be injected via constructor")

            # TODO: Get BrushTool from Action or Config
            brush_tool = BrushTool(size_px=100.0)  # Default for now
            self._animate_brush(state, progress, brush_tool=brush_tool)
            # Set direction from SmartAction if available
            if hasattr(action, "path_direction"):
                # Convert enum to string value
                direction = (
                    action.path_direction.value
                    if hasattr(action.path_direction, "value")
                    else str(action.path_direction)
                )
                state.reveal_direction = direction
            else:
                state.reveal_direction = "horizontal"
