"""basic_chan.tools.registry — Dual-mode tool registry for in-process and MCP execution."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from .interceptors import ToolInterceptorManager
from .schema import ToolSpec, extract_tool_spec


class ChanToolRegistry:
    """Manages registered tools for in-process execution, worker swarms, and MCP export."""

    def __init__(self):
        self._specs: Dict[str, ToolSpec] = {}
        self.interceptors = ToolInterceptorManager()

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a tool."""
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            spec = extract_tool_spec(fn, name=name, description=description)
            self._specs[spec.name] = spec
            return fn
        return decorator

    def register_func(
        self,
        fn: Callable[..., Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ToolSpec:
        """Programmatically register a callable."""
        spec = extract_tool_spec(fn, name=name, description=description)
        self._specs[spec.name] = spec
        return spec

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._specs.get(name)

    def list_specs(self) -> List[ToolSpec]:
        return list(self._specs.values())

    def execute(self, tool_name: str, *args: Any, **kwargs: Any) -> Any:
        """Executes a tool with pre/post interceptors and timing metrics."""
        spec = self.get(tool_name)
        if not spec:
            raise KeyError(f"Tool '{tool_name}' not found in registry.")

        self.interceptors.run_pre_hooks(tool_name, kwargs)
        t0 = time.perf_counter()
        error = None
        result = None

        try:
            result = spec.handler(*args, **kwargs)
            return result
        except Exception as exc:
            error = exc
            raise
        finally:
            dur = (time.perf_counter() - t0) * 1000.0
            self.interceptors.run_post_hooks(tool_name, result, error, dur)

    def to_compact_schemas(self) -> List[Dict[str, Any]]:
        """Export compact schemas for small local LLMs."""
        return [s.to_compact_schema() for s in self._specs.values()]

    def __len__(self) -> int:
        return len(self._specs)
