import random
from collections.abc import Sequence
from typing import Any

from domain.ports.system.random_port import RandomPort, T  # type: ignore[import-not-found]

"""
SystemRandomAdapter: Standard random number generation implementation of RandomPort.
Dependencies: random, Domain.Ports.RandomPort
"""


class SystemRandomAdapter(RandomPort):  # type: ignore[misc]
    """Standard random implementation using Python's random module."""

    def __init__(self, seed: int = None):  # type: ignore[assignment]
        self._random = random.Random(seed)

    def choice(self, sequence: Sequence[T]) -> T:
        return self._random.choice(sequence)

    def uniform(self, a: float, b: float) -> float:
        return self._random.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        return self._random.randint(a, b)

    def shuffle(self, sequence: list[Any]) -> None:
        self._random.shuffle(sequence)

    def set_seed(self, seed: int) -> None:
        self._random.seed(seed)
