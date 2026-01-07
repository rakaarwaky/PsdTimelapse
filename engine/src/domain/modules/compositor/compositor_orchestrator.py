from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ...value_objects.compositor.compositor_dependencies import CompositorDependencies
from ...value_objects.configs import CompositorConfig

if TYPE_CHECKING:
    from PIL import Image

    from domain.ports.media.image_processing_port import (  # type: ignore[import-not-found]
        ImageProcessingPort,  # type: ignore[unused-ignore]
    )

    from ...entities.layer_entity import LayerEntity
    from ...entities.viewport_entity import ViewportEntity
    from ...entities.world_entity import WorldEntity
    from .orchestrators.compositor_module import FrameCompositor
    from .services.layer_cache_module import LayerCache

from .orchestrators.compositor_module import FrameCompositor
from .services.layer_cache_module import LayerCache


class CompositorOrchestrator:
    """
    High-level compositor that coordinates all composition components.

    Provides a unified API for frame composition with lazy initialization
    of internal components to prevent circular imports.

    Usage:
        orchestrator = create_compositor(world, viewport)
        frame = orchestrator.compose_frame(layer_states, find_layer_fn)
    """

    def __init__(
        self,
        world: WorldEntity,
        viewport: ViewportEntity,
        config: CompositorConfig | None = None,
        image_processor: ImageProcessingPort | None = None,
        dependencies: CompositorDependencies | None = None,
    ):
        self.config = config or CompositorConfig()
        self.dependencies = dependencies or CompositorDependencies()
        self._world = world
        self._viewport = viewport
        self._image_processor = image_processor
        self._compositor: FrameCompositor | None = None
        self._cache: LayerCache | None = None

    @property
    def compositor(self) -> FrameCompositor:
        """Lazy-loaded FrameCompositor instance."""
        if self._compositor is None:
            self._compositor = FrameCompositor(
                self._world,
                self._viewport,
                image_processor=self._image_processor,
                dependencies=self.dependencies,
            )
        return self._compositor

    @property
    def cache(self) -> LayerCache:
        """Lazy-loaded LayerCache instance."""
        if self._cache is None:
            self._cache = LayerCache()
        return self._cache

    def compose_frame(
        self,
        layer_states: dict[str, Any],
        find_layer_fn: Callable[[str], LayerEntity | None],
    ) -> Image:  # type: ignore[valid-type]
        """
        Compose single frame with current settings.

        Args:
            layer_states: Dict mapping layer_id to LayerAnimState
            find_layer_fn: Function to retrieve LayerEntity by ID

        Returns:
            Composited PIL Image
        """
        return self.compositor.compose_psd_content(layer_states, find_layer_fn)

    def clear_cache(self) -> None:
        """Clear all cached layers."""
        self.compositor.clear_cache()  # type: ignore[attr-defined]
        if self._cache:
            self._cache.clear()

    def validate(self) -> bool:
        """Validate all components are properly initialized."""
        return self._world is not None and self._viewport is not None


# ============================================================
# Factory Functions
# ============================================================


def create_compositor(  # type: ignore[no-untyped-def]
    world: WorldEntity,
    viewport: ViewportEntity,
    image_processor: ImageProcessingPort | None = None,
    dependencies: CompositorDependencies | None = None,
    **config_kwargs,
) -> CompositorOrchestrator:
    """
    Factory: Create compositor orchestrator with configuration.
    """
    config = CompositorConfig(**config_kwargs)
    return CompositorOrchestrator(
        world,
        viewport,
        config,
        image_processor=image_processor,
        dependencies=dependencies,
    )


def create_frame_compositor(
    world: WorldEntity,
    viewport: ViewportEntity,
    image_processor: ImageProcessingPort | None = None,
    dependencies: CompositorDependencies | None = None,
) -> FrameCompositor:
    """
    Factory: Create raw FrameCompositor (backward compatible).
    """

    return FrameCompositor(
        world,
        viewport,
        image_processor=image_processor,
        dependencies=dependencies,
    )
