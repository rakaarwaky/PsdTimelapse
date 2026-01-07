"""
RandomPort: Interface for random number generation (seedable for testing).
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, TypeVar

T = TypeVar("T")


class RandomPort(ABC):
    """
    Port interface for random number generation.

    Abstracts randomness to allow deterministic testing
    via seeding.

    Adapters implementing this port:
    - system_random.py (uses Python's random module)
    - deterministic_random.py (fixed seed for testing)
    """

    @abstractmethod
    def choice(self, sequence: Sequence[T]) -> T:
        """
        Choose random element from sequence.

        Args:
            sequence: Non-empty sequence to choose from.

        Returns:
            Random element from sequence.
        """
        pass

    @abstractmethod
    def uniform(self, a: float, b: float) -> float:
        """
        Random float N such that a <= N <= b.

        Args:
            a: Lower bound.
            b: Upper bound.

        Returns:
            Random float in range.
        """
        pass

    @abstractmethod
    def randint(self, a: int, b: int) -> int:
        """
        Random integer N such that a <= N <= b.

        Args:
            a: Lower bound (inclusive).
            b: Upper bound (inclusive).

        Returns:
            Random integer in range.
        """
        pass

    @abstractmethod
    def shuffle(self, sequence: list[Any]) -> None:
        """
        Shuffle list in place.

        Args:
            sequence: List to shuffle.
        """
        pass

    @abstractmethod
    def set_seed(self, seed: int) -> None:
        """
        Set random seed for reproducible results.

        Args:
            seed: Seed value.
        """
        pass


class DeterministicRandom(RandomPort):
    """
    Deterministic random for testing.
    Always returns the same sequence based on seed.
    """

    def __init__(self, seed: int = 42):
        import random

        self._random = random.Random(seed)
        self._seed = seed

    def choice(self, sequence: Sequence[T]) -> T:
        return self._random.choice(sequence)

    def uniform(self, a: float, b: float) -> float:
        return self._random.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        return self._random.randint(a, b)

    def shuffle(self, sequence: list[Any]) -> None:
        self._random.shuffle(sequence)

    def set_seed(self, seed: int) -> None:
        self._seed = seed
        self._random.seed(seed)

    def reset(self) -> None:
        """Reset to original seed for reproducible tests."""
        self._random.seed(self._seed)
