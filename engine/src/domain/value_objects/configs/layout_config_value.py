"""
Layout Configuration Value Object.
Immutable configuration for layout manager operations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutConfig:
    """Configuration for layout manager operations."""

    default_zoom: float = 1.0
    center_on_content: bool = True
