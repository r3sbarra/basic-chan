"""basic_chan.base — The foundational BaseChan abstract class."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from rich.console import Console

from .cli.formatter import print_banner
from .events.bus import ChanEventBus
from .git_diff.baseline import BaselineManager
from .git_diff.diff_scanner import GitDiffScanner
from .git_diff.pragma import PragmaParser
from .identity import ChanIdentity
from .intelligence.ai_gateway import AIGateway
from .intelligence.confusion import ConfusionTracker
from .intelligence.dag import WorkflowDAG
from .mcp.host import ChanMCPHost
from .openclaw.manifest_gen import generate_openclaw_manifest
from .openclaw.skill_gen import generate_skill_md
from .reporting.reporter import ChanReporter
from .safety.dry_run import DryRunGuard, is_dry_run
from .safety.overrides import BehaviorOverrideRegistry
from .safety.scope_guard import ScopeGuard
from .safety.shield import CoreShield
from .sisters.descriptor import SisterDescriptor
from .sisters.resolver import DynamicSisterResolver
from .snapshots.engine import SnapshotEngine
from .storage.vault import DaemonlessVault
from .tools.registry import ChanToolRegistry
from .verification.falsci_contract import FalsciContract


class BaseChan(ABC):
    """Abstract foundational base class for all -chan applications.
    
    Provides:
      - Persona identity & Rich ASCII mascot presentation
      - 100% Daemonless SQLite WAL memory vault & atomic leases
      - Safety boundaries (ScopeGuard, CoreShield immutability, DryRun)
      - Dynamic 4-tier sister discovery (zero static lists)
      - Dual in-process & native MCP server tool execution
      - AI gateway with multi-provider fallback
      - Kahn DAG workflow engine & failure confusion tracking
      - Diff-aware git inspection & baseline debt suppression
      - Multi-format reporting (Markdown, standalone offline HTML, JSON, SARIF)
      - Historical run snapshots (.chan_snapshots/)
      - OpenClaw manifest & skill synthesis
    """

    def __init__(
        self,
        identity: ChanIdentity,
        project_root: Optional[Path | str] = None,
        console: Optional[Console] = None,
    ):
        self.identity = identity
        self.root = Path(project_root).resolve() if project_root else Path.cwd()
        self.console = console or Console()
        self.logger = logging.getLogger(identity.slug)

        # Standard project layout directories
        self.data_dir = self.root / "data"
        self.reports_dir = self.root / "reports"
        self.assets_dir = self.root / "assets"
        self.snapshots_dir = self.root / ".chan_snapshots"

        for d in (self.data_dir, self.reports_dir, self.assets_dir, self.snapshots_dir):
            d.mkdir(parents=True, exist_ok=True)

        # Storage
        self.vault = DaemonlessVault(db_path=self.data_dir / "vault.db")

        # Safety & Isolation
        self.scope = ScopeGuard(allowed_roots=[self.root])
        self.shield = CoreShield(package_root=self.root)
        self.overrides = BehaviorOverrideRegistry()

        # Dynamic Sisters Discovery
        self.sisters = DynamicSisterResolver(current_slug=self.identity.slug)

        # Tools & MCP Host
        self.tools = ChanToolRegistry()
        self.mcp = ChanMCPHost(server_name=self.identity.slug, registry=self.tools)

        # Events & Signals
        self.events = ChanEventBus()

        # Intelligence & Workflows
        self.ai = AIGateway()
        self.confusion = ConfusionTracker()
        self.dag = WorkflowDAG()

        # Reporting & Snapshots
        self.reporter = ChanReporter(
            chan_name=self.identity.name,
            output_dir=self.reports_dir,
            version=self.identity.version,
        )
        self.snapshots = SnapshotEngine(storage_dir=self.snapshots_dir)

        # Register self into local daemonless IPC sister registry
        self._register_with_sisters_ipc()

        # Register standard base inspection tools
        self._register_builtin_tools()

        # Run subclass initialization
        self.initialize()

    def print_banner(self) -> None:
        """Render Rich ASCII mascot banner to console."""
        print_banner(
            console=self.console,
            identity_dict=self.identity.to_dict(),
            ascii_art=self.identity.ascii_art,
        )

    def sister(self, slug: str) -> Optional[SisterDescriptor]:
        """Resolves a sister chan by slug."""
        return self.sisters.get(slug)

    def has_sister(self, slug: str) -> bool:
        """Check if a sister chan exists in the environment."""
        return self.sisters.get(slug) is not None

    def execute_tool(self, tool_name: str, *args: Any, **kwargs: Any) -> Any:
        """Executes a registered tool in-process."""
        return self.tools.execute(tool_name, *args, **kwargs)

    def run_mcp_server(self) -> None:
        """Launches the standalone stdio MCP server."""
        self.mcp.run_stdio()

    def generate_manifest(self) -> Dict[str, Any]:
        """Generates OpenClaw AppManager manifest.json dictionary."""
        return generate_openclaw_manifest(
            name=self.identity.name,
            slug=self.identity.slug,
            version=self.identity.version,
            description=self.identity.description or self.identity.tagline,
            entry_point=self.identity.entry_point,
            has_web_ui=self.identity.has_web_ui,
        )

    def generate_skill_md(self) -> str:
        """Generates OpenClaw Agent SKILL.md specification."""
        tools_info = [
            {"name": s.name, "description": s.description}
            for s in self.tools.list_specs()
        ]
        return generate_skill_md(
            name=self.identity.name,
            slug=self.identity.slug,
            description=self.identity.tagline or self.identity.name,
            tools=tools_info,
        )

    def verify(self) -> Dict[str, Any]:
        """Self-audit contract verifying integrity, sisters, and falsci spec."""
        integrity_ok = self.shield.verify_integrity()
        sisters_count = len(self.sisters.discover_all())
        tools_count = len(self.tools)
        return {
            "status": "healthy",
            "shield_integrity": integrity_ok,
            "tools_count": tools_count,
            "sisters_count": sisters_count,
            "falsci_spec": FalsciContract.generate_health_spec(
                self.identity.slug, [s.name for s in self.tools.list_specs()]
            ),
        }

    def _register_with_sisters_ipc(self) -> None:
        try:
            desc = SisterDescriptor(
                name=self.identity.name,
                slug=self.identity.slug,
                version=self.identity.version,
                root_path=self.root,
                capabilities=self.identity.capabilities,
                tools=[s.name for s in self.tools.list_specs()],
                instance=self,
            )
            self.sisters.db.register_sister(desc)
        except Exception:
            pass

    def _register_builtin_tools(self) -> None:
        @self.tools.register(
            name=f"{self.identity.prefix}_status",
            description=f"Inspect operational status, health, and discovered sisters of {self.identity.name}.",
        )
        def chan_status() -> Dict[str, Any]:
            return {
                "name": self.identity.name,
                "slug": self.identity.slug,
                "version": self.identity.version,
                "tools_count": len(self.tools),
                "sisters": [s.slug for s in self.sisters.discover_all()],
            }

        @self.tools.register(
            name=f"{self.identity.prefix}_verify",
            description=f"Run formal integrity verification contract on {self.identity.name}.",
        )
        def chan_verify() -> Dict[str, Any]:
            return self.verify()

    @abstractmethod
    def initialize(self) -> None:
        """Subclass setup hook."""
        pass
