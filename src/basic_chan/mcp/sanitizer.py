"""basic_chan.mcp.sanitizer — Coercion of non-JSON values (NaN, Inf, sets, paths)."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any


def safe_json(obj: Any) -> Any:
    """Recursively coerce non-JSON-safe values (NaN, Inf, Path, set) to JSON-serializable types."""
    if isinstance(obj, dict):
        return {str(k): safe_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [safe_json(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return str(obj)
        return obj
    if isinstance(obj, Path):
        return str(obj)
    if hasattr(obj, "model_dump"):
        return safe_json(obj.model_dump())
    if hasattr(obj, "to_dict"):
        return safe_json(obj.to_dict())
    return obj
