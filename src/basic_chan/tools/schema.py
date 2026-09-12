"""basic_chan.tools.schema — Token-efficient compact & full JSONSchema generators."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, get_type_hints


@dataclass
class ToolParam:
    name: str
    type_name: str
    description: str = ""
    required: bool = True
    default: Any = None


@dataclass
class ToolSpec:
    name: str
    description: str
    handler: Callable[..., Any]
    params: List[ToolParam] = field(default_factory=list)

    def to_compact_schema(self) -> Dict[str, Any]:
        """Generate token-efficient compact schema for small local LLMs."""
        params_dict = {}
        for p in self.params:
            item: Dict[str, Any] = {"type": p.type_name}
            if p.description:
                item["desc"] = p.description
            if not p.required:
                item["optional"] = True
                if p.default is not None:
                    item["default"] = p.default
            params_dict[p.name] = item

        return {
            "name": self.name,
            "description": self.description,
            "parameters": params_dict,
        }

    def to_json_schema(self) -> Dict[str, Any]:
        """Generate standard JSONSchema specification for cloud agents / MCP."""
        properties = {}
        required = []

        type_map = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object",
        }

        for p in self.params:
            json_type = type_map.get(p.type_name, "string")
            prop_def: Dict[str, Any] = {"type": json_type}
            if p.description:
                prop_def["description"] = p.description
            if p.default is not None:
                prop_def["default"] = p.default
            properties[p.name] = prop_def
            if p.required:
                required.append(p.name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


def extract_tool_spec(fn: Callable[..., Any], name: Optional[str] = None, description: Optional[str] = None) -> ToolSpec:
    """Reflects parameter types and docstrings to build a ToolSpec."""
    tool_name = name or fn.__name__
    tool_desc = description or (inspect.getdoc(fn) or tool_name).split("\n\n")[0].strip()

    sig = inspect.signature(fn)
    try:
        type_hints = get_type_hints(fn)
    except Exception:
        type_hints = {}

    params: List[ToolParam] = []
    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue
        hint = type_hints.get(param_name, str)
        type_name = getattr(hint, "__name__", str(hint))
        is_required = param.default is inspect.Parameter.empty
        default_val = None if is_required else param.default

        params.append(
            ToolParam(
                name=param_name,
                type_name=type_name,
                description="",
                required=is_required,
                default=default_val,
            )
        )

    return ToolSpec(name=tool_name, description=tool_desc, handler=fn, params=params)
