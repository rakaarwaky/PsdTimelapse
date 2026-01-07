"""
ConsoleNotificationAdapter: Simple console-based implementation of NotificationPort.
Dependencies: Domain.Ports.NotificationPort
"""

import time
from typing import Any

from domain.ports.system.notification_port import (
    DomainEvent,
    EventCallback,
    EventPayload,
    NotificationPort,
)


class ConsoleNotificationAdapter(NotificationPort):
    """
    Adapter that prints notifications to console and maintains subscriptions in memory.
    """

    def __init__(self):
        self._subscribers: dict[DomainEvent, list[EventCallback]] = {}

    def publish(self, event: DomainEvent, data: dict[str, Any] = None) -> None:
        """Publish event to all subscribers and print to console."""
        payload = EventPayload(event=event, data=data or {}, timestamp=time.time())

        # Print notification
        print(f"[{event.value}] Published")
        if data:
            print(f"  Data: {data}")

        # Notify subscribers
        if event in self._subscribers:
            for callback in self._subscribers[event]:
                try:
                    callback(payload)
                except Exception as e:
                    print(f"Error in subscriber for {event.value}: {e}")

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
