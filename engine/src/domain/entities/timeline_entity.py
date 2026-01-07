from collections.abc import Iterator
from dataclasses import dataclass, field

from ..value_objects.animation.timing_constants import OUTRO_DURATION
from .action_entity import Action, CameraAction


@dataclass
class TimelineEntity:
    """Complete animation timeline."""

    actions: list[Action] = field(default_factory=list)
    camera_actions: list[CameraAction] = field(default_factory=list)

    @property
    def total_duration(self) -> float:
        """Get total timeline duration."""
        if not self.actions and not self.camera_actions:
            return 0.0

        last_action_end = max((a.end_time for a in self.actions), default=0.0)
        last_camera_end = max((a.end_time for a in self.camera_actions), default=0.0)
        return max(last_action_end, last_camera_end) + OUTRO_DURATION

    def add_action(self, action: Action) -> None:
        """Add an action to the timeline."""
        self.actions.append(action)

    def add_camera_action(self, action: CameraAction) -> None:
        """Add a camera action."""
        self.camera_actions.append(action)

    def get_actions_at(self, time: float) -> list[Action]:
        """Get all actions active at a specific time."""
        return [a for a in self.actions if a.start_time <= time < a.end_time]

    def get_camera_at(self, time: float) -> CameraAction | None:
        """Get camera action active at a specific time."""
        for action in self.camera_actions:
            if action.start_time <= time < action.end_time:
                return action
        return None

    def iterate_frames(self, fps: int = 30) -> Iterator[tuple[int, float]]:
        """
        Iterate frame numbers and their timestamps.

        Yields:
            (frame_number, timestamp_seconds)
        """
        total_frames = int(self.total_duration * fps)
        for f in range(total_frames):
            yield f, f / fps
