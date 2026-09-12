"""basic_chan.sisters.registry_db — Daemonless SQLite WAL sister registry."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .descriptor import SisterDescriptor
from ..storage.filelock import acquire_lock


def get_default_registry_path() -> Path:
    home = Path.home()
    base = home / ".openclaw" / "chans"
    if not base.exists():
        try:
            base.mkdir(parents=True, exist_ok=True)
        except Exception:
            base = home / ".cache" / "chans"
            base.mkdir(parents=True, exist_ok=True)
    return base / "registry.db"


class SisterRegistryDB:
    """Daemonless cross-process sister chan discovery registry."""

    def __init__(self, db_path: Optional[Path | str] = None):
        self.db_path = Path(db_path).resolve() if db_path else get_default_registry_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.db_path.with_suffix(".lock")
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_db(self) -> None:
        with acquire_lock(self.lock_path):
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sister_chans (
                        slug TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        version TEXT,
                        root_path TEXT,
                        module_name TEXT,
                        capabilities TEXT,
                        tools TEXT,
                        updated_at REAL NOT NULL
                    )
                """)
                conn.commit()

    def register_sister(self, desc: SisterDescriptor) -> None:
        now = time.time()
        with acquire_lock(self.lock_path):
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO sister_chans
                    (slug, name, version, root_path, module_name, capabilities, tools, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        desc.slug,
                        desc.name,
                        desc.version,
                        str(desc.root_path) if desc.root_path else None,
                        desc.module_name,
                        json.dumps(desc.capabilities),
                        json.dumps(desc.tools),
                        now,
                    ),
                )
                conn.commit()

    def list_sisters(self) -> List[SisterDescriptor]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM sister_chans ORDER BY name ASC")
            results = []
            for r in cur.fetchall():
                results.append(
                    SisterDescriptor(
                        name=r["name"],
                        slug=r["slug"],
                        version=r["version"] or "0.1.0",
                        root_path=Path(r["root_path"]) if r["root_path"] else None,
                        module_name=r["module_name"],
                        capabilities=json.loads(r["capabilities"] or "[]"),
                        tools=json.loads(r["tools"] or "[]"),
                    )
                )
            return results
