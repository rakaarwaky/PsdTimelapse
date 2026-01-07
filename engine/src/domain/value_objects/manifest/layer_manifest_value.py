from dataclasses import dataclass, field
from typing import Any


@dataclass
class LayerManifest:
    """Manifest entry for a single layer."""

    id: str
    name: str
    sequence_folder: str
    animation_type: str  # "drag" or "brush"
    visible_range: tuple[int, int]  # (start_frame, end_frame)
    hold_frames: list[tuple[int, int]] = field(default_factory=list)  # [(start, end), ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "sequence_folder": self.sequence_folder,
            "animation_type": self.animation_type,
            "visible_range": list(self.visible_range),
            "hold_frames": [list(hf) for hf in self.hold_frames],
        }
