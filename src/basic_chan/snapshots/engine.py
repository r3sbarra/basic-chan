"""basic_chan.snapshots.engine — Historical run snapshotting & delta tracking."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class SnapshotEngine:
    """Manages versioned JSON snapshots of runs under .chan_snapshots/."""

    def __init__(self, storage_dir: Path | str):
        self.storage_dir = Path(storage_dir).resolve()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def record_snapshot(self, tag: str, payload: Dict[str, Any]) -> Path:
        timestamp = int(time.time())
        filename = f"{tag}_{timestamp}.json"
        out_file = self.storage_dir / filename
        data = {
            "tag": tag,
            "timestamp": timestamp,
            "payload": payload,
        }
        out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return out_file

    def list_snapshots(self, tag: Optional[str] = None) -> List[Path]:
        files = sorted(self.storage_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if tag:
            files = [f for f in files if f.name.startswith(f"{tag}_")]
        return files

    def get_latest(self, tag: str) -> Optional[Dict[str, Any]]:
        snaps = self.list_snapshots(tag)
        if not snaps:
            return None
        try:
            return json.loads(snaps[0].read_text(encoding="utf-8"))
        except Exception:
            return None
