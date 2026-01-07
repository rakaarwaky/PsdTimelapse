"""
MediaOutputPath Value Object: Immutable path structure for media output.
Generates standardized paths for all render output types.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# Frame naming convention: 5-digit padding
FRAME_PATTERN = "frame_{:05d}.exr"
PREVIEW_FILENAME = "preview.mp4"
MANIFEST_FILENAME = "_manifest.json"
FINAL_VIDEO_FILENAME = "output.mp4"


@dataclass(frozen=True)
class MediaOutputPath:
    """
    Immutable path structure for media output.
    Generates all paths relative to project root.
    """

    base_path: str
    project_id: str

    def __post_init__(self):
        if not str(self.base_path).strip():
            raise ValueError("Base path cannot be empty")
        if not self.project_id or not self.project_id.strip():
            raise ValueError("Project ID cannot be empty")

    # ============================================================
    # Project Root
    # ============================================================

    @property
    def project_root(self) -> Path:
        """Root folder for this project."""
        return Path(self.base_path) / self.project_id

    @property
    def manifest_path(self) -> Path:
        """Path to project manifest file."""
        return self.project_root / MANIFEST_FILENAME

    # ============================================================
    # Layout Paths
    # ============================================================

    @property
    def layout_dir(self) -> Path:
        """Directory for layout render output."""
        return self.project_root / "layout"

    def layout_frame_path(self, frame_number: int) -> Path:
        """Path for specific layout frame."""
        return self.layout_dir / FRAME_PATTERN.format(frame_number)

    # ============================================================
    # UI Paths
    # ============================================================

    @property
    def ui_dir(self) -> Path:
        """Directory for UI render output."""
        return self.project_root / "ui"

    def ui_frame_path(self, frame_number: int) -> Path:
        """Path for specific UI overlay frame."""
        return self.ui_dir / f"overlay_{frame_number:05d}.exr"

    # ============================================================
    # Animation Paths (per layer)
    # ============================================================

    @property
    def animation_dir(self) -> Path:
        """Root directory for all layer animations."""
        return self.project_root / "animation"

    def animation_layer_dir(self, layer_name: str) -> Path:
        """Directory for specific layer animation."""
        return self.animation_dir / self._sanitize_name(layer_name)

    def animation_frames_dir(self, layer_name: str) -> Path:
        """Directory for layer animation EXR frames (cache)."""
        return self.animation_layer_dir(layer_name) / "frames"

    def animation_frame_path(self, layer_name: str, frame_number: int) -> Path:
        """Path for specific animation frame."""
        return self.animation_frames_dir(layer_name) / FRAME_PATTERN.format(frame_number)

    def animation_preview_path(self, layer_name: str) -> Path:
        """Path for layer preview MP4 (NOT deleted after final)."""
        return self.animation_layer_dir(layer_name) / PREVIEW_FILENAME

    # ============================================================
    # Final Paths
    # ============================================================

    @property
    def final_dir(self) -> Path:
        """Directory for final composited output."""
        return self.project_root / "final"

    @property
    def final_frames_dir(self) -> Path:
        """Directory for final EXR frames (cache)."""
        return self.final_dir / "frames"

    def final_frame_path(self, frame_number: int) -> Path:
        """Path for specific final frame."""
        return self.final_frames_dir / FRAME_PATTERN.format(frame_number)

    @property
    def final_video_path(self) -> Path:
        """Path for final composited video (NOT deleted)."""
        return self.final_dir / FINAL_VIDEO_FILENAME

    # ============================================================
    # Test Output Paths (for scenario tests)
    # ============================================================

    @property
    def tests_dir(self) -> Path:
        """Root directory for all test outputs."""
        return self.project_root / "tests"

    @property
    def unit_test_dir(self) -> Path:
        """Directory for unit test outputs."""
        return self.tests_dir / "unit"

    @property
    def integration_test_dir(self) -> Path:
        """Directory for integration test outputs."""
        return self.tests_dir / "integration"

    @property
    def visual_test_dir(self) -> Path:
        """Directory for visual test outputs."""
        return self.tests_dir / "visual"

    @property
    def benchmark_test_dir(self) -> Path:
        """Directory for benchmark test outputs."""
        return self.tests_dir / "benchmark"

    def test_output_path(self, test_type: str, test_name: str) -> Path:
        """Get output path for a specific test."""
        type_dirs = {
            "unit": self.unit_test_dir,
            "integration": self.integration_test_dir,
            "visual": self.visual_test_dir,
            "benchmark": self.benchmark_test_dir,
        }
        base_dir = type_dirs.get(test_type, self.tests_dir)
        return base_dir / self._sanitize_name(test_name)

    # ============================================================
    # Utilities
    # ============================================================

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Sanitize layer name for filesystem compatibility."""
        # Replace spaces and special chars with underscores
        sanitized = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        return sanitized.lower().strip("_")

    def ensure_structure(self) -> None:
        """Create the entire folder structure including test folders."""
        dirs = [
            self.layout_dir,
            self.ui_dir,
            self.animation_dir,  # Animation root folder
            self.final_frames_dir,
            # Test output folders
            self.unit_test_dir,
            self.integration_test_dir,
            self.visual_test_dir,
            self.benchmark_test_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def ensure_layer_structure(self, layer_name: str) -> None:
        """Create folder structure for a specific layer."""
        self.animation_frames_dir(layer_name).mkdir(parents=True, exist_ok=True)
