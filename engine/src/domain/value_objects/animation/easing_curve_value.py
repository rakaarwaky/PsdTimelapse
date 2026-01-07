"""
EasingCurve Value Object: Immutable easing curve configuration.
Part of animation category - timing and interpolation functions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

# Auto-extracted constants
# Auto-extracted constants
MAGIC_2_0 = 2.0
HALF = 0.5
MAGIC_0_2 = 0.2
HIGH_THRESHOLD = 0.8
MAGIC_0_7 = 0.7
MAGIC_0_35 = 0.35
MAGIC_0_55 = 0.55
MAGIC_0_45 = 0.45
MAGIC_0_65 = 0.65
MAGIC_0_12 = 0.12
HIGH_THRESHOLD8 = 0.88


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
        if not -MAGIC_2_0 <= self.overshoot <= MAGIC_2_0:
            raise ValueError(f"Overshoot must be -MAGIC_2_0 to MAGIC_2_0: {self.overshoot}")

    def apply(self, t: float) -> float:
        """Apply easing to normalized time (0.0-1.0)."""
        t = max(0.0, min(1.0, t))

        # Dynamic dispatch based on easing type name
        method_name = f"_apply_{self.easing_type.value}"
        method = getattr(self, method_name, self._apply_linear)
        return method(t)

    def _apply_linear(self, t: float) -> float:
        return t

    def _apply_ease_in(self, t: float) -> float:
        return t * t

    def _apply_ease_out(self, t: float) -> float:
        return 1.0 - (1.0 - t) ** 2

    def _apply_ease_in_out(self, t: float) -> float:
        if t < HALF:
            return MAGIC_2_0 * t * t
        return 1.0 - (-MAGIC_2_0 * t + MAGIC_2_0) ** 2 / MAGIC_2_0

    def _apply_ease_in_cubic(self, t: float) -> float:
        return t * t * t

    def _apply_ease_out_cubic(self, t: float) -> float:
        return 1.0 - (1.0 - t) ** 3

    def _apply_ease_out_expo(self, t: float) -> float:
        return 1.0 if t == 1.0 else 1.0 - MAGIC_2_0 ** (-10.0 * t)

    def _apply_ease_out_back(self, t: float) -> float:
        c1 = 1.70158 + self.overshoot
        c3 = c1 + 1.0
        return 1.0 + c3 * (t - 1.0) ** 3 + c1 * (t - 1.0) ** 2

    def _apply_ease_out_elastic(self, t: float) -> float:
        if t in {0.0, 1.0}:
            return t

        p = 0.3
        return float(
            MAGIC_2_0 ** (-10.0 * t) * math.sin((t - p / 4.0) * (MAGIC_2_0 * math.pi) / p) + 1.0
        )

    def _apply_speed_ramp(self, t: float) -> float:
        intensity = MAGIC_2_0 + self.overshoot
        return float(1.0 - abs(2 * t - 1) ** intensity)

    def _apply_whip_pan(self, t: float) -> float:
        if t < MAGIC_0_2:
            return float(t / MAGIC_0_2 * 0.1)
        elif t < HIGH_THRESHOLD:
            return float(0.1 + (t - MAGIC_0_2) / 0.6 * HIGH_THRESHOLD)
        return float(0.9 + (t - HIGH_THRESHOLD) / MAGIC_0_2 * 0.1)

    def _apply_bounce(self, t: float) -> float:
        if t < MAGIC_0_7:
            return float(t / MAGIC_0_7)
        bt = (t - MAGIC_0_7) / 0.3
        return float(1.0 + 0.15 * math.sin(bt * math.pi * 2) * (1 - bt))

    def _apply_elastic_snap(self, t: float) -> float:
        if t >= 1.0:
            return 1.0
        return float(1.0 - 2 ** (-10 * t) * math.cos(t * math.pi * 4))

    def _apply_gravity_fall(self, t: float) -> float:
        return float(t**2.5)

    def _apply_expo_burst(self, t: float) -> float:
        if t < MAGIC_0_7:
            return float((t / MAGIC_0_7) ** 4 * 0.3)
        return float(0.3 + (t - MAGIC_0_7) / 0.3 * MAGIC_0_7)

    def _apply_cinematic_ramp(self, t: float) -> float:
        threshold_mid = 0.55
        if t < MAGIC_0_35:
            return float((t / MAGIC_0_35) ** HALF * 0.3)
        elif t < threshold_mid:
            return float(0.3 + (t - MAGIC_0_35) / MAGIC_0_2 * MAGIC_0_2)
        return float(0.5 + ((t - threshold_mid) / 0.45) ** 1.5 * 0.5)

    def _apply_reverse_ramp(self, t: float) -> float:
        return float(abs(2 * t - 1) ** HALF * (1 if t >= HALF else -1) * HALF + HALF)

    def _apply_stutter(self, t: float) -> float:
        steps = 6
        return float(int(t * steps) / steps)

    def _apply_smooth_overshoot(self, t: float) -> float:
        amount = MAGIC_0_2 + self.overshoot * 0.3
        if t < MAGIC_0_65:
            return float((t / MAGIC_0_65) ** MAGIC_0_7 * (1 + amount))
        return float((1 + amount) - amount * ((t - MAGIC_0_65) / MAGIC_0_35))

    def _apply_anticipation(self, t: float) -> float:
        if t < MAGIC_0_12:
            return float(-0.08 * (t / MAGIC_0_12))
        return float(-0.08 + ((t - MAGIC_0_12) / HIGH_THRESHOLD8) ** HIGH_THRESHOLD * 1.08)

    def interpolate(self, start: float, end: float, t: float) -> float:
        """Interpolate between start and end values using this easing."""
        eased_t = self.apply(t)
        return start + (end - start) * eased_t


# Presets
EasingCurve.LINEAR = EasingCurve(EasingType.LINEAR)  # type: ignore[attr-defined]
EasingCurve.EASE_IN = EasingCurve(EasingType.EASE_IN)  # type: ignore[attr-defined]
EasingCurve.EASE_OUT = EasingCurve(EasingType.EASE_OUT)  # type: ignore[attr-defined]
EasingCurve.EASE_IN_OUT = EasingCurve(EasingType.EASE_IN_OUT)  # type: ignore[attr-defined]
EasingCurve.EASE_IN_CUBIC = EasingCurve(EasingType.EASE_IN_CUBIC)  # type: ignore[attr-defined]
EasingCurve.EASE_OUT_CUBIC = EasingCurve(EasingType.EASE_OUT_CUBIC)  # type: ignore[attr-defined]
EasingCurve.EASE_OUT_EXPO = EasingCurve(EasingType.EASE_OUT_EXPO)  # type: ignore[attr-defined]
EasingCurve.EASE_OUT_BACK = EasingCurve(EasingType.EASE_OUT_BACK, overshoot=0.3)  # type: ignore[attr-defined]
