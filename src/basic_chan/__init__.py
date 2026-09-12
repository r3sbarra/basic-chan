"""basic_chan — Daemonless, agent-native foundational framework for the -chan ecosystem."""

from __future__ import annotations

from .base import BaseChan
from .exceptions import (
    ChanError,
    CoreImmunityViolationError,
    ScopeViolationError,
    SisterNotFoundError,
)
from .git_diff.baseline import BaselineManager
from .git_diff.diff_scanner import GitDiffScanner
from .git_diff.pragma import PragmaParser
from .identity import (
    DEFAULT_CHIBI_ASCII,
    DEFAULT_DOT_MASCOT_ASCII,
    DEFAULT_SILHOUETTE_MASCOT_ASCII,
    ChanIdentity,
)
from .intelligence.ai_gateway import AIGateway
from .intelligence.confusion import ConfusionTracker
from .intelligence.dag import WorkflowDAG
from .reporting.reporter import ChanReporter
from .safety.dry_run import DryRunGuard, is_dry_run, set_dry_run
from .safety.overrides import BehaviorOverrideRegistry
from .safety.scope_guard import ScopeGuard
from .safety.shield import CoreShield
from .sisters.descriptor import SisterDescriptor
from .sisters.resolver import DynamicSisterResolver
from .storage.vault import DaemonlessVault
from .tools.decorators import chan_tool
from .tools.registry import ChanToolRegistry
from .verification.falsci_contract import FalsciContract

__all__ = [
    "BaseChan",
    "ChanIdentity",
    "chan_tool",
    "ChanError",
    "ScopeViolationError",
    "CoreImmunityViolationError",
    "SisterNotFoundError",
    "ScopeGuard",
    "CoreShield",
    "BehaviorOverrideRegistry",
    "DryRunGuard",
    "set_dry_run",
    "is_dry_run",
    "DaemonlessVault",
    "DynamicSisterResolver",
    "SisterDescriptor",
    "ChanToolRegistry",
    "ChanReporter",
    "GitDiffScanner",
    "BaselineManager",
    "PragmaParser",
    "AIGateway",
    "ConfusionTracker",
    "WorkflowDAG",
    "FalsciContract",
    "DEFAULT_DOT_MASCOT_ASCII",
    "DEFAULT_SILHOUETTE_MASCOT_ASCII",
    "DEFAULT_CHIBI_ASCII",
]

__version__ = "0.1.0"
