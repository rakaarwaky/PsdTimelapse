"""
Layer Manifest Module
=====================
Data structures for layer rendering manifests.
"""

from dataclasses import dataclass, field


@dataclass
class LayerManifest:
    """Manifest for a single rendered layer."""

    layer_id: str
    folder_path: str
    total_frames: int
    visible_range: tuple[int, int]
    hold_ranges: list[tuple[int, int]] = field(default_factory=list)
    blank_frames: int = 0


@dataclass
class RenderManifest:
    """Master manifest for the entire render job."""

    total_frames: int
    fps: int
    canvas_size: tuple[int, int]
    layers: list[LayerManifest] = field(default_factory=list)
