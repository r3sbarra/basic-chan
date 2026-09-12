"""basic_chan.reporting.reporter — Multi-format reporting coordinator."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .html import generate_html_report
from .markdown import MarkdownReportBuilder
from .sarif import generate_sarif_report


class ChanReporter:
    """Coordinates writing reports in Markdown, HTML, JSON, and SARIF to dated subdirectories."""

    def __init__(self, chan_name: str, output_dir: Path | str, version: str = "0.1.0"):
        self.chan_name = chan_name
        self.output_dir = Path(output_dir).resolve()
        self.version = version

    def get_dated_dir(self, run_type: str = "general") -> Path:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        d = self.output_dir / today / run_type
        d.mkdir(parents=True, exist_ok=True)
        return d

    def export_report(
        self,
        title: str,
        summary: str,
        headers: List[str],
        rows: List[List[Any]],
        run_type: str = "audit",
        format_type: str = "markdown",
    ) -> Path:
        target_dir = self.get_dated_dir(run_type)

        if format_type.lower() == "html":
            content = generate_html_report(
                title=title,
                summary=summary,
                headers=headers,
                rows=rows,
                version=self.version,
            )
            out_file = target_dir / "report.html"
            out_file.write_text(content, encoding="utf-8")
            return out_file

        elif format_type.lower() == "json":
            payload = {
                "title": title,
                "summary": summary,
                "headers": headers,
                "rows": rows,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            out_file = target_dir / "report.json"
            out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return out_file

        else:  # markdown default
            builder = MarkdownReportBuilder(title)
            builder.add_paragraph(summary)
            if headers and rows:
                builder.add_table(headers, rows)
            out_file = target_dir / "report.md"
            out_file.write_text(builder.build(), encoding="utf-8")
            return out_file
