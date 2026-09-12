"""basic_chan.safety.overrides — Dynamic behavior hooks with guaranteed fallback."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class BehaviorOverrideRegistry:
    """Registry for safe dynamic runtime behavior hooks with zero-crash fallback."""

    def __init__(self):
        self._overrides: Dict[str, Callable[..., Any]] = {}
        self._defaults: Dict[str, Callable[..., Any]] = {}

    def register_default(self, behavior_name: str, handler: Callable[..., Any]) -> None:
        """Register the pristine default core implementation for a behavior."""
        self._defaults[behavior_name] = handler

    def register_override(self, behavior_name: str, handler: Callable[..., Any]) -> None:
        """Register an alternative dynamic behavior hook."""
        self._overrides[behavior_name] = handler

    def remove_override(self, behavior_name: str) -> bool:
        """Remove an active override and revert to default."""
        return self._overrides.pop(behavior_name, None) is not None

    def execute(self, behavior_name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute the behavior override with guaranteed fallback to default on error."""
        if behavior_name in self._overrides:
            try:
                return self._overrides[behavior_name](*args, **kwargs)
            except Exception as exc:
                logger.warning(
                    f"Override for '{behavior_name}' raised an error ({exc}); falling back to default logic."
                )

        if behavior_name in self._defaults:
            return self._defaults[behavior_name](*args, **kwargs)

        raise KeyError(f"No default or override registered for behavior '{behavior_name}'.")
