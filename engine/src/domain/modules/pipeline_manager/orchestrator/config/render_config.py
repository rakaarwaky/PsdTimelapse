from dataclasses import dataclass


@dataclass
class RenderOrchestratorConfig:
    """Configuration for render orchestration."""

    fps: int = 30
    output_dir: str = "./output"
    enable_exr: bool = True
    enable_video: bool = True
    use_symlinks_for_hold: bool = True
