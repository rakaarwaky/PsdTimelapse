from enum import Enum


class SequencingStrategy(Enum):
    """How to sequence multiple layer animations."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    STAGGERED = "staggered"
