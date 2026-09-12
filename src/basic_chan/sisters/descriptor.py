"""basic_chan.sisters.descriptor — Sister metadata descriptor and dynamic proxy."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class SisterDescriptor:
    """Represents a discovered sister chan in the ecosystem."""

    name: str
    slug: str
    version: str = "0.1.0"
    root_path: Optional[Path | str] = None
    module_name: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    instance: Optional[Any] = None

    def call_tool(self, tool_name: str, *args: Any, **kwargs: Any) -> Any:
        """Invokes a tool on the sister instance if available."""
        if self.instance and hasattr(self.instance, "execute_tool"):
            return self.instance.execute_tool(tool_name, *args, **kwargs)
        if self.instance and hasattr(self.instance, "tools") and hasattr(self.instance.tools, "execute"):
            return self.instance.tools.execute(tool_name, *args, **kwargs)
        raise RuntimeError(f"Sister '{self.slug}' does not have an active tool dispatcher.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "slug": self.slug,
            "version": self.version,
            "root_path": str(self.root_path) if self.root_path else None,
            "module_name": self.module_name,
            "capabilities": self.capabilities,
            "tools": self.tools,
        }
