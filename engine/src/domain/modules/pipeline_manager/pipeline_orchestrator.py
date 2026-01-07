from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ...value_objects.configs import (
    EngineProgress,
    PipelineConfig,
    RenderConfig,
    RenderMode,
)

if TYPE_CHECKING:
    from ...entities.world_entity import WorldEntity
    from .orchestrator.director_engine_module import DirectorEngine


class PipelineOrchestrator:
    """
    Orchestrates the rendering pipeline, enforcing validation and work distribution.

    Responsibilities:
    1. Orchestration: Delegates tasks to Orchestrator, Rendering, and UI sub-modules.
    2. Validation: Ensures only valid Entities and Value Objects are passed.
    3. Management: Ensures no submodule is idle during its phase.
    """

    def __init__(  # type: ignore[no-untyped-def]
        self,
        config: PipelineConfig | None = None,
        **port_kwargs,
    ) -> None:
        self.config = config or PipelineConfig()

        # Lazy loaded components
        self._engine: DirectorEngine | None = None
        self._port_kwargs = port_kwargs
        self._progress_callback: Callable[[EngineProgress], None] | None = None

    @property
    def engine(self) -> DirectorEngine:
        """
        Access the core director engine.
        Auto-initializes the orchestrator submodule.
        """
        if self._engine is None:
            # Lazy import to avoid circular dependencies
            from .orchestrator.director_engine_module import DirectorEngine

            self._engine = DirectorEngine(**self._port_kwargs)
        return self._engine

    def load_project(self, psd_path: str) -> WorldEntity:
        """
        Load and validate a project.

        Delegates to: Orchestrator (DirectorEngine)
        """
        if not psd_path.endswith(".psd"):
            raise ValueError(f"Invalid project format: {psd_path}. Expected .psd file.")

        world = self.engine.load_project(psd_path)

        # Validation: Ensure we got a valid WorldEntity
        from ...entities.world_entity import WorldEntity

        if not isinstance(world, WorldEntity):
            raise TypeError(f"Expected WorldEntity, got {type(world)}")

        return world

    def run(self, output_path: str, **kwargs) -> str:  # type: ignore[no-untyped-def]
        """
        Run the full render pipeline.

        Delegates to:
        1. Orchestrator (Planning)
        2. Rendering (Execution)
        3. UI (Progress)
        """
        # 1. Configuration
        render_config = RenderConfig(
            output_path=output_path,
            fps=kwargs.get("fps", self.config.fps),
            width=kwargs.get("width", self.config.width),
            height=kwargs.get("height", self.config.height),
            use_gpu=(self.config.mode == RenderMode.GPU),
        )

        # 2. Strategy Selection (Load Balancing)
        if self.config.mode == RenderMode.GPU:
            return self.engine.run_gpu(render_config)
        elif self.config.mode == RenderMode.OPTIMIZED:
            return self.engine.run_optimized(render_config)
        else:
            return self.engine.run(render_config)


def create_pipeline(mode: str = "optimized", **kwargs) -> PipelineOrchestrator:  # type: ignore[no-untyped-def]
    render_mode = RenderMode(mode.lower())

    # Extract config
    config_fields = {f.name for f in PipelineConfig.__dataclass_fields__.values()}
    config_args = {k: v for k, v in kwargs.items() if k in config_fields}
    port_args = {k: v for k, v in kwargs.items() if k not in config_fields}

    config_args["mode"] = render_mode
    return PipelineOrchestrator(PipelineConfig(**config_args), **port_args)
