"""basic_chan.events.bus — In-process pub-sub signal dispatcher."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

EventHandler = Callable[[Any], None]


class ChanEventBus:
    """Lightweight in-process event bus for decoupled cross-component signals."""

    def __init__(self):
        self._listeners: Dict[str, List[EventHandler]] = {}

    def on(self, event_name: str, handler: EventHandler) -> None:
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(handler)

    def off(self, event_name: str, handler: EventHandler) -> bool:
        if event_name in self._listeners and handler in self._listeners[event_name]:
            self._listeners[event_name].remove(handler)
            return True
        return False

    def emit(self, event_name: str, data: Any = None) -> None:
        for handler in self._listeners.get(event_name, []):
            try:
                handler(data)
            except Exception:
                pass
