"""basic_chan.reporting.markdown — GitHub Flavored Markdown report builder."""

from __future__ import annotations

from typing import Any, Dict, List


class MarkdownReportBuilder:
    """Constructs structured GitHub Flavored Markdown reports."""

    def __init__(self, title: str):
        self.title = title
        self._sections: List[str] = [f"# {title}\n"]

    def add_header(self, text: str, level: int = 2) -> MarkdownReportBuilder:
        hashes = "#" * level
        self._sections.append(f"\n{hashes} {text}\n")
        return self

    def add_paragraph(self, text: str) -> MarkdownReportBuilder:
        self._sections.append(f"\n{text}\n")
        return self

    def add_table(self, headers: List[str], rows: List[List[Any]]) -> MarkdownReportBuilder:
        hdr_line = "| " + " | ".join(headers) + " |"
        sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
        body_lines = ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
        self._sections.append("\n" + "\n".join([hdr_line, sep_line] + body_lines) + "\n")
        return self

    def add_code_block(self, code: str, lang: str = "") -> MarkdownReportBuilder:
        self._sections.append(f"\n```{lang}\n{code}\n```\n")
        return self

    def build(self) -> str:
        return "".join(self._sections)
