"""
MemoryLimit Value Object: Immutable memory limit configuration.
Part of resource category - memory management.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MemoryUnit(Enum):
    """Memory size units."""

    BYTES = 1
    KB = 1024
    MB = 1024 * 1024
    GB = 1024 * 1024 * 1024


@dataclass(frozen=True)
class MemoryLimit:
    """Immutable memory limit in bytes."""

    bytes: int

    MIN_BYTES: int = 1024 * 1024
    MAX_BYTES: int = 64 * 1024 * 1024 * 1024

    def __post_init__(self):
        if self.bytes < MemoryLimit.MIN_BYTES:
            raise ValueError(f"Memory limit too small (min 1MB): {self.bytes}")
        if self.bytes > MemoryLimit.MAX_BYTES:
            raise ValueError(f"Memory limit too large (max 64GB): {self.bytes}")

    @classmethod
    def from_kb(cls, kb: float) -> MemoryLimit:
        return cls(int(kb * MemoryUnit.KB.value))

    @classmethod
    def from_mb(cls, mb: float) -> MemoryLimit:
        return cls(int(mb * MemoryUnit.MB.value))

    @classmethod
    def from_gb(cls, gb: float) -> MemoryLimit:
        return cls(int(gb * MemoryUnit.GB.value))

    def to_kb(self) -> float:
        return self.bytes / MemoryUnit.KB.value

    def to_mb(self) -> float:
        return self.bytes / MemoryUnit.MB.value

    def to_gb(self) -> float:
        return self.bytes / MemoryUnit.GB.value

    def format(self) -> str:
        if self.bytes >= MemoryUnit.GB.value:
            return f"{self.to_gb():.1f} GB"
        elif self.bytes >= MemoryUnit.MB.value:
            return f"{self.to_mb():.1f} MB"
        elif self.bytes >= MemoryUnit.KB.value:
            return f"{self.to_kb():.1f} KB"
        return f"{self.bytes} bytes"

    def exceeds(self, usage_bytes: int) -> bool:
        return usage_bytes > self.bytes

    def remaining(self, usage_bytes: int) -> int:
        return max(0, self.bytes - usage_bytes)

    def usage_percent(self, usage_bytes: int) -> float:
        return (usage_bytes / self.bytes) * 100

    def __add__(self, other: MemoryLimit) -> MemoryLimit:
        return MemoryLimit(self.bytes + other.bytes)

    def __sub__(self, other: MemoryLimit) -> MemoryLimit:
        return MemoryLimit(max(MemoryLimit.MIN_BYTES, self.bytes - other.bytes))

    def __lt__(self, other: MemoryLimit) -> bool:
        return self.bytes < other.bytes

    def __le__(self, other: MemoryLimit) -> bool:
        return self.bytes <= other.bytes


# Common presets
MemoryLimit.MB_512 = MemoryLimit.from_mb(512)
MemoryLimit.GB_1 = MemoryLimit.from_gb(1)
MemoryLimit.GB_2 = MemoryLimit.from_gb(2)
MemoryLimit.GB_4 = MemoryLimit.from_gb(4)
MemoryLimit.GB_8 = MemoryLimit.from_gb(8)
