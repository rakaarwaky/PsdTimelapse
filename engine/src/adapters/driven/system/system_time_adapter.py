"""
SystemTimeAdapter: Standard time implementation of TimePort using Python's time module.
Dependencies: time, Domain.Ports.TimePort
"""

import time

from domain.ports.system.time_port import TimePort  # type: ignore[import-not-found]


class SystemTimeAdapter(TimePort):  # type: ignore[misc]
    """Standard time implementation using Python's time module."""

    def now(self) -> float:
        return time.time()

    def now_ms(self) -> int:
        return int(time.time() * 1000)

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def elapsed_since(self, start: float) -> float:
        return self.now() - start
