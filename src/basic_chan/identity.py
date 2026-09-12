"""basic_chan.identity — Persona definitions, anime/kanji metadata, and mascot banners."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_SILHOUETTE_MASCOT_ASCII = r"""
            /\_/\
           (     )
          /       \
         /  |   |  \
        (   |___|   )
         \         /
          \_______/
           /     \
          |   |   |
          |   |   |
          |   |   |
         (___|___)
"""

DEFAULT_DOT_MASCOT_ASCII = DEFAULT_SILHOUETTE_MASCOT_ASCII

DEFAULT_CHIBI_ASCII = r"""
          (o)   (o)
         (  ^ . ^  )
          /|  *  |\
          d| === |b
          (  | |  )
"""


@dataclass
class ChanIdentity:
    """Encapsulates the persona, mascot, and metadata of a -chan application."""

    name: str
    slug: str
    japanese_name: str = ""
    etymology: str = ""
    tagline: str = ""
    version: str = "0.1.0"
    author: str = "OpenClaw"
    prefix: str = ""
    theme_color: str = "cyan"
    ascii_art: str = DEFAULT_DOT_MASCOT_ASCII
    logo_path: Optional[Path | str] = None
    has_web_ui: bool = False
    entry_point: str = "cli:main"
    description: str = ""
    capabilities: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.prefix:
            self.prefix = self.slug.replace("-chan", "").replace("-", "_")

    def format_banner(self) -> str:
        """Format terminal ASCII banner string."""
        kanji_str = f" ({self.japanese_name})" if self.japanese_name else ""
        etym_str = f"\n[dim]{self.etymology}[/dim]" if self.etymology else ""
        return (
            f"[bold {self.theme_color}]{self.name}[/bold {self.theme_color}]"
            f"[magenta]{kanji_str}[/magenta] [dim]v{self.version}[/dim]{etym_str}\n"
            f"[italic white]\"{self.tagline}\"[/italic white]\n"
            f"{self.ascii_art}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert identity to JSON-compatible dictionary."""
        return {
            "name": self.name,
            "slug": self.slug,
            "japanese_name": self.japanese_name,
            "etymology": self.etymology,
            "tagline": self.tagline,
            "version": self.version,
            "author": self.author,
            "prefix": self.prefix,
            "theme_color": self.theme_color,
            "has_web_ui": self.has_web_ui,
            "description": self.description,
            "capabilities": self.capabilities,
        }
