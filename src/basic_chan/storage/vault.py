"""basic_chan.storage.vault — Zero-daemon SQLite WAL storage engine."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .filelock import acquire_lock


class DaemonlessVault:
    """Thread-safe, process-safe zero-daemon persistent storage engine using SQLite WAL."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.db_path.with_suffix(".lock")
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    def _init_db(self) -> None:
        with acquire_lock(self.lock_path):
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS kv_store (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        expires_at REAL
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        domain TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        lease_owner TEXT,
                        lease_expires_at REAL,
                        result TEXT,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, domain)")
                conn.commit()

    # --- KV Store ---

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        """Store key-value pair with optional expiration."""
        val_str = json.dumps(value)
        expires_at = (time.time() + ttl_seconds) if ttl_seconds else None
        with acquire_lock(self.lock_path):
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO kv_store (key, value, expires_at) VALUES (?, ?, ?)",
                    (key, val_str, expires_at),
                )
                conn.commit()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve key value, returning default if missing or expired."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT value, expires_at FROM kv_store WHERE key = ?", (key,))
            row = cursor.fetchone()
            if not row:
                return default
            if row["expires_at"] and row["expires_at"] < time.time():
                # Expired: clean up lazily
                self.delete(key)
                return default
            try:
                return json.loads(row["value"])
            except Exception:
                return row["value"]

    def delete(self, key: str) -> bool:
        """Delete a key."""
        with acquire_lock(self.lock_path):
            with self._get_connection() as conn:
                cur = conn.execute("DELETE FROM kv_store WHERE key = ?", (key,))
                conn.commit()
                return cur.rowcount > 0

    def keys(self, prefix: str = "") -> List[str]:
        """List keys matching prefix."""
        with self._get_connection() as conn:
            now = time.time()
            if prefix:
                cur = conn.execute(
                    "SELECT key FROM kv_store WHERE key LIKE ? AND (expires_at IS NULL OR expires_at > ?)",
                    (f"{prefix}%", now),
                )
            else:
                cur = conn.execute(
                    "SELECT key FROM kv_store WHERE (expires_at IS NULL OR expires_at > ?)",
                    (now,),
                )
            return [r["key"] for r in cur.fetchall()]

    # --- Tasks & Ephemeral Leases ---

    def enqueue_task(self, task_id: str, domain: str, payload: Dict[str, Any]) -> None:
        now = time.time()
        with acquire_lock(self.lock_path):
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO tasks (id, domain, payload, status, created_at, updated_at)
                    VALUES (?, ?, ?, 'pending', ?, ?)
                    """,
                    (task_id, domain, json.dumps(payload), now, now),
                )
                conn.commit()

    def lease_task(self, domain: str, worker_id: str, lease_seconds: float = 60.0) -> Optional[Dict[str, Any]]:
        now = time.time()
        lease_until = now + lease_seconds
        with acquire_lock(self.lock_path):
            with self._get_connection() as conn:
                # Find available pending task or expired lease
                cur = conn.execute(
                    """
                    SELECT id, payload FROM tasks
                    WHERE domain = ? AND (status = 'pending' OR (status = 'running' AND lease_expires_at < ?))
                    ORDER BY created_at ASC LIMIT 1
                    """,
                    (domain, now),
                )
                row = cur.fetchone()
                if not row:
                    return None

                task_id = row["id"]
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = 'running', lease_owner = ?, lease_expires_at = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (worker_id, lease_until, now, task_id),
                )
                conn.commit()
                return {
                    "id": task_id,
                    "domain": domain,
                    "payload": json.loads(row["payload"]),
                    "lease_owner": worker_id,
                }

    def complete_task(self, task_id: str, result: Any) -> None:
        now = time.time()
        with acquire_lock(self.lock_path):
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE tasks SET status = 'completed', result = ?, updated_at = ? WHERE id = ?",
                    (json.dumps(result), now, task_id),
                )
                conn.commit()
