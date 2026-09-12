"""basic_chan.intelligence.confusion — Autonomy-first confusion tracking & escalation gating."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ConfusionState:
    """Tracks autonomous failure cycles for a domain or task."""

    domain_or_task: str
    failure_count: int = 0
    threshold: int = 3
    history: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def is_confused(self) -> bool:
        return self.failure_count >= self.threshold

    def record_failure(self, error: str, attempt_type: str = "general") -> bool:
        self.failure_count += 1
        self.history.append({"attempt": self.failure_count, "type": attempt_type, "error": error})
        return self.is_confused

    def record_success(self) -> None:
        self.failure_count = 0
        self.history.clear()


class ConfusionTracker:
    """Manages failure cycles across domains to prevent agent infinite loops."""

    def __init__(self, default_threshold: int = 3):
        self.default_threshold = default_threshold
        self._states: Dict[str, ConfusionState] = {}

    def get_state(self, key: str) -> ConfusionState:
        if key not in self._states:
            self._states[key] = ConfusionState(domain_or_task=key, threshold=self.default_threshold)
        return self._states[key]

    def record_failure(self, key: str, error: str, attempt_type: str = "general") -> bool:
        return self.get_state(key).record_failure(error, attempt_type)

    def record_success(self, key: str) -> None:
        self.get_state(key).record_success()

    def is_confused(self, key: str) -> bool:
        return self.get_state(key).is_confused
