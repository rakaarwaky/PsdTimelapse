from dataclasses import dataclass, field
from typing import Any

"""
Layer Manifest: IO data structures for layer rendering.
"""



@dataclass
class LayerManifest:
    """Render manifest for a single layer."""

    layer_id: str
    folder_path: str
    total_frames: int
    visible_range: tuple[int, int]  # (start_frame, end_frame)
    hold_ranges: list[tuple[int, int]] = field(default_factory=list)  # [(start, end), ...]
    blank_frames: int = 0  # Number of blank frames at start


@dataclass
class RenderManifest:
    """Complete render manifest."""

    total_frames: int
    fps: int
    canvas_size: tuple[int, int]  # (width, height)
    layers: list[LayerManifest] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_frames": self.total_frames,
            "fps": self.fps,
            "canvas_size": list(self.canvas_size),
            "layers": [
                {
                    "layer_id": lm.layer_id,
                    "folder_path": lm.folder_path,
                    "visible_range": list(lm.visible_range),
                    "hold_ranges": [list(hr) for hr in lm.hold_ranges],
                    "blank_frames": lm.blank_frames,
                }
                for lm in self.layers
            ],
        }
