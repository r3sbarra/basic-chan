"""basic_chan.git_diff.baseline — Stable signatures and technical debt suppression."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Set


class BaselineManager:
    """Manages baseline technical debt suppression files."""

    @staticmethod
    def compute_signature(category: str, identifier: str, relative_file: str, snippet: str = "") -> str:
        raw = f"{category}|{identifier}|{relative_file}|{snippet[:40]}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def load_baseline_signatures(cls, baseline_file: Path | str) -> Set[str]:
        p = Path(baseline_file)
        if not p.exists() or not p.is_file():
            return set()
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return {item if isinstance(item, str) else item.get("signature", "") for item in data}
            if isinstance(data, dict):
                return set(data.get("signatures", []))
        except Exception:
            pass
        return set()

    @classmethod
    def save_baseline_signatures(cls, baseline_file: Path | str, signatures: Set[str] | List[str]) -> None:
        p = Path(baseline_file)
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = {"signatures": sorted(list(signatures))}
        p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
