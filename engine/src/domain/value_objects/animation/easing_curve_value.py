"""
EasingCurve Value Object: Immutable easing curve configuration.
Part of animation category - timing and interpolation functions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EasingType(Enum):
    """Available easing function types."""

    # Basic
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_OUT_EXPO = "ease_out_expo"
    EASE_OUT_BACK = "ease_out_back"
    EASE_OUT_ELASTIC = "ease_out_elastic"

    # Trending 2024-2025 (Social Media)
    SPEED_RAMP = "speed_ramp"
    WHIP_PAN = "whip_pan"
    BOUNCE = "bounce"
    ELASTIC_SNAP = "elastic_snap"
    GRAVITY_FALL = "gravity_fall"
    EXPO_BURST = "expo_burst"
    CINEMATIC_RAMP = "cinematic_ramp"
    REVERSE_RAMP = "reverse_ramp"
    STUTTER = "stutter"
    SMOOTH_OVERSHOOT = "smooth_overshoot"
    ANTICIPATION = "anticipation"


@dataclass(frozen=True)
class EasingCurve:
    """Immutable easing curve configuration."""

    easing_type: EasingType
    overshoot: float = 0.0

    def __post_init__(self) -> None:
        if not -2.0 <= self.overshoot <= 2.0:
            raise ValueError(f"Overshoot must be -2.0 to 2.0: {self.overshoot}")

    def apply(self, t: float) -> float:
        """Apply easing to normalized time (0.0-1.0)."""
        t = max(0.0, min(1.0, t))

        if self.easing_type == EasingType.LINEAR:
            return t
        elif self.easing_type == EasingType.EASE_IN:
            return t * t
        elif self.easing_type == EasingType.EASE_OUT:
            return 1.0 - (1.0 - t) ** 2
        elif self.easing_type == EasingType.EASE_IN_OUT:
            if t < 0.5:
                return 2.0 * t * t
            else:
                return 1.0 - (-2.0 * t + 2.0) ** 2 / 2.0
        elif self.easing_type == EasingType.EASE_IN_CUBIC:
            return t * t * t
        elif self.easing_type == EasingType.EASE_OUT_CUBIC:
            return 1.0 - pow(1.0 - t, 3)
        elif self.easing_type == EasingType.EASE_OUT_EXPO:
            return 1.0 if t == 1.0 else 1.0 - pow(2.0, -10.0 * t)
        elif self.easing_type == EasingType.EASE_OUT_BACK:
            c1 = 1.70158 + self.overshoot
            c3 = c1 + 1.0
            return 1.0 + c3 * pow(t - 1.0, 3) + c1 * pow(t - 1.0, 2)
        elif self.easing_type == EasingType.EASE_OUT_ELASTIC:
            if t == 0.0 or t == 1.0:
                return t
            import math

            p = 0.3
            return pow(2.0, -10.0 * t) * math.sin((t - p / 4.0) * (2.0 * math.pi) / p) + 1.0

        # Trending 2024-2025
        elif self.easing_type == EasingType.SPEED_RAMP:
            intensity = 2.0 + self.overshoot
            return 1.0 - abs(2 * t - 1) ** intensity
        elif self.easing_type == EasingType.WHIP_PAN:
            if t < 0.2:
                return t / 0.2 * 0.1
            elif t < 0.8:
                return 0.1 + (t - 0.2) / 0.6 * 0.8
            else:
                return 0.9 + (t - 0.8) / 0.2 * 0.1
        elif self.easing_type == EasingType.BOUNCE:
            import math

            if t < 0.7:
                return t / 0.7
            else:
                bt = (t - 0.7) / 0.3
                return 1.0 + 0.15 * math.sin(bt * math.pi * 2) * (1 - bt)
        elif self.easing_type == EasingType.ELASTIC_SNAP:
            import math

            if t >= 1.0:
                return 1.0
            return 1.0 - pow(2, -10 * t) * math.cos(t * math.pi * 4)
        elif self.easing_type == EasingType.GRAVITY_FALL:
            return t**2.5
        elif self.easing_type == EasingType.EXPO_BURST:
            if t < 0.7:
                return (t / 0.7) ** 4 * 0.3
            else:
                return 0.3 + (t - 0.7) / 0.3 * 0.7
        elif self.easing_type == EasingType.CINEMATIC_RAMP:
            if t < 0.35:
                return pow(t / 0.35, 0.5) * 0.3
            elif t < 0.55:
                return 0.3 + (t - 0.35) / 0.2 * 0.2
            else:
                return 0.5 + pow((t - 0.55) / 0.45, 1.5) * 0.5
        elif self.easing_type == EasingType.REVERSE_RAMP:
            return abs(2 * t - 1) ** 0.5 * (1 if t >= 0.5 else -1) * 0.5 + 0.5
        elif self.easing_type == EasingType.STUTTER:
            steps = 6
            return int(t * steps) / steps
        elif self.easing_type == EasingType.SMOOTH_OVERSHOOT:
            amount = 0.2 + self.overshoot * 0.3
            if t < 0.65:
                return pow(t / 0.65, 0.7) * (1 + amount)
            else:
                return (1 + amount) - amount * ((t - 0.65) / 0.35)
        elif self.easing_type == EasingType.ANTICIPATION:
            if t < 0.12:
                return -0.08 * (t / 0.12)
            else:
                return -0.08 + pow((t - 0.12) / 0.88, 0.8) * 1.08

        return t

    def interpolate(self, start: float, end: float, t: float) -> float:
        """Interpolate between start and end values using this easing."""
        eased_t = self.apply(t)
        return start + (end - start) * eased_t


# Presets
EasingCurve.LINEAR = EasingCurve(EasingType.LINEAR)
EasingCurve.EASE_IN = EasingCurve(EasingType.EASE_IN)
EasingCurve.EASE_OUT = EasingCurve(EasingType.EASE_OUT)
EasingCurve.EASE_IN_OUT = EasingCurve(EasingType.EASE_IN_OUT)
EasingCurve.EASE_IN_CUBIC = EasingCurve(EasingType.EASE_IN_CUBIC)
EasingCurve.EASE_OUT_CUBIC = EasingCurve(EasingType.EASE_OUT_CUBIC)
EasingCurve.EASE_OUT_EXPO = EasingCurve(EasingType.EASE_OUT_EXPO)
EasingCurve.EASE_OUT_BACK = EasingCurve(EasingType.EASE_OUT_BACK, overshoot=0.3)
