import math
from pathlib import Path
from basic_chan import ChanToolRegistry
from basic_chan.mcp.host import ChanMCPHost
from basic_chan.mcp.sanitizer import safe_json


def test_safe_json_sanitization():
    raw = {
        "nan_val": float("nan"),
        "inf_val": float("inf"),
        "path_val": Path("/tmp/test"),
        "set_val": {"a", "b"},
        "nested": {"valid": 123},
    }
    sanitized = safe_json(raw)
    assert sanitized["nan_val"] == "nan"
    assert sanitized["inf_val"] == "inf"
    assert sanitized["path_val"] == "/tmp/test"
    assert isinstance(sanitized["set_val"], list)
    assert sanitized["nested"]["valid"] == 123


def test_mcp_host_initialization():
    registry = ChanToolRegistry()

    @registry.register(name="ping", description="Ping test tool.")
    def ping() -> str:
        return "pong"

    host = ChanMCPHost(server_name="test-server", registry=registry)
    assert host.server_name == "test-server"
