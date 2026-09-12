import pytest
from basic_chan import (
    BehaviorOverrideRegistry,
    CoreImmunityViolationError,
    CoreShield,
    DryRunGuard,
    ScopeGuard,
    ScopeViolationError,
    is_dry_run,
)


def test_scope_guard_paths(tmp_path):
    guard = ScopeGuard(allowed_roots=[tmp_path])

    safe_file = tmp_path / "safe.txt"
    safe_file.touch()
    assert guard.assert_path_allowed(safe_file) == safe_file

    unsafe_file = tmp_path.parent / "escape.txt"
    with pytest.raises(ScopeViolationError):
        guard.assert_path_allowed(unsafe_file)


def test_scope_guard_targets():
    guard = ScopeGuard(allowed_targets=["example.com", "*.internal.org"])
    assert guard.assert_target_allowed("https://example.com/api") == "https://example.com/api"
    assert guard.assert_target_allowed("sub.internal.org") == "sub.internal.org"

    with pytest.raises(ScopeViolationError):
        guard.assert_target_allowed("evil.com")


def test_core_shield(tmp_path):
    protected_sub = "core/kernel.py"
    target_file = tmp_path / protected_sub
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("PRISTINE = True")

    shield = CoreShield(package_root=tmp_path, protected_subpaths=[protected_sub])
    assert shield.verify_integrity() is True

    # Mutating raises error
    with pytest.raises(CoreImmunityViolationError):
        shield.assert_can_write(target_file)


def test_behavior_overrides():
    registry = BehaviorOverrideRegistry()
    registry.register_default("search", lambda q: f"default:{q}")

    # Default logic works
    assert registry.execute("search", "test") == "default:test"

    # Register override
    registry.register_override("search", lambda q: f"override:{q}")
    assert registry.execute("search", "test") == "override:test"

    # Crashing override triggers guaranteed fallback
    def failing_override(q):
        raise RuntimeError("crash!")

    registry.register_override("search", failing_override)
    assert registry.execute("search", "test") == "default:test"


def test_dry_run():
    assert is_dry_run() is False
    with DryRunGuard(True):
        assert is_dry_run() is True
    assert is_dry_run() is False
