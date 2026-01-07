"""
Script Director Configuration Value Object.
Immutable configuration for script director operations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScriptDirectorConfig:
    """Configuration for script director operations."""

    default_strategy: str = "STAGGERED"
    default_action_duration: float = 2.0
    default_stagger_delay: float = 0.3
    auto_classify_actions: bool = True
