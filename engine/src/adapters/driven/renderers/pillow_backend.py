from typing import Any

from PIL import Image

try:
    from ....domain.modules.pipeline_manager.orchestrator.pipeline_manager_module import (
        CompositingBackend,
    )
except ImportError:
    # Fallback for relative import resolution issues during dev/test if package structure varies
    from domain.modules.pipeline_manager.orchestrator.pipeline_manager_module import (  # type: ignore[import-not-found,no-redef]
        CompositingBackend,
    )


class PillowBackend(CompositingBackend):
    """Reference implementation using PIL."""

    def copy(self, image: Any) -> Any:
        return image.copy()

    def resize(self, image: Any, size: tuple[int, int]) -> Any:
        return image.resize(size, Image.Resampling.LANCZOS)

    def paste(self, target: Any, source: Any, pos: tuple[int, int]) -> None:
        if source.mode == "RGBA":
            target.paste(source, pos, source)
        else:
            target.paste(source, pos)

    def get_size(self, image: Any) -> tuple[int, int]:
        return image.size  # type: ignore[no-any-return]

    def is_rgba(self, image: Any) -> bool:
        return image.mode == "RGBA"  # type: ignore[no-any-return]

    def to_device(self, image: Any) -> Any:
        # PIL is already on host
        return image
