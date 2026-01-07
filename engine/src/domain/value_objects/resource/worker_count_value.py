"""
WorkerCount Value Object: Immutable worker count for parallel processing.
Part of resource category - CPU-aware parallel configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import cpu_count


@dataclass(frozen=True)
class WorkerCount:
    """Immutable worker count for parallel processing."""

    count: int

    def __post_init__(self):
        if self.count < 1:
            raise ValueError(f"Worker count must be at least 1: {self.count}")
        max_workers = cpu_count() * 4
        if self.count > max_workers:
            raise ValueError(f"Worker count too high (max {max_workers}): {self.count}")

    @classmethod
    def auto(cls, reserve_cores: int = 1) -> WorkerCount:
        available = cpu_count()
        workers = max(1, available - reserve_cores)
        return cls(workers)

    @classmethod
    def all_cores(cls) -> WorkerCount:
        return cls(cpu_count())

    @classmethod
    def half_cores(cls) -> WorkerCount:
        return cls(max(1, cpu_count() // 2))

    @classmethod
    def single(cls) -> WorkerCount:
        return cls(1)

    def is_parallel(self) -> bool:
        return self.count > 1

    def is_single(self) -> bool:
        return self.count == 1

    def cpu_utilization(self) -> float:
        return (self.count / cpu_count()) * 100

    def scale(self, factor: float) -> WorkerCount:
        return WorkerCount(max(1, int(self.count * factor)))

    def format(self) -> str:
        cores = cpu_count()
        if self.count == 1:
            return "1 worker (sequential)"
        elif self.count == cores:
            return f"{self.count} workers (all cores)"
        else:
            return f"{self.count} workers ({self.cpu_utilization():.0f}% CPU)"

    def __int__(self) -> int:
        return self.count


# Presets
WorkerCount.SINGLE = WorkerCount(1)
WorkerCount.AUTO = WorkerCount.auto()
