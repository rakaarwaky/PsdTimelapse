"""
DirectorProfile Value Object: Configuration for AI director behavior.
Part of animation category - rhythm and variation control.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class RhythmPace(Enum):
    """Pace settings for animation rhythm."""

    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


@dataclass(frozen=True)
class DirectorProfile:
    """
    Immutable configuration for AI Director behavior.
    Controls rhythm, variation, and timing decisions.
    """

    name: str
    pace: RhythmPace = RhythmPace.NORMAL

    # Constraints
    min_layer_duration: float = 2.0
    max_layer_duration: float = 8.0

    # Logic Weights
    transition_style: str = "mix"
    prefer_variation: bool = True
    max_consecutive_same_actions: int = 2

    # Randomness
    chaos_factor: float = 0.1

    # Class-level presets (assigned after class definition)
    DEFAULT: ClassVar[DirectorProfile]
    FAST_PACED: ClassVar[DirectorProfile]
    SLOW_CINEMATIC: ClassVar[DirectorProfile]

    def should_force_variation(self, current_same_action_count: int) -> bool:
        """Check if director should force action type change."""
        if not self.prefer_variation:
            return False
        return current_same_action_count >= self.max_consecutive_same_actions


# Presets
DirectorProfile.DEFAULT = DirectorProfile(name="default")
DirectorProfile.FAST_PACED = DirectorProfile(
    name="fast_paced", pace=RhythmPace.FAST, min_layer_duration=1.0, max_layer_duration=4.0
)
DirectorProfile.SLOW_CINEMATIC = DirectorProfile(
    name="slow_cinematic", pace=RhythmPace.SLOW, min_layer_duration=4.0, max_layer_duration=12.0
)
