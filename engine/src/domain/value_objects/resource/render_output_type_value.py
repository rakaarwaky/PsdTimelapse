"""
RenderOutputType Value Object: Enum for render output types.
Defines the different categories of render outputs and their cache behavior.
"""

from dataclasses import dataclass
from enum import Enum


class RenderOutputType(Enum):
    """Type of render output with associated metadata."""

    LAYOUT = "layout"
    UI = "ui"
    ANIMATION = "animation"
    FINAL = "final"


@dataclass(frozen=True)
class RenderOutputMeta:
    """Metadata for render output type behavior."""

    output_type: RenderOutputType
    is_cache: bool
    extension: str

    @classmethod
    def layout(cls) -> "RenderOutputMeta":
        """Layout pass - cache, EXR format."""
        return cls(RenderOutputType.LAYOUT, is_cache=True, extension=".exr")

    @classmethod
    def ui(cls) -> "RenderOutputMeta":
        """UI overlay pass - cache, EXR format."""
        return cls(RenderOutputType.UI, is_cache=True, extension=".exr")

    @classmethod
    def animation_frames(cls) -> "RenderOutputMeta":
        """Animation frames - cache, EXR format."""
        return cls(RenderOutputType.ANIMATION, is_cache=True, extension=".exr")

    @classmethod
    def animation_preview(cls) -> "RenderOutputMeta":
        """Animation preview - NOT cache (kept for debugging), MP4 format."""
        return cls(RenderOutputType.ANIMATION, is_cache=False, extension=".mp4")

    @classmethod
    def final_frames(cls) -> "RenderOutputMeta":
        """Final composited frames - cache, EXR format."""
        return cls(RenderOutputType.FINAL, is_cache=True, extension=".exr")

    @classmethod
    def final_video(cls) -> "RenderOutputMeta":
        """Final video - NOT cache (kept), MP4 format."""
        return cls(RenderOutputType.FINAL, is_cache=False, extension=".mp4")
