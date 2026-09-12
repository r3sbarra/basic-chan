"""basic_chan.storage.filelock — Advisory process file locking."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Iterator

from filelock import FileLock, Timeout


@contextlib.contextmanager
def acquire_lock(lock_path: Path | str, timeout: float = 10.0) -> Iterator[FileLock]:
    """Acquires a cross-process advisory lock with a configurable timeout."""
    p = Path(lock_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(str(p), timeout=timeout)
    lock.acquire()
    try:
        yield lock
    finally:
        try:
            lock.release()
        except Exception:
            pass
