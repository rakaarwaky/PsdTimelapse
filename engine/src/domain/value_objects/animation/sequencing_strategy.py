"""
Sequencing Strategy: Enum for layer animation sequencing.
"""

from enum import Enum


class SequencingStrategy(Enum):
    """How to sequence multiple layer animations."""

    SEQUENTIAL = "sequential"  # One after another
    PARALLEL = "parallel"  # All at once
    STAGGERED = "staggered"  # Overlapping with delay
