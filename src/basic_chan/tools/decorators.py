"""basic_chan.tools.decorators — Global decorators for chan tools."""

from __future__ import annotations

from typing import Any, Callable, Optional


def chan_tool(name: Optional[str] = None, description: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Annotates a function as a chan tool."""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(fn, "_is_chan_tool", True)
        setattr(fn, "_chan_tool_name", name)
        setattr(fn, "_chan_tool_description", description)
        return fn
    return decorator
