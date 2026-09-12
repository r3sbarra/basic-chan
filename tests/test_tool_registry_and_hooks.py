from basic_chan import ChanToolRegistry, chan_tool


def test_tool_registry_and_execution():
    registry = ChanToolRegistry()

    @registry.register(name="add_numbers", description="Adds two numbers.")
    def add(a: int, b: int) -> int:
        return a + b

    assert len(registry) == 1
    assert registry.execute("add_numbers", a=10, b=20) == 30

    # Compact schema for small LLMs
    compact = registry.to_compact_schemas()
    assert len(compact) == 1
    assert compact[0]["name"] == "add_numbers"
    assert "parameters" in compact[0]


def test_tool_interceptors():
    registry = ChanToolRegistry()
    events = []

    registry.interceptors.add_pre_hook(lambda name, kwargs: events.append(f"pre:{name}"))
    registry.interceptors.add_post_hook(lambda name, res, err, dur: events.append(f"post:{name}:{res}"))

    @registry.register(name="echo")
    def echo(msg: str) -> str:
        return msg.upper()

    res = registry.execute("echo", msg="hello")
    assert res == "HELLO"
    assert events == ["pre:echo", "post:echo:HELLO"]
