import json
from dataclasses import dataclass, field
from typing import Any

from .layer_manifest_value import LayerManifest


@dataclass
class CompositorManifest:
    """Complete manifest for compositor."""

    total_frames: int
    fps: int
    duration_seconds: float
    layers: list[LayerManifest] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_frames": self.total_frames,
            "fps": self.fps,
            "duration_seconds": self.duration_seconds,
            "layers": [layer.to_dict() for layer in self.layers],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
