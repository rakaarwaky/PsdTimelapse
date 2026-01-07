"""
FilePath Value Object: Immutable validated file path.
Part of resource category - file and path handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

VIDEO_EXTENSIONS: set[str] = {".mp4", ".webm", ".avi", ".mov", ".mkv"}
IMAGE_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
PSD_EXTENSIONS: set[str] = {".psd", ".psb"}


@dataclass(frozen=True)
class FilePath:
    """Immutable validated file path."""

    path: str

    def __post_init__(self) -> None:
        if not self.path or not self.path.strip():
            raise ValueError("File path cannot be empty")

    @property
    def _path_obj(self) -> Path:
        return Path(self.path)

    @property
    def extension(self) -> str:
        return self._path_obj.suffix.lower()

    @property
    def stem(self) -> str:
        return self._path_obj.stem

    @property
    def filename(self) -> str:
        return self._path_obj.name

    @property
    def directory(self) -> str:
        return str(self._path_obj.parent)

    @property
    def absolute(self) -> str:
        return str(self._path_obj.absolute())

    def is_video(self) -> bool:
        return self.extension in VIDEO_EXTENSIONS

    def is_image(self) -> bool:
        return self.extension in IMAGE_EXTENSIONS

    def is_psd(self) -> bool:
        return self.extension in PSD_EXTENSIONS

    def with_extension(self, ext: str) -> FilePath:
        if not ext.startswith("."):
            ext = f".{ext}"
        return FilePath(str(self._path_obj.with_suffix(ext)))

    def with_suffix_added(self, suffix: str) -> FilePath:
        new_stem = f"{self.stem}{suffix}"
        new_path = self._path_obj.with_stem(new_stem)
        return FilePath(str(new_path))

    def exists(self) -> bool:
        return self._path_obj.exists()

    def is_file(self) -> bool:
        return self._path_obj.is_file()

    def is_directory(self) -> bool:
        return self._path_obj.is_dir()

    def ensure_parent_exists(self) -> None:
        self._path_obj.parent.mkdir(parents=True, exist_ok=True)

    def __truediv__(self, other: str) -> FilePath:
        return FilePath(str(self._path_obj / other))

    def __str__(self) -> str:
        return self.path
