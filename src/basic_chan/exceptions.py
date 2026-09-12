"""basic_chan.exceptions — Standardized exceptions and agent remediation protocol."""

from __future__ import annotations

from typing import Any, Dict, Optional


class ChanError(Exception):
    """Base exception for all chan ecosystem errors.
    
    Provides structured error responses specifically tailored for AI coding agents
    (Gemini, Claude, OpenClaw, Antigravity) with actionable remediation hints.
    """

    def __init__(
        self,
        message: str,
        error_type: Optional[str] = None,
        remedy_hint: Optional[str] = None,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type or self.__class__.__name__
        self.remedy_hint = remedy_hint or "Check input parameters and retry."
        self.retryable = retryable
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a standardized agent-diagnostic JSON dictionary."""
        return {
            "status": "error",
            "error_type": self.error_type,
            "message": self.message,
            "remedy_hint": self.remedy_hint,
            "retryable": self.retryable,
            "details": self.details,
        }


class ScopeViolationError(ChanError):
    """Raised when an operation violates target scope or filesystem confinement."""

    def __init__(self, message: str, target: str, remedy_hint: Optional[str] = None):
        super().__init__(
            message=message,
            error_type="ScopeViolationError",
            remedy_hint=remedy_hint or f"Authorize target '{target}' via scope allowlist or check path boundaries.",
            retryable=False,
            details={"target": target},
        )


class CoreImmunityViolationError(ChanError):
    """Raised when an autonomous process attempts to modify a protected core file."""

    def __init__(self, file_path: str):
        super().__init__(
            message=f"Modification of protected core kernel file '{file_path}' is strictly prohibited.",
            error_type="CoreImmunityViolationError",
            remedy_hint="Implement desired logic via BehaviorOverrideRegistry or safe plugins instead of patching core.",
            retryable=False,
            details={"protected_file": file_path},
        )


class SisterNotFoundError(ChanError):
    """Raised when a requested sister chan cannot be resolved."""

    def __init__(self, sister_name: str):
        super().__init__(
            message=f"Sister chan '{sister_name}' was not found in environment.",
            error_type="SisterNotFoundError",
            remedy_hint=f"Ensure sister repo '{sister_name}' exists in workspace or is installed as a Python package.",
            retryable=True,
            details={"sister_name": sister_name},
        )
