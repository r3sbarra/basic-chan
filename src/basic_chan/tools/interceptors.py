"""basic_chan.tools.interceptors — Pre/post tool execution hooks & telemetry."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional


PreHook = Callable[[str, Dict[str, Any]], None]
PostHook = Callable[[str, Any, Optional[Exception], float], None]


class ToolInterceptorManager:
    """Manages telemetry, rate limits, and audit interceptors for tool execution."""

    def __init__(self):
        self._pre_hooks: List[PreHook] = []
        self._post_hooks: List[PostHook] = []

    def add_pre_hook(self, hook: PreHook) -> None:
        self._pre_hooks.append(hook)

    def add_post_hook(self, hook: PostHook) -> None:
        self._post_hooks.append(hook)

    def run_pre_hooks(self, tool_name: str, kwargs: Dict[str, Any]) -> None:
        for hook in self._pre_hooks:
            try:
                hook(tool_name, kwargs)
            except Exception:
                pass

    def run_post_hooks(self, tool_name: str, result: Any, error: Optional[Exception], duration_ms: float) -> None:
        for hook in self._post_hooks:
            try:
                hook(tool_name, result, error, duration_ms)
            except Exception:
                pass
