"""
NotificationPort: Interface for domain event publishing (Event Bus pattern).
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DomainEvent(Enum):
    """Domain events that can be published."""

    # Render lifecycle
    RENDER_STARTED = "render.started"
    RENDER_PROGRESS = "render.progress"
    RENDER_COMPLETED = "render.completed"
    RENDER_CANCELLED = "render.cancelled"

    # Project lifecycle
    PROJECT_LOADED = "project.loaded"
    TIMELINE_GENERATED = "timeline.generated"

    # Errors
    ERROR_OCCURRED = "error.occurred"
    WARNING_RAISED = "warning.raised"

    # Animation states
    FRAME_RENDERED = "frame.rendered"
    LAYER_ANIMATED = "layer.animated"


@dataclass
class EventPayload:
    """Payload for domain events."""

    event: DomainEvent
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


EventCallback = Callable[[EventPayload], None]


class NotificationPort(ABC):
    """
    Port interface for domain event publishing.

    Implements the Observer/Pub-Sub pattern for decoupling
    domain logic from UI and infrastructure concerns.

    Adapters implementing this port:
    - in_memory_event_bus.py (simple callback registry)
    - websocket_notifier.py (real-time UI updates)
    """

    @abstractmethod
    def publish(self, event: DomainEvent, data: dict[str, Any] = None) -> None:  # type: ignore[assignment]
        """
        Publish a domain event.

        Args:
            event: The event type to publish.
            data: Additional event data.
        """
        pass

    @abstractmethod
    def subscribe(self, event: DomainEvent, callback: EventCallback) -> None:
        """
        Subscribe to a domain event.

        Args:
            event: The event type to listen for.
            callback: Function to call when event is published.
        """
        pass

    @abstractmethod
    def unsubscribe(self, event: DomainEvent, callback: EventCallback) -> None:
        """
        Unsubscribe from a domain event.

        Args:
            event: The event type to stop listening for.
            callback: The callback to remove.
        """
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Remove all subscriptions."""
        pass


class InMemoryEventBus(NotificationPort):
    """
    Simple in-memory event bus implementation.
    Suitable for single-process applications.
    """

    def __init__(self) -> None:
        self._subscribers: dict[DomainEvent, list[EventCallback]] = {}

    def publish(self, event: DomainEvent, data: dict[str, Any] = None) -> None:  # type: ignore[assignment]
        """Publish event to all subscribers."""
        import time

        payload = EventPayload(event=event, data=data or {}, timestamp=time.time())

        if event in self._subscribers:
            for callback in self._subscribers[event]:
                try:
                    callback(payload)
                except Exception:
                    # Don't let subscriber errors break the publisher
                    pass

    def subscribe(self, event: DomainEvent, callback: EventCallback) -> None:
        """Add subscriber for an event."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        if callback not in self._subscribers[event]:
            self._subscribers[event].append(callback)

    def unsubscribe(self, event: DomainEvent, callback: EventCallback) -> None:
        """Remove subscriber from an event."""
        if event in self._subscribers:
            try:
                self._subscribers[event].remove(callback)
            except ValueError:
                pass

    def clear_all(self) -> None:
        """Clear all subscriptions."""
        self._subscribers.clear()


class NullNotifier(NotificationPort):
    """No-op notifier for testing or silent operation."""

    def publish(self, event: DomainEvent, data: dict[str, Any] = None) -> None:  # type: ignore[assignment]
        pass

    def subscribe(self, event: DomainEvent, callback: EventCallback) -> None:
        pass

    def unsubscribe(self, event: DomainEvent, callback: EventCallback) -> None:
        pass

    def clear_all(self) -> None:
        pass
