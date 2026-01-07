"""
TimePort: Interface for time operations (mockable for testing).
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod


class TimePort(ABC):
    """
    Port interface for time operations.

    Abstracts time access to allow mocking in tests
    and controlling time flow in simulations.

    Adapters implementing this port:
    - system_time.py (uses Python's time module)
    - mock_time.py (controllable time for testing)
    """

    @abstractmethod
    def now(self) -> float:
        """
        Get current time as Unix timestamp.

        Returns:
            Current time in seconds since epoch.
        """
        pass

    @abstractmethod
    def now_ms(self) -> int:
        """
        Get current time in milliseconds.

        Returns:
            Current time in milliseconds since epoch.
        """
        pass

    @abstractmethod
    def sleep(self, seconds: float) -> None:
        """
        Sleep for specified duration.

        Args:
            seconds: Duration to sleep.
        """
        pass

    @abstractmethod
    def elapsed_since(self, start: float) -> float:
        """
        Calculate elapsed time since start.

        Args:
            start: Start timestamp.

        Returns:
            Elapsed seconds.
        """
        pass


class MockTime(TimePort):
    """
    Controllable mock time for testing.
    Time only advances when explicitly set or incremented.
    """

    def __init__(self, initial_time: float = 0.0):
        self._current_time = initial_time

    def now(self) -> float:
        return self._current_time

    def now_ms(self) -> int:
        return int(self._current_time * 1000)

    def sleep(self, seconds: float) -> None:
        # In mock time, sleep just advances the clock
        self._current_time += seconds

    def elapsed_since(self, start: float) -> float:
        return self._current_time - start

    def set_time(self, timestamp: float) -> None:
        """Set current time to specific value."""
        self._current_time = timestamp

    def advance(self, seconds: float) -> None:
        """Advance time by specified amount."""
        self._current_time += seconds
