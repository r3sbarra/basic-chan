"""basic_chan.sisters.resolver — 4-tier dynamic sister discovery engine."""

from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .descriptor import SisterDescriptor
from .registry_db import SisterRegistryDB
from ..exceptions import SisterNotFoundError


class DynamicSisterResolver:
    """Discovers and resolves sister chans dynamically across 4 discovery tiers."""

    def __init__(self, current_slug: str, workspace_roots: Optional[List[Path | str]] = None):
        self.current_slug = current_slug
        self.workspace_roots: List[Path] = []
        
        # Configure search paths
        if workspace_roots:
            self.workspace_roots.extend([Path(r).resolve() for r in workspace_roots])
        else:
            env_roots = os.environ.get("CHAN_WORKSPACE_ROOTS")
            if env_roots:
                for r in env_roots.split(os.pathsep):
                    if r.strip():
                        self.workspace_roots.append(Path(r.strip()).resolve())
            else:
                default_p = Path.home() / ".openclaw" / "workspace" / "projects"
                if default_p.exists():
                    self.workspace_roots.append(default_p)
                self.workspace_roots.append(Path.cwd().parent)

        self.db = SisterRegistryDB()
        self._runtime_sisters: Dict[str, SisterDescriptor] = {}
        self._discovered_cache: Dict[str, SisterDescriptor] = {}

    def register_runtime_sister(self, desc: SisterDescriptor) -> None:
        """Register a sister instance directly at runtime."""
        self._runtime_sisters[desc.slug] = desc
        self._discovered_cache[desc.slug] = desc

    def discover_all(self) -> List[SisterDescriptor]:
        """Runs dynamic discovery across all 4 tiers."""
        discovered: Dict[str, SisterDescriptor] = {}

        # Tier 1: Runtime in-memory registry
        for slug, desc in self._runtime_sisters.items():
            if slug != self.current_slug:
                discovered[slug] = desc

        # Tier 2: Python entrypoints (basic_chan.sisters)
        try:
            from importlib.metadata import entry_points
            eps = entry_points(group="basic_chan.sisters")
            for ep in eps:
                if ep.name != self.current_slug and ep.name not in discovered:
                    try:
                        factory = ep.load()
                        inst = factory() if callable(factory) else factory
                        discovered[ep.name] = SisterDescriptor(
                            name=getattr(inst, "name", ep.name),
                            slug=ep.name,
                            instance=inst,
                        )
                    except Exception:
                        pass
        except Exception:
            pass

        # Tier 3: Workspace directory crawler
        for root in self.workspace_roots:
            if not root.exists() or not root.is_dir():
                continue
            for child in root.iterdir():
                if not child.is_dir() or child.name.startswith("."):
                    continue
                # Match *-chan* directories or directories containing chan.json / manifest.json
                is_chan_cand = "chan" in child.name.lower() or (child / "chan.json").exists() or (child / "manifest.json").exists()
                if is_chan_cand and child.name != self.current_slug:
                    slug = child.name
                    if slug not in discovered:
                        desc = self._inspect_directory(child, slug)
                        if desc:
                            discovered[slug] = desc

        # Tier 4: SQLite WAL IPC Registry
        try:
            for s in self.db.list_sisters():
                if s.slug != self.current_slug and s.slug not in discovered:
                    discovered[s.slug] = s
        except Exception:
            pass

        self._discovered_cache = discovered
        return list(discovered.values())

    def _inspect_directory(self, dir_path: Path, slug: str) -> Optional[SisterDescriptor]:
        """Examines a candidate directory for manifest.json or chan metadata."""
        name = slug.replace("-", " ").title()
        tools: List[str] = []
        caps: List[str] = []
        version = "0.1.0"

        # Check for manifest.json
        manifest_file = dir_path / "manifest.json"
        if manifest_file.exists():
            try:
                data = json.loads(manifest_file.read_text(encoding="utf-8"))
                name = data.get("name", name)
                version = data.get("version", version)
            except Exception:
                pass

        return SisterDescriptor(
            name=name,
            slug=slug,
            version=version,
            root_path=dir_path,
            capabilities=caps,
            tools=tools,
        )

    def get(self, slug: str) -> Optional[SisterDescriptor]:
        """Resolves a specific sister by slug."""
        if slug in self._discovered_cache:
            return self._discovered_cache[slug]
        for s in self.discover_all():
            if s.slug == slug:
                return s
        return None

    def require(self, slug: str) -> SisterDescriptor:
        """Resolves a sister or raises SisterNotFoundError with remedy hints."""
        s = self.get(slug)
        if not s:
            raise SisterNotFoundError(slug)
        return s
