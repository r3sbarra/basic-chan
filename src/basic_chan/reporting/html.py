"""basic_chan.reporting.html — Standalone offline interactive dark-glassmorphism HTML report generator."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #0d1117;
      --card-bg: rgba(22, 27, 34, 0.85);
      --border: rgba(56, 139, 253, 0.2);
      --accent: #58a6ff;
      --accent-magenta: #d2a8ff;
      --text: #c9d1d9;
      --text-muted: #8b949e;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 24px;
    }}
    .header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0;
      color: var(--accent);
      font-size: 24px;
    }}
    .card {{
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
    }}
    th, td {{
      padding: 10px 14px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      text-align: left;
    }}
    th {{
      color: var(--text-muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: bold;
      background: rgba(88, 166, 255, 0.15);
      color: var(--accent);
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{title}</h1>
    <span class="badge">basic-chan v{version}</span>
  </div>
  <div class="card">
    <h2>Summary</h2>
    <p>{summary}</p>
  </div>
  <div class="card">
    <h2>Details</h2>
    <table>
      <thead>
        <tr>{table_headers}</tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


def generate_html_report(
    title: str,
    summary: str,
    headers: List[str],
    rows: List[List[Any]],
    version: str = "0.1.0",
) -> str:
    """Renders a standalone, fully self-contained offline dark-glassmorphism HTML report."""
    th_html = "".join([f"<th>{h}</th>" for h in headers])
    tr_html_list = []
    for row in rows:
        cells = "".join([f"<td>{cell}</td>" for cell in row])
        tr_html_list.append(f"<tr>{cells}</tr>")
    tr_html = "\n".join(tr_html_list)

    return HTML_TEMPLATE.format(
        title=title,
        version=version,
        summary=summary,
        table_headers=th_html,
        table_rows=tr_html,
    )
