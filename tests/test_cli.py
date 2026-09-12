from basic_chan import BaseChan, ChanIdentity
from basic_chan.cli.app import build_cli_parser


class DummyChan(BaseChan):
    def initialize(self) -> None:
        pass


def test_cli_parser():
    ident = ChanIdentity(name="Dummy-chan", slug="dummy-chan")
    chan = DummyChan(identity=ident)
    parser = build_cli_parser(chan)

    # Subcommands registered
    subactions = [action for action in parser._actions if action.dest == "command"]
    assert len(subactions) == 1
    choices = subactions[0].choices
    assert "status" in choices
    assert "sisters" in choices
    assert "tools" in choices
    assert "mcp" in choices
    assert "manifest" in choices
    assert "scaffold" in choices
