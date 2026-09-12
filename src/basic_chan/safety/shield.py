"""basic_chan.safety.shield — Core component immutability shield (CoreShield)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..exceptions import CoreImmunityViolationError


class CoreShield:
    """Guards critical kernel files from unauthorized self-patching or mutation."""

    def __init__(
        self,
        package_root: Optional[Path | str] = None,
        protected_subpaths: Optional[List[str]] = None,
    ):
        self.package_root = Path(package_root).resolve() if package_root else Path.cwd()
        self.protected_subpaths: Set[str] = set(
            protected_subpaths
            or ["src/basic_chan/base.py", "src/basic_chan/safety", "src/basic_chan/storage"]
        )
        self._checksums: Dict[str, str] = {}
        self._record_baselines()

    def _hash_file(self, path: Path) -> str:
        if not path.exists() or not path.is_file():
            return ""
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()

    def _record_baselines(self) -> None:
        for sub in self.protected_subpaths:
            p = self.package_root / sub
            if p.is_file():
                self._checksums[str(p)] = self._hash_file(p)
            elif p.is_dir():
                for f in p.glob("**/*.py"):
                    self._checksums[str(f)] = self._hash_file(f)

    def assert_can_write(self, target_path: Path | str) -> None:
        """Verifies that writing to target_path is not a violation of core immunity."""
        p = Path(target_path).resolve()
        for sub in self.protected_subpaths:
            protected_full = (self.package_root / sub).resolve()
            if p == protected_full or protected_full in p.parents:
                raise CoreImmunityViolationError(file_path=str(p))

    def verify_integrity(self) -> bool:
        """Verify all protected files match their baseline hashes."""
        for file_path_str, expected_hash in self._checksums.items():
            current_hash = self._hash_file(Path(file_path_str))
            if current_hash != expected_hash:
                return False
        return True
