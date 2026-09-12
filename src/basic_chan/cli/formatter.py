"""basic_chan.cli.formatter — Rich console formatting, tables & panels."""

from __future__ import annotations

from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def print_banner(console: Console, identity_dict: Dict[str, Any], ascii_art: str) -> None:
    name = identity_dict.get("name", "Chan")
    kanji = identity_dict.get("japanese_name", "")
    version = identity_dict.get("version", "0.1.0")
    tagline = identity_dict.get("tagline", "")
    color = identity_dict.get("theme_color", "cyan")

    kanji_str = f" ({kanji})" if kanji else ""
    text = (
        f"[bold {color}]{name}[/bold {color}][magenta]{kanji_str}[/magenta] [dim]v{version}[/dim]\n"
        f"[italic white]\"{tagline}\"[/italic white]\n"
        f"{ascii_art}"
    )
    console.print(Panel(text, border_style=color, expand=False))


def render_table(console: Console, title: str, headers: List[str], rows: List[List[Any]], border_style: str = "cyan") -> None:
    table = Table(title=title, border_style=border_style)
    for h in headers:
        table.add_column(h, style="bold" if h == headers[0] else None)
    for r in rows:
        table.add_row(*[str(c) for c in r])
    console.print(table)
