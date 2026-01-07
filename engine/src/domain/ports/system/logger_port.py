"""
LoggerPort: Interface for structured logging operations.
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod
from typing import Any


class LoggerPort(ABC):
    """
    Port interface for structured logging.

    Adapters implementing this port:
    - console_logger_adapter.py (stdout with colors)
    - file_logger_adapter.py (rotating file logs)
    - null_logger_adapter.py (silent, for testing)
    """

    @abstractmethod
    def debug(self, message: str, **context: Any) -> None:
        """
        Log debug-level message.

        Args:
            message: Log message.
            context: Additional key-value context data.
        """
        pass

    @abstractmethod
    def info(self, message: str, **context: Any) -> None:
        """
        Log info-level message.

        Args:
            message: Log message.
            context: Additional key-value context data.
        """
        pass

    @abstractmethod
    def warning(self, message: str, **context: Any) -> None:
        """
        Log warning-level message.

        Args:
            message: Log message.
            context: Additional key-value context data.
        """
        pass

    @abstractmethod
    def error(self, message: str, exception: Exception | None = None, **context: Any) -> None:
        """
        Log error-level message with optional exception.

        Args:
            message: Log message.
            exception: Optional exception to include.
            context: Additional key-value context data.
        """
        pass

    @abstractmethod
    def trace(self, message: str, **context: Any) -> None:
        """
        Log trace-level message (most verbose).

        Args:
            message: Log message.
            context: Additional key-value context data.
        """
        pass


class NullLogger(LoggerPort):
    """
    No-op logger for testing or silent operation.
    Implements LoggerPort but discards all messages.
    """

    def debug(self, message: str, **context: Any) -> None:
        pass

    def info(self, message: str, **context: Any) -> None:
        pass

    def warning(self, message: str, **context: Any) -> None:
        pass

    def error(self, message: str, exception: Exception | None = None, **context: Any) -> None:
        pass

    def trace(self, message: str, **context: Any) -> None:
        pass
