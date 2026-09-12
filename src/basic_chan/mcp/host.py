"""basic_chan.mcp.host — Standalone stdio & SSE MCP server host."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional

from .sanitizer import safe_json
from ..tools.registry import ChanToolRegistry


class ChanMCPHost:
    """Hosts registered tools as an official Model Context Protocol (MCP) server."""

    def __init__(self, server_name: str, registry: ChanToolRegistry):
        self.server_name = server_name
        self.registry = registry
        self._mcp_app = None
        self._init_mcp()

    def _init_mcp(self) -> None:
        try:
            from mcp.server import MCPServer
            self._mcp_app = MCPServer(self.server_name)
            self._register_tools_to_app()
        except Exception:
            # Fallback for older or alternative environments
            self._mcp_app = None

    def _register_tools_to_app(self) -> None:
        if not self._mcp_app:
            return

        for spec in self.registry.list_specs():
            tool_name = spec.name
            tool_desc = spec.description
            
            # Create a wrapper that captures tool_name and sanitizes output
            def make_wrapper(name: str):
                def wrapper(*args: Any, **kwargs: Any) -> str:
                    res = self.registry.execute(name, *args, **kwargs)
                    sanitized = safe_json(res)
                    if isinstance(sanitized, str):
                        return sanitized
                    return json.dumps(sanitized, indent=2)
                return wrapper

            fn = make_wrapper(tool_name)
            fn.__name__ = tool_name
            fn.__doc__ = tool_desc

            # Register with MCPServer
            if hasattr(self._mcp_app, "add_tool"):
                try:
                    self._mcp_app.add_tool(fn, name=tool_name, description=tool_desc)
                except Exception:
                    pass

    def run_stdio(self) -> None:
        """Runs the MCP server over standard I/O (blocking)."""
        if self._mcp_app and hasattr(self._mcp_app, "run_stdio_async"):
            asyncio.run(self._mcp_app.run_stdio_async())
        else:
            print(f"MCP Server '{self.server_name}' starting (stdio mode)...")
