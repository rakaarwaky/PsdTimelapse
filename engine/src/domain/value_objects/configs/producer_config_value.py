"""
Producer Configuration Value Object.
Immutable configuration for ProducerEngine.
"""

from dataclasses import dataclass

from ..animation import SequencingStrategy


@dataclass(frozen=True)
class ProducerConfig:
    """Configuration for the ProducerEngine."""

    output_path: str = "./output.mp4"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    strategy: SequencingStrategy = SequencingStrategy.STAGGERED
    use_gpu: bool = False
