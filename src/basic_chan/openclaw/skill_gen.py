"""basic_chan.openclaw.skill_gen — OpenClaw agent SKILL.md generator."""

from __future__ import annotations

from typing import Any, Dict, List


def generate_skill_md(
    name: str,
    slug: str,
    description: str,
    tools: List[Dict[str, Any]],
) -> str:
    lines = [
        "---",
        f"name: {slug}",
        f"description: \"{description}\"",
        "---",
        "",
        f"# {name} (`{slug}`)",
        "",
        f"{description}",
        "",
        "## Available Tools",
        "",
    ]
    for t in tools:
        tname = t.get("name", "tool")
        tdesc = t.get("description", "")
        lines.append(f"- **`{tname}`**: {tdesc}")

    lines.append("")
    return "\n".join(lines)
