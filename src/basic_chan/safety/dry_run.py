"""basic_chan.safety.dry_run — Dry-run simulation mode."""

from __future__ import annotations

import contextvars
from typing import Any, Callable, TypeVar

_DRY_RUN_VAR = contextvars.ContextVar[bool]("basic_chan_dry_run", default=False)

F = TypeVar("F", bound=Callable[..., Any])


def set_dry_run(enabled: bool) -> None:
    """Enable or disable dry-run simulation mode globally for the current context."""
    _DRY_RUN_VAR.set(enabled)


def is_dry_run() -> bool:
    """Check if dry-run simulation mode is active."""
    return _DRY_RUN_VAR.get()


class DryRunGuard:
    """Context manager for executing blocks in dry-run mode."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.token = None

    def __enter__(self):
        self.token = _DRY_RUN_VAR.set(self.enabled)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token is not None:
            _DRY_RUN_VAR.reset(self.token)
