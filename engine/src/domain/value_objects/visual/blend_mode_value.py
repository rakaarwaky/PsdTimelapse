"""
BlendMode Value Object: Immutable blend mode for layer compositing.
Part of visual category - layer blending operations.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

# Constants
HALF_LUMINOSITY = 0.5


class BlendModeType(Enum):
    """Available blend mode types."""

    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    COLOR_DODGE = "color_dodge"
    COLOR_BURN = "color_burn"
    HARD_LIGHT = "hard_light"
    SOFT_LIGHT = "soft_light"
    DIFFERENCE = "difference"
    EXCLUSION = "exclusion"


def _clamp(v: float) -> float:
    """Clamp value to 0.0-1.0 range."""
    return max(0.0, min(1.0, v))


# --- Blending Strategy Functions ---


def _blend_normal(b: float, a: float) -> float:
    return a


def _blend_multiply(b: float, a: float) -> float:
    return _clamp(b * a)


def _blend_screen(b: float, a: float) -> float:
    return _clamp(1 - (1 - b) * (1 - a))


def _blend_overlay(b: float, a: float) -> float:
    if b < HALF_LUMINOSITY:
        return 2 * b * a
    return 1 - 2 * (1 - b) * (1 - a)


def _blend_darken(b: float, a: float) -> float:
    return min(b, a)


def _blend_lighten(b: float, a: float) -> float:
    return max(b, a)


def _blend_difference(b: float, a: float) -> float:
    return abs(b - a)


def _blend_exclusion(b: float, a: float) -> float:
    return _clamp(b + a - 2 * b * a)


# Map modes to per-channel functions.
# NOTE: Some modes like Color Dodge/Burn might need more complex logic.
# Left as TODO/Default for now to match previous impl.
_BLEND_STRATEGIES: dict[BlendModeType, Callable[[float, float], float]] = {
    BlendModeType.NORMAL: _blend_normal,
    BlendModeType.MULTIPLY: _blend_multiply,
    BlendModeType.SCREEN: _blend_screen,
    BlendModeType.OVERLAY: _blend_overlay,
    BlendModeType.DARKEN: _blend_darken,
    BlendModeType.LIGHTEN: _blend_lighten,
    BlendModeType.DIFFERENCE: _blend_difference,
    BlendModeType.EXCLUSION: _blend_exclusion,
    # Fallbacks
    BlendModeType.COLOR_DODGE: _blend_normal,
    BlendModeType.COLOR_BURN: _blend_normal,
    BlendModeType.HARD_LIGHT: _blend_overlay,
    BlendModeType.SOFT_LIGHT: _blend_overlay,
}


@dataclass(frozen=True)
class BlendMode:
    """Immutable blend mode for layer compositing."""

    mode: BlendModeType

    def blend_pixel(
        self, base: tuple[float, float, float], blend: tuple[float, float, float]
    ) -> tuple[float, float, float]:
        """Blend two RGB pixels (values 0.0-1.0)."""
        strategy = _BLEND_STRATEGIES.get(self.mode, _blend_normal)

        return (
            strategy(base[0], blend[0]),
            strategy(base[1], blend[1]),
            strategy(base[2], blend[2]),
        )

    def __str__(self) -> str:
        return self.mode.value

    # Class-level presets
    NORMAL: ClassVar[BlendMode]
    MULTIPLY: ClassVar[BlendMode]
    SCREEN: ClassVar[BlendMode]
    OVERLAY: ClassVar[BlendMode]
    DARKEN: ClassVar[BlendMode]
    LIGHTEN: ClassVar[BlendMode]
    COLOR_DODGE: ClassVar[BlendMode]
    COLOR_BURN: ClassVar[BlendMode]
    HARD_LIGHT: ClassVar[BlendMode]
    SOFT_LIGHT: ClassVar[BlendMode]
    DIFFERENCE: ClassVar[BlendMode]
    EXCLUSION: ClassVar[BlendMode]


# Initialize Presets
BlendMode.NORMAL = BlendMode(BlendModeType.NORMAL)
BlendMode.MULTIPLY = BlendMode(BlendModeType.MULTIPLY)
BlendMode.SCREEN = BlendMode(BlendModeType.SCREEN)
BlendMode.OVERLAY = BlendMode(BlendModeType.OVERLAY)
BlendMode.DARKEN = BlendMode(BlendModeType.DARKEN)
BlendMode.LIGHTEN = BlendMode(BlendModeType.LIGHTEN)
BlendMode.COLOR_DODGE = BlendMode(BlendModeType.COLOR_DODGE)
BlendMode.COLOR_BURN = BlendMode(BlendModeType.COLOR_BURN)
BlendMode.HARD_LIGHT = BlendMode(BlendModeType.HARD_LIGHT)
BlendMode.SOFT_LIGHT = BlendMode(BlendModeType.SOFT_LIGHT)
BlendMode.DIFFERENCE = BlendMode(BlendModeType.DIFFERENCE)
BlendMode.EXCLUSION = BlendMode(BlendModeType.EXCLUSION)
