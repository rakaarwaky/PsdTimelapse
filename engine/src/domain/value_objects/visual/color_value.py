"""
Color Value Object: Immutable RGBA color representation.
Part of visual category - color and appearance properties.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    """Immutable RGBA color (values 0-255)."""

    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255

    def __post_init__(self):
        object.__setattr__(self, "r", max(0, min(255, self.r)))
        object.__setattr__(self, "g", max(0, min(255, self.g)))
        object.__setattr__(self, "b", max(0, min(255, self.b)))
        object.__setattr__(self, "a", max(0, min(255, self.a)))

    @staticmethod
    def from_hex(hex_str: str) -> Color:
        """Create Color from hex string (e.g., '#FF5500' or 'FF5500')."""
        hex_clean = hex_str.lstrip("#")

        if len(hex_clean) == 6:
            r = int(hex_clean[0:2], 16)
            g = int(hex_clean[2:4], 16)
            b = int(hex_clean[4:6], 16)
            return Color(r, g, b, 255)
        elif len(hex_clean) == 8:
            r = int(hex_clean[0:2], 16)
            g = int(hex_clean[2:4], 16)
            b = int(hex_clean[4:6], 16)
            a = int(hex_clean[6:8], 16)
            return Color(r, g, b, a)
        else:
            raise ValueError(f"Invalid hex color: {hex_str}")

    @staticmethod
    def from_rgba(r: int, g: int, b: int, a: int = 255) -> Color:
        """Create Color from RGBA values."""
        return Color(r, g, b, a)

    @staticmethod
    def from_float(r: float, g: float, b: float, a: float = 1.0) -> Color:
        """Create Color from float values (0.0-1.0)."""
        return Color(int(r * 255), int(g * 255), int(b * 255), int(a * 255))

    def to_hex(self, include_alpha: bool = False) -> str:
        """Convert to hex string."""
        if include_alpha:
            return f"#{self.r:02X}{self.g:02X}{self.b:02X}{self.a:02X}"
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_tuple(self) -> tuple[int, int, int, int]:
        """Convert to RGBA tuple."""
        return (self.r, self.g, self.b, self.a)

    def to_rgb_tuple(self) -> tuple[int, int, int]:
        """Convert to RGB tuple (no alpha)."""
        return (self.r, self.g, self.b)

    def with_alpha(self, alpha: int) -> Color:
        """Return new Color with different alpha."""
        return Color(self.r, self.g, self.b, alpha)

    def lerp(self, target: Color, t: float) -> Color:
        """Linear interpolation towards target color."""
        t = max(0.0, min(1.0, t))
        return Color(
            int(self.r + (target.r - self.r) * t),
            int(self.g + (target.g - self.g) * t),
            int(self.b + (target.b - self.b) * t),
            int(self.a + (target.a - self.a) * t),
        )

    def __repr__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"


# Preset colors
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
TRANSPARENT = Color(0, 0, 0, 0)
