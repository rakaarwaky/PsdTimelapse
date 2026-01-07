"""
Media Output Service Module
===========================

Service for managing media output paths, folder structure, and cache cleanup.
Coordinates standardized output across all render passes.
"""

from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ....value_objects.configs import MediaOutputConfig
from ....value_objects.resource import MediaOutputPath

if TYPE_CHECKING:
    pass


@dataclass
class ProjectManifest:
    """Manifest data for a render project."""

    project_id: str
    created_at: str
    fps: int
    width: int
    height: int
    layers: list[str] = field(default_factory=list)
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectManifest:
        return cls(**data)


class MediaOutputService:
    """
    Service for managing media output structure and cleanup.

    Responsibilities:
    - Create project folder structure
    - Generate standardized paths
    - Manage project manifest
    - Cleanup cache after final render
    """

    def __init__(self, config: MediaOutputConfig | None = None):
        """
        Initialize media output service.

        Args:
            config: Media output configuration (uses defaults if None)
        """
        self._config = config or MediaOutputConfig()

    @property
    def config(self) -> MediaOutputConfig:
        return self._config

    # ============================================================
    # Project Management
    # ============================================================

    def create_project(self, project_id: str | None = None) -> MediaOutputPath:
        """
        Create a new project with folder structure.

        Args:
            project_id: Optional custom ID, generates UUID if None

        Returns:
            MediaOutputPath for the new project
        """
        if project_id is None:
            project_id = self._generate_project_id()

        output_path = MediaOutputPath(base_path=self._config.base_path, project_id=project_id)

        # Create folder structure
        output_path.ensure_structure()

        # Create initial manifest
        manifest = ProjectManifest(
            project_id=project_id,
            created_at=datetime.now().isoformat(),
            fps=self._config.fps,
            width=self._config.final_width,
            height=self._config.final_height,
        )
        self._save_manifest(output_path, manifest)

        return output_path

    def get_project(self, project_id: str) -> MediaOutputPath:
        """Get MediaOutputPath for existing project."""
        return MediaOutputPath(base_path=self._config.base_path, project_id=project_id)

    # ============================================================
    # Layer Structure
    # ============================================================

    def ensure_layer(self, output_path: MediaOutputPath, layer_name: str) -> Path:
        """
        Ensure layer folder structure exists.

        Args:
            output_path: Project output path
            layer_name: Name of the layer

        Returns:
            Path to layer frames directory
        """
        output_path.ensure_layer_structure(layer_name)

        # Update manifest with layer
        manifest = self._load_manifest(output_path)
        if manifest and layer_name not in manifest.layers:
            manifest.layers.append(layer_name)
            self._save_manifest(output_path, manifest)

        return output_path.animation_frames_dir(layer_name)

    # ============================================================
    # Cache Cleanup
    # ============================================================

    def cleanup_cache(self, output_path: MediaOutputPath) -> list[Path]:
        """
        Remove all cache files after final render.
        Keeps: preview.mp4 per layer, final output.mp4
        Deletes: All .exr files, manifest

        Args:
            output_path: Project output path

        Returns:
            List of deleted paths
        """
        deleted: list[Path] = []

        # Delete layout folder (all EXR cache)
        if output_path.layout_dir.exists():
            shutil.rmtree(output_path.layout_dir)
            deleted.append(output_path.layout_dir)

        # Delete UI folder (all EXR cache)
        if output_path.ui_dir.exists():
            shutil.rmtree(output_path.ui_dir)
            deleted.append(output_path.ui_dir)

        # Delete animation EXR frames (keep preview.mp4)
        animation_dir = output_path.project_root / "animation"
        if animation_dir.exists():
            for layer_dir in animation_dir.iterdir():
                if layer_dir.is_dir():
                    frames_dir = layer_dir / "frames"
                    if frames_dir.exists():
                        shutil.rmtree(frames_dir)
                        deleted.append(frames_dir)

        # Delete final frames (keep output.mp4)
        if output_path.final_frames_dir.exists():
            shutil.rmtree(output_path.final_frames_dir)
            deleted.append(output_path.final_frames_dir)

        # Delete manifest
        if output_path.manifest_path.exists():
            output_path.manifest_path.unlink()
            deleted.append(output_path.manifest_path)

        return deleted

    def cleanup_project(self, output_path: MediaOutputPath) -> None:
        """
        Completely remove a project folder.
        Use with caution - deletes everything including final output.
        """
        if output_path.project_root.exists():
            shutil.rmtree(output_path.project_root)

    # ============================================================
    # Manifest Management
    # ============================================================

    def _save_manifest(self, output_path: MediaOutputPath, manifest: ProjectManifest) -> None:
        """Save manifest to project folder."""
        manifest_path = output_path.manifest_path
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w") as f:
            json.dump(manifest.to_dict(), f, indent=2)

    def _load_manifest(self, output_path: MediaOutputPath) -> ProjectManifest | None:
        """Load manifest from project folder."""
        manifest_path = output_path.manifest_path
        if not manifest_path.exists():
            return None
        with open(manifest_path) as f:
            data = json.load(f)
            return ProjectManifest.from_dict(data)

    def update_manifest_status(self, output_path: MediaOutputPath, status: str) -> None:
        """Update project status in manifest."""
        manifest = self._load_manifest(output_path)
        if manifest:
            manifest.status = status
            self._save_manifest(output_path, manifest)

    # ============================================================
    # Utilities
    # ============================================================

    @staticmethod
    def _generate_project_id() -> str:
        """Generate unique project ID with timestamp prefix."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = uuid.uuid4().hex[:8]
        return f"{timestamp}_{short_uuid}"
