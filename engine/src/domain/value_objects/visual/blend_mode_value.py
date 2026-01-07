"""
BlendMode Value Object: Immutable blend mode for layer compositing.
Part of visual category - layer blending operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


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


@dataclass(frozen=True)
class BlendMode:
    """Immutable blend mode for layer compositing."""

    mode: BlendModeType

    def blend_pixel(
        self, base: tuple[float, float, float], blend: tuple[float, float, float]
    ) -> tuple[float, float, float]:
        """Blend two RGB pixels (values 0.0-1.0)."""
        if self.mode == BlendModeType.NORMAL:
            return blend

        elif self.mode == BlendModeType.MULTIPLY:
            return (
                _clamp(base[0] * blend[0]),
                _clamp(base[1] * blend[1]),
                _clamp(base[2] * blend[2]),
            )

        elif self.mode == BlendModeType.SCREEN:
            return (
                _clamp(1 - (1 - base[0]) * (1 - blend[0])),
                _clamp(1 - (1 - base[1]) * (1 - blend[1])),
                _clamp(1 - (1 - base[2]) * (1 - blend[2])),
            )

        elif self.mode == BlendModeType.OVERLAY:

            def overlay_channel(b: float, luminosity: float) -> float:
                if b < 0.5:
                    return 2 * b * luminosity
                return 1 - 2 * (1 - b) * (1 - luminosity)

            return (
                _clamp(overlay_channel(base[0], blend[0])),
                _clamp(overlay_channel(base[1], blend[1])),
                _clamp(overlay_channel(base[2], blend[2])),
            )

        elif self.mode == BlendModeType.DARKEN:
            return (min(base[0], blend[0]), min(base[1], blend[1]), min(base[2], blend[2]))

        elif self.mode == BlendModeType.LIGHTEN:
            return (max(base[0], blend[0]), max(base[1], blend[1]), max(base[2], blend[2]))

        elif self.mode == BlendModeType.DIFFERENCE:
            return (abs(base[0] - blend[0]), abs(base[1] - blend[1]), abs(base[2] - blend[2]))

        elif self.mode == BlendModeType.EXCLUSION:
            return (
                _clamp(base[0] + blend[0] - 2 * base[0] * blend[0]),
                _clamp(base[1] + blend[1] - 2 * base[1] * blend[1]),
                _clamp(base[2] + blend[2] - 2 * base[2] * blend[2]),
            )

        return blend

    def __str__(self) -> str:
        return self.mode.value

    # Class-level presets (assigned after class definition)
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


# Presets
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
