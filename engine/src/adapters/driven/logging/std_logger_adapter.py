"""
StdLoggerAdapter: standard logging implementation of LoggerPort.
Dependencies: python logging module, Domain.Ports.LoggerPort
"""

import logging
from typing import Any

from domain.ports.system.logger_port import LoggerPort


class StdLoggerAdapter(LoggerPort):
    """
    Adapter for LoggerPort using Python's standard logging module.
    """

    def __init__(self, name: str = "App"):
        self._logger = logging.getLogger(name)
        # Ensure default handler if none exists
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def debug(self, message: str, **context: Any) -> None:
        if context:
            message = f"{message} | {context}"
        self._logger.debug(message)

    def info(self, message: str, **context: Any) -> None:
        if context:
            message = f"{message} | {context}"
        self._logger.info(message)

    def warning(self, message: str, **context: Any) -> None:
        if context:
            message = f"{message} | {context}"
        self._logger.warning(message)

    def error(self, message: str, exception: Exception | None = None, **context: Any) -> None:
        if context:
            message = f"{message} | {context}"
        self._logger.error(message, exc_info=exception)

    def trace(self, message: str, **context: Any) -> None:
        # Map trace to debug for standard logging
        if context:
            message = f"{message} | {context}"
        self._logger.debug(f"[TRACE] {message}")
