"""
BatchSize Value Object: Immutable batch size for processing.
Part of resource category - batch configuration.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BatchSize:
    """Immutable batch size for processing operations."""

    size: int

    MIN_SIZE: int = 1
    MAX_SIZE: int = 10000

    def __post_init__(self) -> None:
        if self.size < BatchSize.MIN_SIZE:
            raise ValueError(f"Batch size too small (min {BatchSize.MIN_SIZE}): {self.size}")
        if self.size > BatchSize.MAX_SIZE:
            raise ValueError(f"Batch size too large (max {BatchSize.MAX_SIZE}): {self.size}")

    @classmethod
    def for_frames(cls, fps: int = 30) -> BatchSize:
        return cls(fps)

    @classmethod
    def auto(cls, total_items: int, target_batches: int = 10) -> BatchSize:
        size = max(1, total_items // target_batches)
        return cls(min(size, BatchSize.MAX_SIZE))

    def num_batches(self, total_items: int) -> int:
        return (total_items + self.size - 1) // self.size

    # type: ignore[name-defined,unused-ignore]
    # type: ignore[name-defined,unused-ignore]
    def batch_ranges(self, total_items: int) -> Iterator[Any]:  # type: ignore[unused-ignore]
        for start in range(0, total_items, self.size):
            end = min(start + self.size, total_items)
            yield (start, end)

    def is_single_batch(self, total_items: int) -> bool:
        return total_items <= self.size

    def scale(self, factor: float) -> BatchSize:
        new_size = max(1, int(self.size * factor))
        return BatchSize(min(new_size, BatchSize.MAX_SIZE))

    def __int__(self) -> int:
        return self.size

    def __mul__(self, factor: float) -> BatchSize:
        return self.scale(factor)


# Common presets
BatchSize.SMALL = BatchSize(10)  # type: ignore[attr-defined]
BatchSize.MEDIUM = BatchSize(30)  # type: ignore[attr-defined]
BatchSize.LARGE = BatchSize(100)  # type: ignore[attr-defined]
BatchSize.XLARGE = BatchSize(500)  # type: ignore[attr-defined]
