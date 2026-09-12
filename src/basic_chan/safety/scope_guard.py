"""basic_chan.safety.scope_guard — Filesystem and network target boundary enforcement."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import List, Optional, Set
from urllib.parse import urlparse

from ..exceptions import ScopeViolationError


class ScopeGuard:
    """Enforces execution boundaries for files and network targets."""

    def __init__(
        self,
        allowed_roots: Optional[List[Path | str]] = None,
        allowed_targets: Optional[List[str]] = None,
    ):
        self.allowed_roots: List[Path] = [
            Path(r).resolve() for r in (allowed_roots or [Path.cwd()])
        ]
        self.allowed_targets: Set[str] = set(allowed_targets or [])

    def add_allowed_root(self, path: Path | str) -> None:
        p = Path(path).resolve()
        if p not in self.allowed_roots:
            self.allowed_roots.append(p)

    def add_allowed_target(self, target: str) -> None:
        self.allowed_targets.add(target.lower().strip())

    def assert_path_allowed(self, path: Path | str) -> Path:
        """Verify that a path lies inside one of the allowed directory roots."""
        resolved = Path(path).resolve()
        for root in self.allowed_roots:
            try:
                resolved.relative_to(root)
                return resolved
            except ValueError:
                continue
        raise ScopeViolationError(
            message=f"Path '{resolved}' is outside allowed root boundaries ({[str(r) for r in self.allowed_roots]}).",
            target=str(resolved),
        )

    def assert_target_allowed(self, target: str) -> str:
        """Verify that a network target or URL is in the authorized scope."""
        if not self.allowed_targets:
            # If no targets explicitly defined, default to allowing local/current
            return target

        clean = target.lower().strip()
        parsed = urlparse(clean)
        host = (parsed.hostname or clean).split(":")[0]

        for allowed in self.allowed_targets:
            if allowed == host or fnmatch.fnmatch(host, allowed):
                return target

        raise ScopeViolationError(
            message=f"Target '{target}' (host '{host}') is not in the authorized scope list.",
            target=target,
            remedy_hint=f"Authorize host '{host}' via scope allowlist before scanning.",
        )
